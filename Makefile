.PHONY: help build up down logs stop restart clean test

help:
	@echo "FastAPI Microservices with gRPC"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make build           - Build all services"
	@echo "  make up              - Start all services"
	@echo "  make up-d            - Start services in detached mode"
	@echo "  make down            - Stop and remove services"
	@echo "  make stop            - Stop services without removing"
	@echo "  make restart         - Restart services"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-a          - View logs from service_a"
	@echo "  make logs-b          - View logs from service_b"
	@echo "  make logs-c          - View logs from service_c"
	@echo "  make clean           - Remove all containers and images"
	@echo "  make test            - Run tests"
	@echo "  make ps              - Show running containers"
	@echo "  make bash-a          - Open bash in service_a"
	@echo "  make bash-b          - Open bash in service_b"
	@echo "  make bash-c          - Open bash in service_c"

build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

stop:
	docker-compose stop

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-a:
	docker-compose logs -f service_a

logs-b:
	docker-compose logs -f service_b

logs-c:
	docker-compose logs -f service_c

ps:
	docker-compose ps

clean:
	docker-compose down -v
	docker system prune -f

bash-a:
	docker exec -it service_a bash

bash-b:
	docker exec -it service_b bash

bash-c:
	docker exec -it service_c bash

test-health:
	@echo "Testing Service A (User Service)..."
	curl http://localhost:8001/health
	@echo "\n\nTesting Service B (Product Service)..."
	curl http://localhost:8002/health
	@echo "\n\nTesting Service C (Order Service)..."
	curl http://localhost:8003/health

test-users:
	curl http://localhost:8001/users | python -m json.tool

test-products:
	curl http://localhost:8002/products | python -m json.tool

test-orders:
	curl http://localhost:8003/orders | python -m json.tool
