#!/usr/bin/env python3
"""
Load GPU-Z processed data from S3 into InfluxDB 2.x
Connects AWS Lambda output → InfluxDB → Grafana
"""

import json
import gzip
import boto3
import os
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configuration from environment variables
S3_BUCKET = os.getenv('S3_BUCKET_PROCESSED', 'gpu-monitoring-processed-logs-dev')
S3_PREFIX = "processed/"
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'gpu-monitoring')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'gpu-metrics')

if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is required")

def download_from_s3(bucket, key):
    """Download and decompress file from S3"""
    print(f"Downloading s3://{bucket}/{key}...")
    s3 = boto3.client('s3', region_name=AWS_REGION)
    response = s3.get_object(Bucket=bucket, Key=key)

    # Decompress if gzipped
    if key.endswith('.gz'):
        data = gzip.decompress(response['Body'].read())
    else:
        data = response['Body'].read()

    return json.loads(data.decode('utf-8'))

def parse_timestamp(date_str):
    """Parse GPU-Z timestamp to datetime"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except:
        return datetime.now()

def transform_to_influx_v2(records):
    """Transform JSON records to InfluxDB 2.x format"""
    points = []

    for record in records:
        if not record.get('Date'):
            continue

        timestamp = parse_timestamp(record['Date'])

        # Create point
        point = Point("gpu_metrics").time(timestamp)

        # Add all numeric fields
        for key, value in record.items():
            if key == 'Date' or key == '':
                continue

            if value is not None and isinstance(value, (int, float)):
                # Clean field name
                field_name = key.replace(' ', '_').replace('(', '').replace(')', '').replace('#', '').replace('%', 'pct').lower()
                point = point.field(field_name, float(value))

        points.append(point)

    return points

def write_to_influxdb(points):
    """Write points to InfluxDB 2.x"""
    print(f"Connecting to InfluxDB at {INFLUXDB_URL}...")

    client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Write points in batches
    batch_size = 1000
    total = len(points)

    print(f"Writing {total} points to InfluxDB bucket '{INFLUXDB_BUCKET}'...")
    for i in range(0, total, batch_size):
        batch = points[i:i+batch_size]
        try:
            write_api.write(bucket=INFLUXDB_BUCKET, record=batch)
            print(f"  Progress: {min(i+batch_size, total)}/{total} ({min(i+batch_size, total)/total*100:.1f}%)")
        except Exception as e:
            print(f"  Error writing batch: {e}")

    print(f"Successfully wrote {total} points to InfluxDB!")
    client.close()

def list_s3_files():
    """List all processed files in S3"""
    s3 = boto3.client('s3', region_name=AWS_REGION)
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)

    if 'Contents' not in response:
        return []

    files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json.gz') or obj['Key'].endswith('.json')]
    return files

def main():
    print("=" * 60)
    print("GPU Monitoring - S3 to InfluxDB 2.x Loader")
    print("=" * 60)
    print()

    # List available files
    print("Finding processed files in S3...")
    files = list_s3_files()

    if not files:
        print("No processed files found in S3!")
        print(f"Bucket: {S3_BUCKET}")
        print(f"Prefix: {S3_PREFIX}")
        return

    print(f"Found {len(files)} file(s):")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")

    # Process each file
    total_records = 0

    for file_key in files:
        print(f"\nProcessing: {file_key}")

        # Download and parse
        records = download_from_s3(S3_BUCKET, file_key)
        print(f"  Loaded {len(records)} records")

        # Transform to InfluxDB format
        points = transform_to_influx_v2(records)
        print(f"  Transformed {len(points)} points")

        # Write to InfluxDB
        write_to_influxdb(points)

        total_records += len(points)

    print()
    print("=" * 60)
    print(f"COMPLETE! Loaded {total_records} total records into InfluxDB")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open Grafana: http://localhost:3000")
    print("2. Go to Explore")
    print("3. Select InfluxDB datasource")
    print(f"4. Query bucket: {INFLUXDB_BUCKET}")
    print("5. Measurement: gpu_metrics")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
