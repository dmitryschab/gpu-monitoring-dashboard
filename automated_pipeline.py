#!/usr/bin/env python3
"""
Automated GPU Monitoring Pipeline
- Monitors GPU-Z log file
- Uploads when size threshold reached
- Processes through AWS Lambda
- Loads into InfluxDB
- Cleans up raw data
- Creates daily aggregates

Run continuously as a background service
"""

import os
import time
import boto3
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import hashlib
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables with defaults
GPU_Z_LOG_PATH = os.getenv('GPU_Z_LOG_PATH', r"C:\Users\dmitr\Documents\projects\GPU-Z Sensor Log.txt")
PROCESSED_DIR = os.getenv('PROCESSED_DIR', r"./processed_logs")
SIZE_THRESHOLD_MB = int(os.getenv('GPU_Z_SIZE_THRESHOLD_MB', '5'))
CHECK_INTERVAL_SECONDS = int(os.getenv('GPU_Z_CHECK_INTERVAL_SEC', '60'))

# AWS Configuration
S3_BUCKET_RAW = os.getenv('S3_BUCKET_RAW', 'gpu-monitoring-raw-logs-dev')
S3_BUCKET_PROCESSED = os.getenv('S3_BUCKET_PROCESSED', 'gpu-monitoring-processed-logs-dev')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# InfluxDB Configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')  # No default - must be provided
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'gpu-monitoring')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'gpu-metrics')
INFLUXDB_BUCKET_DAILY = os.getenv('INFLUXDB_BUCKET_DAILY', 'gpu-metrics-daily')

# Validate required environment variables
if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is required. Please set it in .env file.")

# State file to track processed files
STATE_FILE = Path("pipeline_state.json")


class GPUMonitoringPipeline:
    def __init__(self):
        self.s3 = boto3.client('s3', region_name=AWS_REGION)
        self.influx_client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.state = self.load_state()

        # Ensure processed directory exists
        os.makedirs(PROCESSED_DIR, exist_ok=True)

        # Ensure daily bucket exists
        self.ensure_daily_bucket()

    def load_state(self):
        """Load pipeline state"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            'last_processed': None,
            'last_file_hash': None,
            'processed_files': []
        }

    def save_state(self):
        """Save pipeline state"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_file_size_mb(self, path):
        """Get file size in MB"""
        return os.path.getsize(path) / (1024 * 1024)

    def get_file_hash(self, path):
        """Calculate MD5 hash of file"""
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def should_process(self):
        """Check if file should be processed"""
        if not os.path.exists(GPU_Z_LOG_PATH):
            return False, "File doesn't exist"

        size_mb = self.get_file_size_mb(GPU_Z_LOG_PATH)
        current_hash = self.get_file_hash(GPU_Z_LOG_PATH)

        # Check if file has changed
        if current_hash == self.state.get('last_file_hash'):
            return False, f"File unchanged (hash: {current_hash[:8]})"

        # Check size threshold
        if size_mb < SIZE_THRESHOLD_MB:
            return False, f"File too small ({size_mb:.1f} MB < {SIZE_THRESHOLD_MB} MB)"

        return True, f"Ready to process ({size_mb:.1f} MB, new hash)"

    def upload_to_s3(self):
        """Upload GPU-Z log to S3"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"logs/{timestamp}_GPU-Z_Sensor_Log.txt"

        print(f"[UPLOAD] Uploading to S3: {s3_key}")

        # Compress before upload to save bandwidth
        with open(GPU_Z_LOG_PATH, 'rb') as f_in:
            compressed = gzip.compress(f_in.read())

        self.s3.put_object(
            Bucket=S3_BUCKET_RAW,
            Key=s3_key + '.gz',
            Body=compressed,
            ContentType='text/plain',
            ContentEncoding='gzip',
            Metadata={
                'upload_timestamp': timestamp,
                'original_size': str(os.path.getsize(GPU_Z_LOG_PATH))
            }
        )

        print(f"[OK] Uploaded: {len(compressed) / (1024*1024):.2f} MB compressed")
        return s3_key + '.gz'

    def wait_for_lambda_processing(self, s3_key, timeout=60):
        """Wait for Lambda to process the file"""
        print(f"[WAIT] Waiting for Lambda to process...")

        # Expected processed file name
        base_name = os.path.basename(s3_key).replace('.txt.gz', '').replace('.txt', '')

        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if processed file exists
            try:
                response = self.s3.list_objects_v2(
                    Bucket=S3_BUCKET_PROCESSED,
                    Prefix='processed/'
                )

                if 'Contents' in response:
                    for obj in response['Contents']:
                        if base_name in obj['Key']:
                            print(f"[OK] Lambda processed: {obj['Key']}")
                            return obj['Key']
            except Exception as e:
                print(f"[WARN] Error checking processed files: {e}")

            time.sleep(2)

        print(f"[WARN] Timeout waiting for Lambda processing")
        return None

    def download_processed_data(self, s3_key):
        """Download processed JSON from S3"""
        local_path = os.path.join(PROCESSED_DIR, os.path.basename(s3_key))

        print(f"[DOWNLOAD] Downloading processed data...")
        self.s3.download_file(S3_BUCKET_PROCESSED, s3_key, local_path)

        # Decompress if gzipped
        if local_path.endswith('.gz'):
            with gzip.open(local_path, 'rb') as f:
                data = json.load(f)
            os.remove(local_path)  # Remove compressed file
        else:
            with open(local_path, 'r') as f:
                data = json.load(f)

        print(f"[OK] Downloaded {len(data)} records")
        return data

    def load_to_influxdb(self, records):
        """Load records into InfluxDB"""
        print(f"[INFLUX] Loading {len(records)} records to InfluxDB...")

        points = []
        for record in records:
            if not record.get('Date'):
                continue

            try:
                timestamp = datetime.strptime(record['Date'], "%Y-%m-%d %H:%M:%S")
                point = Point("gpu_metrics").time(timestamp)

                # Add all numeric fields
                for key, value in record.items():
                    if key == 'Date' or key == '':
                        continue

                    if value is not None and isinstance(value, (int, float)):
                        field_name = key.replace(' ', '_').replace('(', '').replace(')', '').replace('#', '').replace('%', 'pct').lower()
                        point = point.field(field_name, float(value))

                points.append(point)
            except Exception as e:
                continue

        # Write in batches
        batch_size = 1000
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.write_api.write(bucket=INFLUXDB_BUCKET, record=batch)

        print(f"[OK] Loaded {len(points)} points to InfluxDB")
        return len(points)

    def create_daily_aggregates(self, date_str=None):
        """Create daily aggregates for analysis"""
        if date_str is None:
            # Aggregate yesterday's data
            date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"[AGGREGATE] Creating daily aggregates for {date_str}...")

        query_api = self.influx_client.query_api()

        # Aggregate query - calculate daily statistics
        aggregate_query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: {date_str}T00:00:00Z, stop: {date_str}T23:59:59Z)
          |> filter(fn: (r) => r._measurement == "gpu_metrics")
          |> filter(fn: (r) =>
              r._field == "gpu_temperature" or
              r._field == "cpu_temperature" or
              r._field == "gpu_load" or
              r._field == "board_power_draw" or
              r._field == "gpu_clock" or
              r._field == "memory_used"
          )
          |> aggregateWindow(every: 1h, fn: mean)
        '''

        try:
            tables = query_api.query(aggregate_query)

            # Write aggregates to daily bucket
            points = []
            for table in tables:
                for record in table.records:
                    point = Point("gpu_metrics_daily") \
                        .time(record.get_time()) \
                        .tag("date", date_str) \
                        .field(record.get_field(), record.get_value())
                    points.append(point)

            if points:
                self.write_api.write(bucket=INFLUXDB_BUCKET_DAILY, record=points)
                print(f"[OK] Created {len(points)} daily aggregate points")

        except Exception as e:
            print(f"[WARN] Error creating aggregates: {e}")

    def detect_scenario(self, records):
        """Detect if session is idle or gaming based on GPU load"""
        if not records:
            return "unknown"

        # Calculate average GPU load
        loads = [r.get('GPU Load', 0) for r in records if r.get('GPU Load')]
        if not loads:
            return "unknown"

        avg_load = sum(loads) / len(loads)

        # Threshold: >30% average load = gaming, <30% = idle
        return "gaming" if avg_load > 30 else "idle"

    def tag_session_data(self, records, scenario):
        """Add scenario tag to records"""
        print(f"[TAG] Tagging session as: {scenario}")

        points = []
        for record in records:
            if not record.get('Date'):
                continue

            try:
                timestamp = datetime.strptime(record['Date'], "%Y-%m-%d %H:%M:%S")

                # Create a point with scenario tag
                point = Point("gpu_sessions") \
                    .time(timestamp) \
                    .tag("scenario", scenario)

                # Add key metrics
                for field in ['GPU Load', 'GPU Temperature', 'Board Power Draw', 'GPU Clock']:
                    if field in record and record[field] is not None:
                        field_name = field.replace(' ', '_').lower()
                        point = point.field(field_name, float(record[field]))

                points.append(point)
            except:
                continue

        if points:
            self.write_api.write(bucket=INFLUXDB_BUCKET, record=points)
            print(f"[OK] Tagged {len(points)} points as {scenario}")

    def cleanup_s3_raw_data(self, s3_key):
        """Delete raw data from S3 after processing"""
        print(f"[CLEANUP] Cleaning up raw S3 data: {s3_key}")
        try:
            self.s3.delete_object(Bucket=S3_BUCKET_RAW, Key=s3_key)
            print(f"[OK] Deleted from S3")
        except Exception as e:
            print(f"[WARN] Error deleting: {e}")

    def cleanup_local_file(self):
        """Delete local GPU-Z log to save space"""
        print(f"[CLEANUP] Deleting local GPU-Z log file to save space")

        # Delete the file completely (data already in S3 and InfluxDB)
        if os.path.exists(GPU_Z_LOG_PATH):
            os.remove(GPU_Z_LOG_PATH)
            print(f"[OK] Local file deleted (data preserved in S3 and InfluxDB)")

        # Create empty file for GPU-Z to continue logging
        with open(GPU_Z_LOG_PATH, 'w') as f:
            f.write("")
        print(f"[OK] New empty log file created for GPU-Z")

    def ensure_daily_bucket(self):
        """Ensure daily aggregates bucket exists"""
        try:
            buckets_api = self.influx_client.buckets_api()
            existing = buckets_api.find_bucket_by_name(INFLUXDB_BUCKET_DAILY)
            if not existing:
                print(f"Creating daily bucket: {INFLUXDB_BUCKET_DAILY}")
                buckets_api.create_bucket(bucket_name=INFLUXDB_BUCKET_DAILY, org=INFLUXDB_ORG)
        except:
            pass  # Bucket might already exist

    def process_file(self):
        """Main processing pipeline"""
        print(f"\n{'='*60}")
        print(f"[START] Starting pipeline: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        try:
            # Step 1: Upload to S3
            s3_key = self.upload_to_s3()

            # Step 2: Wait for Lambda processing
            processed_key = self.wait_for_lambda_processing(s3_key, timeout=120)

            if not processed_key:
                print("[ERROR] Lambda processing failed or timed out")
                return False

            # Step 3: Download processed data
            records = self.download_processed_data(processed_key)

            # Step 4: Detect scenario (idle vs gaming)
            scenario = self.detect_scenario(records)

            # Step 5: Load to InfluxDB with regular data
            self.load_to_influxdb(records)

            # Step 6: Tag session data with scenario
            self.tag_session_data(records, scenario)

            # Step 7: Create daily aggregates (for previous day)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            self.create_daily_aggregates(yesterday)

            # Step 8: Cleanup S3 raw data
            self.cleanup_s3_raw_data(s3_key)

            # Step 9: Archive and clear local file
            self.cleanup_local_file()

            # Update state
            self.state['last_processed'] = datetime.now().isoformat()
            self.state['last_file_hash'] = self.get_file_hash(GPU_Z_LOG_PATH)
            self.state['processed_files'].append({
                'timestamp': datetime.now().isoformat(),
                's3_key': s3_key,
                'records': len(records),
                'scenario': scenario
            })
            self.save_state()

            print(f"\n{'='*60}")
            print(f"[SUCCESS] Pipeline completed successfully!")
            print(f"   Records processed: {len(records)}")
            print(f"   Scenario: {scenario}")
            print(f"   S3 raw data cleaned up")
            print(f"   Local file archived and cleared")
            print(f"{'='*60}\n")

            return True

        except Exception as e:
            print(f"\n[ERROR] Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_forever(self):
        """Run pipeline continuously"""
        print(f"[MONITOR] Starting GPU Monitoring Pipeline")
        print(f"   GPU-Z Log: {GPU_Z_LOG_PATH}")
        print(f"   Size threshold: {SIZE_THRESHOLD_MB} MB")
        print(f"   Check interval: {CHECK_INTERVAL_SECONDS} seconds")
        print(f"   Press Ctrl+C to stop\n")

        while True:
            try:
                should_process, reason = self.should_process()

                if should_process:
                    print(f"[TRIGGER] Processing triggered: {reason}")
                    self.process_file()
                else:
                    print(f"[WAIT] {datetime.now().strftime('%H:%M:%S')} - {reason}")

                time.sleep(CHECK_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                print(f"\n\n[STOP] Stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Error in main loop: {e}")
                time.sleep(CHECK_INTERVAL_SECONDS)


def main():
    pipeline = GPUMonitoringPipeline()
    pipeline.run_forever()


if __name__ == "__main__":
    main()
