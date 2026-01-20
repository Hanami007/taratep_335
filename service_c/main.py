import logging
from fastapi import FastAPI, HTTPException
import grpc
from concurrent import futures
import sys
import os

# Import proto generated modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))
from proto import order_pb2, order_pb2_grpc, user_pb2, user_pb2_grpc, product_pb2, product_pb2_grpc

# FastAPI app
app = FastAPI(title="Order Service", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database
orders_db = {
    1: {"id": 1, "user_id": 1, "product_id": 1, "quantity": 2, "total_price": 1999.98},
    2: {"id": 2, "user_id": 2, "product_id": 2, "quantity": 5, "total_price": 149.95}
}

# gRPC channels
user_service_channel = None
user_service_stub = None
product_service_channel = None
product_service_stub = None


async def init_service_connections():
    """Initialize connections to other services"""
    global user_service_channel, user_service_stub
    global product_service_channel, product_service_stub
    
    try:
        # Connect to User Service
        user_service_channel = await grpc.aio.insecure_channel('service_a:50051')
        user_service_stub = user_pb2_grpc.UserServiceStub(user_service_channel)
        logger.info("Connected to User Service gRPC")
        
        # Connect to Product Service
        product_service_channel = await grpc.aio.insecure_channel('service_b:50052')
        product_service_stub = product_pb2_grpc.ProductServiceStub(product_service_channel)
        logger.info("Connected to Product Service gRPC")
    except Exception as e:
        logger.error(f"Failed to connect to services: {e}")


# ============= REST API Endpoints =============

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await init_service_connections()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-service"}


@app.get("/orders")
async def list_orders():
    """Get all orders"""
    return {"data": list(orders_db.values())}


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order by ID"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"data": orders_db[order_id]}


@app.post("/orders")
async def create_order(order: dict):
    """Create new order with validation from User and Product services"""
    try:
        user_id = order["user_id"]
        product_id = order["product_id"]
        quantity = order["quantity"]

        # Validate user exists (via gRPC)
        if user_service_stub:
            user_response = await user_service_stub.GetUser(user_pb2.GetUserRequest(id=user_id))
            if user_response.code != 200:
                raise HTTPException(status_code=404, detail="User not found")

        # Validate product exists and has stock (via gRPC)
        if product_service_stub:
            product_response = await product_service_stub.GetProduct(product_pb2.GetProductRequest(id=product_id))
            if product_response.code != 200:
                raise HTTPException(status_code=404, detail="Product not found")
            if product_response.product.stock < quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")

        # Create order
        new_id = max(orders_db.keys()) + 1 if orders_db else 1
        total_price = product_response.product.price * quantity
        orders_db[new_id] = {
            "id": new_id,
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price
        }
        
        return {
            "data": orders_db[new_id],
            "message": "Order created successfully",
            "user": {"id": user_id},
            "product": {"id": product_id, "price": product_response.product.price}
        }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders-detail")
async def get_orders_detail():
    """Get all orders with detailed user and product information"""
    try:
        result = []
        
        for order in orders_db.values():
            order_detail = order.copy()
            
            # Get user info
            if user_service_stub:
                user_resp = await user_service_stub.GetUser(user_pb2.GetUserRequest(id=order["user_id"]))
                if user_resp.code == 200:
                    order_detail["user"] = {
                        "id": user_resp.user.id,
                        "name": user_resp.user.name,
                        "email": user_resp.user.email
                    }
            
            # Get product info
            if product_service_stub:
                product_resp = await product_service_stub.GetProduct(product_pb2.GetProductRequest(id=order["product_id"]))
                if product_resp.code == 200:
                    order_detail["product"] = {
                        "id": product_resp.product.id,
                        "name": product_resp.product.name,
                        "price": product_resp.product.price,
                        "stock": product_resp.product.stock
                    }
            
            result.append(order_detail)
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error fetching orders detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= gRPC Service =============

class OrderServiceImpl(order_pb2_grpc.OrderServiceServicer):
    """gRPC Order Service Implementation"""

    def CreateOrder(self, request, context):
        """Create order via gRPC"""
        logger.info(f"gRPC CreateOrder called with user_id={request.user_id}, product_id={request.product_id}")
        
        try:
            new_id = max(orders_db.keys()) + 1 if orders_db else 1
            total_price = 0.0
            
            orders_db[new_id] = {
                "id": new_id,
                "user_id": request.user_id,
                "product_id": request.product_id,
                "quantity": request.quantity,
                "total_price": total_price
            }
            
            order_pb = order_pb2.Order(
                id=new_id,
                user_id=request.user_id,
                product_id=request.product_id,
                quantity=request.quantity,
                total_price=total_price
            )
            return order_pb2.OrderResponse(code=201, message="Order created", order=order_pb)
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return order_pb2.OrderResponse(code=500, message=str(e), order=None)

    def ListOrders(self, request, context):
        """List all orders via gRPC"""
        logger.info("gRPC ListOrders called")
        orders_list = []
        for order in orders_db.values():
            orders_list.append(order_pb2.Order(
                id=order["id"],
                user_id=order["user_id"],
                product_id=order["product_id"],
                quantity=order["quantity"],
                total_price=order["total_price"]
            ))
        return order_pb2.OrderList(orders=orders_list)


def serve_grpc():
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceImpl(), server)
    server.add_insecure_port('0.0.0.0:50053')
    logger.info("gRPC Server started on port 50053")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    import threading
    import uvicorn

    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
