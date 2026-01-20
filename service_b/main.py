import logging
from fastapi import FastAPI, HTTPException
import grpc
from concurrent import futures
import sys
import os

# Import proto generated modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))
from proto import product_pb2, product_pb2_grpc, user_pb2, user_pb2_grpc

# FastAPI app
app = FastAPI(title="Product Service", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database
products_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 30}
}

# Service A gRPC channel (for inter-service communication)
user_service_channel = None
user_service_stub = None


async def init_user_service_connection():
    """Initialize connection to User Service gRPC"""
    global user_service_channel, user_service_stub
    try:
        user_service_channel = await grpc.aio.insecure_channel('service_a:50051')
        user_service_stub = user_pb2_grpc.UserServiceStub(user_service_channel)
        logger.info("Connected to User Service gRPC")
    except Exception as e:
        logger.error(f"Failed to connect to User Service: {e}")


# ============= REST API Endpoints =============

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await init_user_service_connection()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product-service"}


@app.get("/products")
async def list_products():
    """Get all products"""
    return {"data": list(products_db.values())}


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product by ID"""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"data": products_db[product_id]}


@app.post("/products")
async def create_product(product: dict):
    """Create new product"""
    new_id = max(products_db.keys()) + 1 if products_db else 1
    products_db[new_id] = {
        "id": new_id,
        "name": product["name"],
        "price": product["price"],
        "stock": product["stock"]
    }
    return {"data": products_db[new_id], "message": "Product created"}


@app.get("/products-with-users")
async def get_products_with_users():
    """Get all products and fetch user info from User Service"""
    try:
        # Call User Service gRPC
        if user_service_stub:
            response = await user_service_stub.ListUsers(user_pb2.ListUsersRequest())
            users = [{"id": u.id, "name": u.name, "email": u.email} for u in response.users]
        else:
            users = []

        return {
            "products": list(products_db.values()),
            "users": users,
            "message": "Data from both services"
        }
    except Exception as e:
        logger.error(f"Error calling User Service: {e}")
        return {"products": list(products_db.values()), "error": str(e)}


# ============= gRPC Service =============

class ProductServiceImpl(product_pb2_grpc.ProductServiceServicer):
    """gRPC Product Service Implementation"""

    def GetProduct(self, request, context):
        """Get product by ID via gRPC"""
        logger.info(f"gRPC GetProduct called with id={request.id}")
        if request.id in products_db:
            product = products_db[request.id]
            product_pb = product_pb2.Product(
                id=product["id"],
                name=product["name"],
                price=product["price"],
                stock=product["stock"]
            )
            return product_pb2.ProductResponse(code=200, message="Success", product=product_pb)
        else:
            return product_pb2.ProductResponse(code=404, message="Product not found", product=None)

    def ListProducts(self, request, context):
        """List all products via gRPC"""
        logger.info("gRPC ListProducts called")
        products_list = []
        for product in products_db.values():
            products_list.append(product_pb2.Product(
                id=product["id"],
                name=product["name"],
                price=product["price"],
                stock=product["stock"]
            ))
        return product_pb2.ProductList(products=products_list)


def serve_grpc():
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductServiceImpl(), server)
    server.add_insecure_port('0.0.0.0:50052')
    logger.info("gRPC Server started on port 50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    import threading
    import uvicorn

    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
