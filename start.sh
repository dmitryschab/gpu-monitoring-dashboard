#!/bin/bash

# GPU Monitoring Dashboard Startup Script

set -e

echo "======================================"
echo "GPU Monitoring Dashboard Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Run this script from the project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found docker-compose.yml${NC}"

# Start services
echo ""
echo "Starting services..."
echo "This may take a few minutes on first run..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service status..."

services=("zookeeper" "kafka" "namenode" "datanode" "spark-master" "spark-worker" "influxdb" "grafana")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    echo ""
    echo -e "${YELLOW}Warning: Some services are not running. Check logs with:${NC}"
    echo "  docker-compose logs <service-name>"
    exit 1
fi

# Wait a bit more for Kafka to be fully ready
echo ""
echo "Waiting for Kafka to be fully ready..."
sleep 15

# Create Kafka topic
echo ""
echo "Creating Kafka topic 'gpu-metrics'..."
docker exec kafka kafka-topics --create --if-not-exists --topic gpu-metrics --bootstrap-server localhost:9093 --partitions 1 --replication-factor 1 2>/dev/null || true

echo -e "${GREEN}✓ Kafka topic created${NC}"

# Display access URLs
echo ""
echo "======================================"
echo "Services are ready!"
echo "======================================"
echo ""
echo "Access the following UIs:"
echo "  • Grafana:        http://localhost:3000 (admin/admin)"
echo "  • InfluxDB:       http://localhost:8086 (admin/adminpassword)"
echo "  • Spark Master:   http://localhost:8080"
echo "  • Hadoop HDFS:    http://localhost:9870"
echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Copy your GPU-Z log file to the data/ directory:"
echo "   cp 'GPU-Z Sensor Log.txt' ./data/"
echo ""
echo "2. Install Python dependencies:"
echo "   cd kafka-producer"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Start the Kafka producer (in a new terminal):"
echo "   cd kafka-producer"
echo "   python gpuz_producer.py --file '../data/GPU-Z Sensor Log.txt' --speed 1.0 --loop"
echo ""
echo "4. Start the InfluxDB consumer (in another terminal):"
echo "   cd kafka-producer"
echo "   python influxdb_consumer.py"
echo ""
echo "5. Open Grafana and create your dashboard:"
echo "   http://localhost:3000"
echo ""
echo "======================================"
echo "To stop all services:"
echo "  docker-compose down"
echo "======================================"
