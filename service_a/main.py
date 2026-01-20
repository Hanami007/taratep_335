import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import grpc
from concurrent import futures
from typing import List
import sys
import os

# Import proto generated modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))
from proto import user_pb2, user_pb2_grpc

# FastAPI app
app = FastAPI(title="User Service", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
}


# ============= REST API Endpoints =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-service"}


@app.get("/users")
async def list_users():
    """Get all users"""
    return {"data": list(users_db.values())}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": users_db[user_id]}


@app.post("/users")
async def create_user(user: dict):
    """Create new user"""
    new_id = max(users_db.keys()) + 1 if users_db else 1
    users_db[new_id] = {"id": new_id, "name": user["name"], "email": user["email"]}
    return {"data": users_db[new_id], "message": "User created"}


# ============= gRPC Service =============

class UserServiceImpl(user_pb2_grpc.UserServiceServicer):
    """gRPC User Service Implementation"""

    def GetUser(self, request, context):
        """Get user by ID via gRPC"""
        logger.info(f"gRPC GetUser called with id={request.id}")
        if request.id in users_db:
            user = users_db[request.id]
            user_pb = user_pb2.User(id=user["id"], name=user["name"], email=user["email"])
            return user_pb2.UserResponse(code=200, message="Success", user=user_pb)
        else:
            return user_pb2.UserResponse(code=404, message="User not found", user=None)

    def ListUsers(self, request, context):
        """List all users via gRPC"""
        logger.info("gRPC ListUsers called")
        users_list = []
        for user in users_db.values():
            users_list.append(user_pb2.User(id=user["id"], name=user["name"], email=user["email"]))
        return user_pb2.UserList(users=users_list)


def serve_grpc():
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceImpl(), server)
    server.add_insecure_port('0.0.0.0:50051')
    logger.info("gRPC Server started on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    import threading
    import uvicorn

    # Start gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
