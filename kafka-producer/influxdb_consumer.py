"""
Kafka to InfluxDB Consumer
Consumes GPU metrics from Kafka and writes to InfluxDB for Grafana visualization
"""

import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfluxDBConsumer:
    def __init__(
        self,
        kafka_broker='localhost:9092',
        kafka_topic='gpu-metrics',
        influx_url='http://localhost:8086',
        influx_token='my-super-secret-auth-token',
        influx_org='gpu-monitoring',
        influx_bucket='gpu-metrics'
    ):
        """Initialize Kafka consumer and InfluxDB client"""
        self.kafka_broker = kafka_broker
        self.kafka_topic = kafka_topic
        self.influx_bucket = influx_bucket
        self.influx_org = influx_org

        # Initialize InfluxDB client
        self.influx_client = InfluxDBClient(
            url=influx_url,
            token=influx_token,
            org=influx_org
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)

        # Initialize Kafka consumer
        self.consumer = None
        self.connect_to_kafka()

    def connect_to_kafka(self):
        """Connect to Kafka with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.consumer = KafkaConsumer(
                    self.kafka_topic,
                    bootstrap_servers=[self.kafka_broker],
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id='influxdb-consumer-group',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                logger.info(f"Successfully connected to Kafka at {self.kafka_broker}")
                logger.info(f"Subscribed to topic: {self.kafka_topic}")
                return
            except KafkaError as e:
                logger.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to Kafka.")
                    raise

    def create_influx_point(self, metric_data):
        """Convert metric data to InfluxDB point"""
        try:
            # Parse timestamp
            timestamp_str = metric_data.get('timestamp', datetime.now().isoformat())
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()

            # Create point with measurement name
            point = Point("gpu_metrics").time(timestamp, WritePrecision.S)

            # Add GPU temperature fields
            if metric_data.get('GPU Temperature') is not None:
                point.field("gpu_temperature", float(metric_data['GPU Temperature']))

            if metric_data.get('Hot Spot') is not None:
                point.field("hot_spot_temperature", float(metric_data['Hot Spot']))

            if metric_data.get('Memory Temperature') is not None:
                point.field("memory_temperature", float(metric_data['Memory Temperature']))

            # Add CPU temperature
            if metric_data.get('CPU Temperature') is not None:
                point.field("cpu_temperature", float(metric_data['CPU Temperature']))

            # Add clock speeds
            if metric_data.get('GPU Clock') is not None:
                point.field("gpu_clock", float(metric_data['GPU Clock']))

            if metric_data.get('Memory Clock') is not None:
                point.field("memory_clock", float(metric_data['Memory Clock']))

            # Add load metrics
            if metric_data.get('GPU Load') is not None:
                point.field("gpu_load", float(metric_data['GPU Load']))

            if metric_data.get('Memory Controller Load') is not None:
                point.field("memory_controller_load", float(metric_data['Memory Controller Load']))

            # Add power metrics
            if metric_data.get('Board Power Draw') is not None:
                point.field("board_power_draw", float(metric_data['Board Power Draw']))

            if metric_data.get('GPU Chip Power Draw') is not None:
                point.field("gpu_chip_power_draw", float(metric_data['GPU Chip Power Draw']))

            if metric_data.get('Power Consumption (%)') is not None:
                point.field("power_consumption_percent", float(metric_data['Power Consumption (%)']))

            # Add memory usage
            if metric_data.get('Memory Used') is not None:
                point.field("gpu_memory_used", float(metric_data['Memory Used']))

            if metric_data.get('System Memory Used') is not None:
                point.field("system_memory_used", float(metric_data['System Memory Used']))

            # Add fan speeds
            if metric_data.get('Fan 1 Speed (%)') is not None:
                point.field("fan1_speed_percent", float(metric_data['Fan 1 Speed (%)']))

            if metric_data.get('Fan 2 Speed (%)') is not None:
                point.field("fan2_speed_percent", float(metric_data['Fan 2 Speed (%)']))

            # Add voltage
            if metric_data.get('GPU Voltage') is not None:
                point.field("gpu_voltage", float(metric_data['GPU Voltage']))

            return point

        except Exception as e:
            logger.error(f"Error creating InfluxDB point: {e}")
            return None

    def consume_and_write(self):
        """Consume from Kafka and write to InfluxDB"""
        logger.info("Starting to consume messages...")
        message_count = 0

        try:
            for message in self.consumer:
                try:
                    metric_data = message.value

                    # Create InfluxDB point
                    point = self.create_influx_point(metric_data)

                    if point:
                        # Write to InfluxDB
                        self.write_api.write(
                            bucket=self.influx_bucket,
                            org=self.influx_org,
                            record=point
                        )

                        message_count += 1

                        if message_count % 10 == 0:
                            logger.info(f"Written {message_count} metrics to InfluxDB")

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        finally:
            self.close()

    def close(self):
        """Close connections"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

        if self.influx_client:
            self.influx_client.close()
            logger.info("InfluxDB client closed")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Consume GPU metrics and write to InfluxDB')
    parser.add_argument('--kafka-broker', default='localhost:9092', help='Kafka broker address')
    parser.add_argument('--kafka-topic', default='gpu-metrics', help='Kafka topic name')
    parser.add_argument('--influx-url', default='http://localhost:8086', help='InfluxDB URL')
    parser.add_argument('--influx-token', default='my-super-secret-auth-token', help='InfluxDB token')
    parser.add_argument('--influx-org', default='gpu-monitoring', help='InfluxDB organization')
    parser.add_argument('--influx-bucket', default='gpu-metrics', help='InfluxDB bucket')

    args = parser.parse_args()

    consumer = InfluxDBConsumer(
        kafka_broker=args.kafka_broker,
        kafka_topic=args.kafka_topic,
        influx_url=args.influx_url,
        influx_token=args.influx_token,
        influx_org=args.influx_org,
        influx_bucket=args.influx_bucket
    )

    consumer.consume_and_write()


if __name__ == '__main__':
    main()
