FROM python:3.10-slim

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy proto files
COPY service_b/proto/ /tmp/proto/

# Generate Python code from proto
RUN python -m grpc_tools.protoc \
    -I/tmp/proto \
    --python_out=/tmp/proto \
    --grpc_python_out=/tmp/proto \
    /tmp/proto/product.proto \
    /tmp/proto/user.proto

# Copy service files
COPY service_b/main.py .
COPY service_b/requirements.txt .

# Copy generated proto files to service
RUN mkdir -p proto && cp /tmp/proto/*_pb2*.py proto/ && touch proto/__init__.py

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002 50052

CMD ["python", "main.py"]
