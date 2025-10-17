"""
GPU-Z Log Kafka Producer
Reads GPU-Z sensor logs and streams them to Kafka in real-time
"""

import json
import time
import csv
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUZProducer:
    def __init__(self, kafka_broker='localhost:9092', topic='gpu-metrics'):
        """Initialize Kafka producer"""
        self.topic = topic
        self.producer = None
        self.kafka_broker = kafka_broker
        self.connect_to_kafka()

    def connect_to_kafka(self):
        """Connect to Kafka broker with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.kafka_broker],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    compression_type='gzip',
                    acks='all',
                    retries=3
                )
                logger.info(f"Successfully connected to Kafka at {self.kafka_broker}")
                return
            except KafkaError as e:
                logger.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to Kafka.")
                    raise

    def parse_gpuz_line(self, line, headers):
        """Parse a single GPU-Z log line into structured data"""
        try:
            values = [v.strip() for v in line.split(',')]

            if len(values) != len(headers):
                logger.warning(f"Line has {len(values)} values but expected {len(headers)}")
                return None

            # Create metric dictionary
            metrics = {}
            for i, header in enumerate(headers):
                # Clean header name (remove units)
                clean_header = header.split('[')[0].strip()
                value = values[i].strip()

                # Try to convert to float if possible
                try:
                    if value and value != '':
                        metrics[clean_header] = float(value)
                    else:
                        metrics[clean_header] = None
                except ValueError:
                    # Keep as string if not a number (like dates)
                    metrics[clean_header] = value

            # Add timestamp
            if 'Date' in metrics:
                timestamp_str = metrics['Date']
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    metrics['timestamp'] = timestamp.isoformat()
                except ValueError:
                    metrics['timestamp'] = datetime.now().isoformat()
            else:
                metrics['timestamp'] = datetime.now().isoformat()

            return metrics

        except Exception as e:
            logger.error(f"Error parsing line: {e}")
            return None

    def send_metric(self, metric_data):
        """Send a metric to Kafka"""
        try:
            future = self.producer.send(self.topic, value=metric_data)
            # Block for 'synchronous' sends
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent metric to {record_metadata.topic} partition {record_metadata.partition}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def stream_from_file(self, file_path, replay_speed=1.0, loop=False):
        """
        Stream GPU-Z logs from file to Kafka

        Args:
            file_path: Path to GPU-Z log file
            replay_speed: Speed multiplier for replay (1.0 = real-time, 2.0 = 2x speed)
            loop: Whether to loop the file when it ends
        """
        logger.info(f"Starting to stream from {file_path}")
        logger.info(f"Replay speed: {replay_speed}x, Loop: {loop}")

        while True:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    # Read header line
                    header_line = f.readline().strip()
                    headers = [h.strip() for h in header_line.split(',')]
                    logger.info(f"Found {len(headers)} metrics in log file")

                    prev_timestamp = None
                    line_count = 0

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        # Parse line
                        metric_data = self.parse_gpuz_line(line, headers)

                        if metric_data:
                            # Calculate delay to simulate real-time streaming
                            if prev_timestamp and 'Date' in metric_data and metric_data['Date']:
                                try:
                                    current_ts = datetime.strptime(metric_data['Date'], '%Y-%m-%d %H:%M:%S')
                                    time_diff = (current_ts - prev_timestamp).total_seconds()

                                    if time_diff > 0:
                                        sleep_time = time_diff / replay_speed
                                        time.sleep(min(sleep_time, 5))  # Cap at 5 seconds

                                    prev_timestamp = current_ts
                                except ValueError:
                                    pass
                            elif 'Date' in metric_data and metric_data['Date']:
                                try:
                                    prev_timestamp = datetime.strptime(metric_data['Date'], '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    pass

                            # Send to Kafka
                            if self.send_metric(metric_data):
                                line_count += 1
                                if line_count % 10 == 0:
                                    logger.info(f"Sent {line_count} metrics to Kafka")

                    logger.info(f"Finished streaming {line_count} metrics from file")

                    if not loop:
                        break
                    else:
                        logger.info("Looping back to start of file...")
                        time.sleep(1)

            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                break
            except Exception as e:
                logger.error(f"Error streaming from file: {e}")
                break

    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer closed")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Stream GPU-Z logs to Kafka')
    parser.add_argument('--file', required=True, help='Path to GPU-Z log file')
    parser.add_argument('--broker', default='localhost:9092', help='Kafka broker address')
    parser.add_argument('--topic', default='gpu-metrics', help='Kafka topic name')
    parser.add_argument('--speed', type=float, default=1.0, help='Replay speed multiplier')
    parser.add_argument('--loop', action='store_true', help='Loop the file when it ends')

    args = parser.parse_args()

    producer = GPUZProducer(kafka_broker=args.broker, topic=args.topic)

    try:
        producer.stream_from_file(args.file, replay_speed=args.speed, loop=args.loop)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        producer.close()


if __name__ == '__main__':
    main()
