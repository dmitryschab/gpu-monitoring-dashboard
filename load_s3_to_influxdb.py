#!/usr/bin/env python3
"""
Load GPU-Z processed data from S3 into InfluxDB
Connects AWS Lambda output → InfluxDB → Grafana
"""

import json
import gzip
import boto3
from datetime import datetime
from influxdb import InfluxDBClient
import sys

# Configuration
S3_BUCKET = "gpu-monitoring-processed-logs-dev"
S3_PREFIX = "processed/"
AWS_REGION = "us-east-1"

INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DB = "gpu_monitoring"

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
    """Parse GPU-Z timestamp to Unix timestamp"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp() * 1_000_000_000)  # nanoseconds
    except:
        return int(datetime.now().timestamp() * 1_000_000_000)

def transform_to_influx(records):
    """Transform JSON records to InfluxDB format"""
    points = []

    for record in records:
        if not record.get('Date'):
            continue

        timestamp = parse_timestamp(record['Date'])

        # Build InfluxDB point
        point = {
            "measurement": "gpu_metrics",
            "time": timestamp,
            "fields": {}
        }

        # Add all numeric fields
        for key, value in record.items():
            if key == 'Date' or key == '':
                continue

            if value is not None and isinstance(value, (int, float)):
                # Clean field name
                field_name = key.replace(' ', '_').replace('(', '').replace(')', '').replace('#', '').replace('%', 'pct').lower()
                point["fields"][field_name] = float(value)

        if point["fields"]:  # Only add if we have data
            points.append(point)

    return points

def write_to_influxdb(points):
    """Write points to InfluxDB"""
    print(f"Connecting to InfluxDB at {INFLUXDB_HOST}:{INFLUXDB_PORT}...")

    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        database=INFLUXDB_DB
    )

    # Create database if it doesn't exist
    databases = client.get_list_database()
    if {'name': INFLUXDB_DB} not in databases:
        print(f"Creating database: {INFLUXDB_DB}")
        client.create_database(INFLUXDB_DB)

    # Write points in batches
    batch_size = 1000
    total = len(points)

    print(f"Writing {total} points to InfluxDB...")
    for i in range(0, total, batch_size):
        batch = points[i:i+batch_size]
        client.write_points(batch, time_precision='n')
        print(f"  Progress: {min(i+batch_size, total)}/{total} ({min(i+batch_size, total)/total*100:.1f}%)")

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
    print("GPU Monitoring - S3 to InfluxDB Loader")
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
        points = transform_to_influx(records)
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
    print("4. Query: SELECT * FROM gpu_metrics")
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
