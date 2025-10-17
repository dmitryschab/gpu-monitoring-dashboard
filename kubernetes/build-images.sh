#!/bin/bash

# Build Docker images for Kubernetes deployment
set -e

echo "Building Docker images for GPU Monitoring Dashboard..."

# Define image registry (change this to your registry)
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
VERSION="${VERSION:-latest}"

# Build Kafka Producer image
echo "Building kafka-producer image..."
docker build -f docker/Dockerfile.kafka-producer -t ${REGISTRY}/gpu-monitoring/kafka-producer:${VERSION} .

# Build InfluxDB Consumer image
echo "Building influxdb-consumer image..."
docker build -f docker/Dockerfile.influxdb-consumer -t ${REGISTRY}/gpu-monitoring/influxdb-consumer:${VERSION} .

# Build Batch Analytics image
echo "Building batch-analytics image..."
docker build -f docker/Dockerfile.batch-analytics -t ${REGISTRY}/gpu-monitoring/batch-analytics:${VERSION} .

echo ""
echo "Images built successfully!"
echo ""
echo "To push to registry:"
echo "  docker push ${REGISTRY}/gpu-monitoring/kafka-producer:${VERSION}"
echo "  docker push ${REGISTRY}/gpu-monitoring/influxdb-consumer:${VERSION}"
echo "  docker push ${REGISTRY}/gpu-monitoring/batch-analytics:${VERSION}"
echo ""
echo "Or run: ./kubernetes/push-images.sh"
