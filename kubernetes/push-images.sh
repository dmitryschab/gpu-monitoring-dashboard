#!/bin/bash

# Push Docker images to registry
set -e

# Define image registry (change this to your registry)
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
VERSION="${VERSION:-latest}"

echo "Pushing images to ${REGISTRY}..."

docker push ${REGISTRY}/gpu-monitoring/kafka-producer:${VERSION}
docker push ${REGISTRY}/gpu-monitoring/influxdb-consumer:${VERSION}
docker push ${REGISTRY}/gpu-monitoring/batch-analytics:${VERSION}

echo "Images pushed successfully!"
