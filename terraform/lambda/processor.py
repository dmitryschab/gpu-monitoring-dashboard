"""
GPU-Z Log Processor Lambda Function
Parses GPU-Z sensor logs from S3 and forwards to Kafka

Author: GPU Monitoring Dashboard
Free Tier Optimized: Uses minimal memory and execution time
"""

import json
import os
import csv
import boto3
import gzip
from datetime import datetime
from io import StringIO
from typing import Dict, List, Optional
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# AWS clients
s3_client = boto3.client('s3')

# Optional Kafka integration (requires kafka-python in layer or package)
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("kafka-python not available. Install for Kafka integration.")


def parse_gpu_log_line(headers: List[str], values: List[str]) -> Optional[Dict]:
    """
    Parse a single GPU-Z log line into a structured dictionary

    Args:
        headers: Column headers from CSV
        values: Values for this row

    Returns:
        Dictionary with parsed metrics or None if invalid
    """
    if len(values) != len(headers):
        return None

    record = {}

    for i, header in enumerate(headers):
        value = values[i].strip()

        # Clean up header name
        clean_header = header.split('[')[0].strip()

        # Parse numeric values
        try:
            if value and value != '':
                # Try to convert to float
                record[clean_header] = float(value)
            else:
                record[clean_header] = None
        except ValueError:
            # Keep as string if not numeric
            record[clean_header] = value

    return record


def process_gpu_log(bucket: str, key: str) -> Dict:
    """
    Process GPU-Z log file from S3

    Args:
        bucket: S3 bucket name
        key: S3 object key

    Returns:
        Processing results dictionary
    """
    logger.info(f"Processing file: s3://{bucket}/{key}")

    # Download file from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    raw_data = response['Body'].read()

    # Decompress if gzipped
    if key.endswith('.gz'):
        logger.info("Decompressing gzipped file")
        raw_data = gzip.decompress(raw_data)

    # Try multiple encodings to handle special characters like degree symbol
    try:
        content = raw_data.decode('utf-8')
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode failed, trying latin-1")
        content = raw_data.decode('latin-1')

    # Parse CSV
    csv_reader = csv.reader(StringIO(content))

    # Read header
    headers = next(csv_reader)
    headers = [h.strip() for h in headers]

    # Process records
    records = []
    skipped = 0

    for row in csv_reader:
        if not row or all(not cell for cell in row):
            skipped += 1
            continue

        parsed = parse_gpu_log_line(headers, row)
        if parsed:
            records.append(parsed)
        else:
            skipped += 1

    logger.info(f"Parsed {len(records)} records, skipped {skipped}")

    return {
        'total_records': len(records),
        'skipped': skipped,
        'records': records,
        'headers': headers
    }


def send_to_kafka(records: List[Dict], kafka_endpoint: str, topic: str) -> int:
    """
    Send parsed records to Kafka

    Args:
        records: List of parsed GPU metrics
        kafka_endpoint: Kafka broker address
        topic: Kafka topic name

    Returns:
        Number of records sent successfully
    """
    if not KAFKA_AVAILABLE:
        logger.warning("Kafka not available, skipping send")
        return 0

    if not kafka_endpoint:
        logger.warning("No Kafka endpoint configured, skipping send")
        return 0

    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_endpoint],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip',  # Reduce bandwidth
            acks=1,  # Wait for leader acknowledgment
            retries=3
        )

        sent = 0
        for record in records:
            try:
                future = producer.send(topic, value=record)
                future.get(timeout=10)  # Wait for confirmation
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send record: {e}")

        producer.flush()
        producer.close()

        logger.info(f"Sent {sent}/{len(records)} records to Kafka")
        return sent

    except Exception as e:
        logger.error(f"Kafka error: {e}")
        return 0


def save_processed_data(records: List[Dict], processed_bucket: str, original_key: str) -> str:
    """
    Save processed data to S3 as compressed JSON

    Args:
        records: Parsed records
        processed_bucket: Destination S3 bucket
        original_key: Original file key (for naming)

    Returns:
        S3 key of saved file
    """
    # Generate output key
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = os.path.basename(original_key).replace('.txt', '')
    output_key = f"processed/{timestamp}_{filename}.json.gz"

    # Compress data
    json_data = json.dumps(records, indent=2)
    compressed_data = gzip.compress(json_data.encode('utf-8'))

    # Upload to S3
    s3_client.put_object(
        Bucket=processed_bucket,
        Key=output_key,
        Body=compressed_data,
        ContentType='application/json',
        ContentEncoding='gzip',
        Metadata={
            'original_file': original_key,
            'record_count': str(len(records)),
            'processed_at': timestamp
        }
    )

    logger.info(f"Saved processed data to s3://{processed_bucket}/{output_key}")
    logger.info(f"Compression: {len(json_data)} -> {len(compressed_data)} bytes ({len(compressed_data)/len(json_data)*100:.1f}%)")

    return output_key


def lambda_handler(event, context):
    """
    Lambda handler function triggered by S3 events

    Args:
        event: S3 event notification
        context: Lambda context

    Returns:
        Response dictionary
    """
    logger.info("Lambda function started")
    logger.info(f"Event: {json.dumps(event)}")

    # Get environment variables
    processed_bucket = os.environ.get('PROCESSED_BUCKET', '')
    kafka_endpoint = os.environ.get('KAFKA_ENDPOINT', '')
    kafka_topic = os.environ.get('KAFKA_TOPIC', 'gpu-metrics')

    results = []

    try:
        # Process each S3 record in the event
        for record in event.get('Records', []):
            # Extract S3 info
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # Process the log file
            result = process_gpu_log(bucket, key)

            # Send to Kafka (if configured)
            kafka_sent = 0
            if kafka_endpoint:
                kafka_sent = send_to_kafka(
                    result['records'],
                    kafka_endpoint,
                    kafka_topic
                )

            # Save processed data to S3
            output_key = save_processed_data(
                result['records'],
                processed_bucket,
                key
            )

            results.append({
                'source_file': f"s3://{bucket}/{key}",
                'processed_file': f"s3://{processed_bucket}/{output_key}",
                'records_parsed': result['total_records'],
                'records_skipped': result['skipped'],
                'kafka_sent': kafka_sent,
                'status': 'success'
            })

    except Exception as e:
        logger.error(f"Error processing: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'status': 'failed'
            })
        }

    # Return success response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Processing completed successfully',
            'results': results,
            'total_files': len(results)
        })
    }

    logger.info(f"Lambda function completed: {json.dumps(results)}")
    return response


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'Records': [{
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'test-log.txt'}
            }
        }]
    }

    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
