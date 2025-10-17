#!/bin/bash

# GPU Monitoring Dashboard Management Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_help() {
    echo "GPU Monitoring Dashboard - Management Script"
    echo ""
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start           - Start all services"
    echo "  stop            - Stop all services"
    echo "  restart         - Restart all services"
    echo "  status          - Show service status"
    echo "  logs [service]  - Show logs (optional: specify service)"
    echo "  clean           - Stop and remove all data (WARNING: deletes everything)"
    echo "  producer        - Start Kafka producer"
    echo "  consumer        - Start InfluxDB consumer"
    echo "  spark-stream    - Start Spark streaming job"
    echo "  spark-batch     - Run batch analytics"
    echo "  topic-create    - Create Kafka topic"
    echo "  topic-list      - List Kafka topics"
    echo "  hdfs-ls         - List HDFS files"
    echo "  hdfs-ui         - Open HDFS web UI"
    echo "  grafana-ui      - Open Grafana UI"
    echo "  influx-ui       - Open InfluxDB UI"
    echo "  spark-ui        - Open Spark UI"
    echo "  help            - Show this help"
    echo ""
}

function start_services() {
    echo -e "${BLUE}Starting services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Services started${NC}"
    echo ""
    echo "Waiting for services to be ready..."
    sleep 15
    create_kafka_topic
    show_access_urls
}

function stop_services() {
    echo -e "${BLUE}Stopping services...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Services stopped${NC}"
}

function restart_services() {
    stop_services
    echo ""
    start_services
}

function show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose ps
}

function show_logs() {
    if [ -z "$1" ]; then
        docker-compose logs --tail=50 -f
    else
        docker-compose logs --tail=50 -f "$1"
    fi
}

function clean_all() {
    echo -e "${RED}WARNING: This will delete all data and volumes!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo -e "${BLUE}Cleaning up...${NC}"
        docker-compose down -v
        echo -e "${GREEN}✓ All data cleaned${NC}"
    else
        echo "Cancelled."
    fi
}

function start_producer() {
    echo -e "${BLUE}Starting Kafka producer...${NC}"
    cd kafka-producer
    python gpuz_producer.py --file "../data/GPU-Z Sensor Log.txt" --speed 1.0 --loop
}

function start_consumer() {
    echo -e "${BLUE}Starting InfluxDB consumer...${NC}"
    cd kafka-producer
    python influxdb_consumer.py
}

function start_spark_streaming() {
    echo -e "${BLUE}Starting Spark streaming job...${NC}"
    docker exec -it spark-master bash -c "cd /opt/spark-jobs && pip install -q -r requirements.txt && spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 streaming_processor.py"
}

function run_spark_batch() {
    echo -e "${BLUE}Running Spark batch analytics...${NC}"
    docker exec -it spark-master bash -c "cd /opt/spark-jobs && pip install -q -r requirements.txt && spark-submit batch_analytics.py"
}

function create_kafka_topic() {
    echo -e "${BLUE}Creating Kafka topic...${NC}"
    docker exec kafka kafka-topics --create --if-not-exists --topic gpu-metrics --bootstrap-server localhost:9093 --partitions 1 --replication-factor 1 2>/dev/null || true
    echo -e "${GREEN}✓ Kafka topic ready${NC}"
}

function list_kafka_topics() {
    echo -e "${BLUE}Kafka topics:${NC}"
    docker exec kafka kafka-topics --list --bootstrap-server localhost:9093
}

function list_hdfs() {
    echo -e "${BLUE}HDFS contents:${NC}"
    docker exec namenode hdfs dfs -ls -R /
}

function open_hdfs_ui() {
    echo -e "${BLUE}Opening HDFS UI...${NC}"
    xdg-open http://localhost:9870 2>/dev/null || open http://localhost:9870 2>/dev/null || start http://localhost:9870 2>/dev/null || echo "Open http://localhost:9870 in your browser"
}

function open_grafana_ui() {
    echo -e "${BLUE}Opening Grafana UI...${NC}"
    xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || start http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in your browser"
}

function open_influx_ui() {
    echo -e "${BLUE}Opening InfluxDB UI...${NC}"
    xdg-open http://localhost:8086 2>/dev/null || open http://localhost:8086 2>/dev/null || start http://localhost:8086 2>/dev/null || echo "Open http://localhost:8086 in your browser"
}

function open_spark_ui() {
    echo -e "${BLUE}Opening Spark UI...${NC}"
    xdg-open http://localhost:8080 2>/dev/null || open http://localhost:8080 2>/dev/null || start http://localhost:8080 2>/dev/null || echo "Open http://localhost:8080 in your browser"
}

function show_access_urls() {
    echo ""
    echo -e "${GREEN}======================================"
    echo "Services are ready!"
    echo "======================================${NC}"
    echo ""
    echo "Access UIs:"
    echo "  • Grafana:      http://localhost:3000"
    echo "  • InfluxDB:     http://localhost:8086"
    echo "  • Spark:        http://localhost:8080"
    echo "  • Hadoop HDFS:  http://localhost:9870"
    echo ""
}

# Main script
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    clean)
        clean_all
        ;;
    producer)
        start_producer
        ;;
    consumer)
        start_consumer
        ;;
    spark-stream)
        start_spark_streaming
        ;;
    spark-batch)
        run_spark_batch
        ;;
    topic-create)
        create_kafka_topic
        ;;
    topic-list)
        list_kafka_topics
        ;;
    hdfs-ls)
        list_hdfs
        ;;
    hdfs-ui)
        open_hdfs_ui
        ;;
    grafana-ui)
        open_grafana_ui
        ;;
    influx-ui)
        open_influx_ui
        ;;
    spark-ui)
        open_spark_ui
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
