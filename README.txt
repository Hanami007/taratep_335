================================================================================
  FastAPI Microservices with gRPC & Docker Compose
================================================================================

PROJECT OVERVIEW
================================================================================
This project demonstrates a complete microservices architecture with 3 FastAPI 
services that communicate using both RESTful APIs and gRPC. All services are 
containerized and orchestrated using Docker Compose.

PROJECT STRUCTURE
================================================================================
testMin_S/
├── service_a/                  # User Service (gRPC Server)
│   ├── proto/
│   │   └── user.proto         # User service proto definitions
│   ├── main.py                # FastAPI + gRPC implementation
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Container configuration
│
├── service_b/                  # Product Service (gRPC Server)
│   ├── proto/
│   │   ├── product.proto      # Product service proto definitions
│   │   └── user.proto         # User proto for gRPC client calls
│   ├── main.py                # FastAPI + gRPC implementation
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Container configuration
│
├── service_c/                  # Order Service (gRPC Server & Client)
│   ├── proto/
│   │   ├── order.proto        # Order service proto definitions
│   │   ├── user.proto         # User proto for gRPC client calls
│   │   └── product.proto      # Product proto for gRPC client calls
│   ├── main.py                # FastAPI + gRPC implementation
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile             # Container configuration
│
├── docker-compose.yml         # Docker Compose orchestration
└── README.txt                 # This file


SERVICE DESCRIPTIONS
================================================================================

SERVICE_A (User Service) - Port 8001 (REST), 50051 (gRPC)
---------
Features:
  - Manages user data
  - Provides REST API endpoints
  - Exposes gRPC UserService
  
REST Endpoints:
  GET    /health              - Health check
  GET    /users               - List all users
  GET    /users/{user_id}    - Get user by ID
  POST   /users               - Create new user

gRPC Services:
  - GetUser(GetUserRequest) -> UserResponse
  - ListUsers(ListUsersRequest) -> UserList


SERVICE_B (Product Service) - Port 8002 (REST), 50052 (gRPC)
---------
Features:
  - Manages product catalog
  - Provides REST API endpoints
  - Exposes gRPC ProductService
  - Calls Service_A via gRPC to get user information

REST Endpoints:
  GET    /health                        - Health check
  GET    /products                      - List all products
  GET    /products/{product_id}        - Get product by ID
  POST   /products                      - Create new product
  GET    /products-with-users          - Get products & users from Service_A

gRPC Services:
  - GetProduct(GetProductRequest) -> ProductResponse
  - ListProducts(ListProductsRequest) -> ProductList


SERVICE_C (Order Service) - Port 8003 (REST), 50053 (gRPC)
---------
Features:
  - Manages orders
  - Provides REST API endpoints
  - Exposes gRPC OrderService
  - Calls Service_A (User) and Service_B (Product) via gRPC
  - Validates user and product existence before creating orders

REST Endpoints:
  GET    /health                  - Health check
  GET    /orders                  - List all orders
  GET    /orders/{order_id}      - Get order by ID
  POST   /orders                  - Create new order
  GET    /orders-detail          - Get orders with user & product details

gRPC Services:
  - CreateOrder(CreateOrderRequest) -> OrderResponse
  - ListOrders(ListOrdersRequest) -> OrderList


INTER-SERVICE COMMUNICATION
================================================================================

Communication Methods:
  1. REST API: HTTP calls between services (optional in current setup)
  2. gRPC: Binary protocol using Protocol Buffers for efficiency

Service Dependencies:
  Service_B depends on Service_A (calls gRPC UserService)
  Service_C depends on Service_A and Service_B (calls both gRPC services)


TECHNOLOGY STACK
================================================================================
- FastAPI: Modern web framework for building APIs
- gRPC: High-performance RPC framework
- Protocol Buffers: Serialization format for gRPC
- Docker: Container platform
- Docker Compose: Container orchestration
- Python 3.10: Programming language


PREREQUISITES
================================================================================
- Docker Desktop (version 20.10+)
- Docker Compose (version 1.29+)


INSTALLATION & SETUP
================================================================================

1. Clone or download the project

2. Build and start the services using Docker Compose:
   
   cd testMin_S
   docker-compose up --build

   Or in detached mode:
   docker-compose up -d --build

3. Verify services are running:
   
   docker-compose ps

4. View logs:
   
   docker-compose logs -f service_a
   docker-compose logs -f service_b
   docker-compose logs -f service_c


TESTING THE SERVICES
================================================================================

Once services are running, you can test them using curl or Postman:

SERVICE_A (User Service):
  
  Health Check:
  curl http://localhost:8001/health

  List Users:
  curl http://localhost:8001/users

  Get Specific User:
  curl http://localhost:8001/users/1

  Create User:
  curl -X POST http://localhost:8001/users \
    -H "Content-Type: application/json" \
    -d '{"name":"John Doe","email":"john@example.com"}'


SERVICE_B (Product Service):
  
  Health Check:
  curl http://localhost:8002/health

  List Products:
  curl http://localhost:8002/products

  Get Specific Product:
  curl http://localhost:8002/products/1

  Get Products with User Data:
  curl http://localhost:8002/products-with-users

  Create Product:
  curl -X POST http://localhost:8002/products \
    -H "Content-Type: application/json" \
    -d '{"name":"Monitor","price":299.99,"stock":15}'


SERVICE_C (Order Service):
  
  Health Check:
  curl http://localhost:8003/health

  List Orders:
  curl http://localhost:8003/orders

  Get Specific Order:
  curl http://localhost:8003/orders/1

  Create Order (validates user & product):
  curl -X POST http://localhost:8003/orders \
    -H "Content-Type: application/json" \
    -d '{"user_id":1,"product_id":1,"quantity":2}'

  Get Orders with Detail:
  curl http://localhost:8003/orders-detail


gRPC TESTING (using grpcurl)
================================================================================

Install grpcurl:
  go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

Test Service_A (gRPC):
  
  List users:
  grpcurl -plaintext localhost:50051 user.UserService/ListUsers

  Get user:
  grpcurl -plaintext -d '{"id":1}' localhost:50051 user.UserService/GetUser


Test Service_B (gRPC):
  
  List products:
  grpcurl -plaintext localhost:50052 product.ProductService/ListProducts

  Get product:
  grpcurl -plaintext -d '{"id":1}' localhost:50052 product.ProductService/GetProduct


Test Service_C (gRPC):
  
  List orders:
  grpcurl -plaintext localhost:50053 order.OrderService/ListOrders

  Create order:
  grpcurl -plaintext -d '{"user_id":1,"product_id":1,"quantity":2}' \
    localhost:50053 order.OrderService/CreateOrder


STOPPING SERVICES
================================================================================

Stop running services:
  docker-compose stop

Stop and remove containers:
  docker-compose down

Stop and remove all data (including volumes):
  docker-compose down -v


SCALING & PRODUCTION CONSIDERATIONS
================================================================================

1. Load Balancing:
   - Consider using Kubernetes instead of Docker Compose for production
   - Implement NGINX as a reverse proxy in front of services

2. Database:
   - Add persistent data stores (PostgreSQL, MongoDB)
   - Implement database migrations

3. Monitoring:
   - Add Prometheus for metrics collection
   - Add Grafana for visualization
   - Implement ELK stack for logging

4. Security:
   - Use TLS/SSL for gRPC communication
   - Implement authentication and authorization
   - Use API keys or OAuth2

5. Service Mesh:
   - Consider Istio for advanced traffic management
   - Add distributed tracing with Jaeger

6. CI/CD:
   - Set up GitHub Actions or GitLab CI
   - Implement automated testing and deployment


TROUBLESHOOTING
================================================================================

1. Container fails to start:
   - Check logs: docker-compose logs service_name
   - Verify Docker resources are available

2. Services can't communicate:
   - Ensure they're on the same network (defined in docker-compose.yml)
   - Check service names in connection strings (should match service names)

3. Proto file compilation errors:
   - Rebuild containers: docker-compose up --build
   - Ensure protobuf-compiler is installed in Dockerfile

4. Port conflicts:
   - Check if ports are already in use: netstat -an
   - Modify ports in docker-compose.yml


EXAMPLE WORKFLOW
================================================================================

1. Create a user via Service_A:
   POST http://localhost:8001/users
   {"name":"Alice","email":"alice@example.com"}

2. Create a product via Service_B:
   POST http://localhost:8002/products
   {"name":"Laptop","price":999.99,"stock":10}

3. Create an order via Service_C:
   POST http://localhost:8003/orders
   {"user_id":1,"product_id":1,"quantity":2}

4. Get order details which will fetch user and product info:
   GET http://localhost:8003/orders-detail


DEVELOPMENT NOTES
================================================================================

Proto File Organization:
  - Each service has its own proto files
  - Services that call other services include their proto files
  - Proto files are compiled to Python code during Docker build

Code Generation:
  - Protocol Buffer files (.proto) are compiled to Python files
  - Generated files are placed in proto/ directory
  - Generated files are added to gitignore (not committed to version control)

Async Support:
  - FastAPI endpoints are async for better performance
  - gRPC uses threading for concurrent requests
  - Both can handle high concurrency


USEFUL COMMANDS
================================================================================

View all running containers:
  docker ps

View container logs:
  docker logs -f service_a

Execute command in container:
  docker exec -it service_a bash

Rebuild specific service:
  docker-compose up -d --build service_a

Remove all unused Docker resources:
  docker system prune

Push images to registry:
  docker tag service_a:latest myregistry/service_a:latest
  docker push myregistry/service_a:latest


FURTHER IMPROVEMENTS
================================================================================

1. Add API documentation with Swagger/OpenAPI
2. Implement comprehensive error handling
3. Add validation middleware
4. Implement rate limiting
5. Add caching strategies
6. Implement circuit breakers for resilience
7. Add health check endpoints with detailed status
8. Implement structured logging
9. Add distributed tracing
10. Implement API versioning


CONTACT & SUPPORT
================================================================================

For issues or questions, please refer to the service logs or documentation.


LICENSE
================================================================================

This project is provided as-is for educational and demonstration purposes.


VERSION HISTORY
================================================================================

v1.0 - Initial release
  - 3 FastAPI microservices
  - gRPC inter-service communication
  - Docker Compose orchestration
  - RESTful API endpoints
