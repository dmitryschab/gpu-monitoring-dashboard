#!/usr/bin/env python3
"""
GPU-Z Log Uploader to S3
Uploads GPU-Z sensor logs to S3 in batches to optimize free tier usage

Features:
- Batch uploads every N minutes (default: 5)
- Compression to reduce storage costs
- Progress tracking to avoid re-uploading
- Free tier optimized (stays within 2000 PUT requests/month)

Usage:
    python upload_to_s3.py --bucket your-bucket-name --file "path/to/GPU-Z Sensor Log.txt"
"""

import argparse
import boto3
import gzip
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
DEFAULT_BATCH_INTERVAL = 5  # minutes
PROGRESS_FILE = ".upload_progress.json"


class GPULogUploader:
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize S3 uploader

        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region)
        self.progress_file = Path(PROGRESS_FILE)
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """Load upload progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load progress file: {e}")
        return {}

    def _save_progress(self):
        """Save upload progress to file"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _compress_file(self, file_path: Path) -> bytes:
        """Compress file with gzip"""
        with open(file_path, 'rb') as f:
            return gzip.compress(f.read(), compresslevel=9)

    def should_upload(self, file_path: Path, batch_interval: int) -> bool:
        """
        Check if file should be uploaded based on:
        - File modification time
        - Last upload time
        - Batch interval

        Args:
            file_path: Path to log file
            batch_interval: Minimum minutes between uploads

        Returns:
            True if should upload
        """
        file_key = str(file_path.absolute())
        current_hash = self._get_file_hash(file_path)

        # Check if file exists in progress
        if file_key in self.progress:
            last_upload = self.progress[file_key].get('last_upload', 0)
            last_hash = self.progress[file_key].get('hash', '')

            # Calculate time since last upload
            elapsed_minutes = (time.time() - last_upload) / 60

            # Upload if:
            # 1. File has changed (different hash)
            # 2. OR batch interval has passed
            if current_hash != last_hash:
                print(f"📝 File has changed since last upload")
                return True

            if elapsed_minutes >= batch_interval:
                print(f"⏰ Batch interval reached ({elapsed_minutes:.1f} min)")
                return True

            print(f"⏳ Waiting... ({batch_interval - elapsed_minutes:.1f} min until next upload)")
            return False

        # First time uploading this file
        print(f"🆕 New file detected")
        return True

    def upload_file(self, file_path: Path, compress: bool = True) -> Optional[str]:
        """
        Upload file to S3

        Args:
            file_path: Path to GPU-Z log file
            compress: Whether to compress before upload

        Returns:
            S3 key of uploaded file, or None if failed
        """
        try:
            # Generate S3 key
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = file_path.stem
            extension = '.txt.gz' if compress else '.txt'
            s3_key = f"logs/{timestamp}_{filename}{extension}"

            # Read and optionally compress
            if compress:
                print(f"🗜️  Compressing file...")
                file_data = self._compress_file(file_path)
                content_encoding = 'gzip'
            else:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                content_encoding = None

            original_size = file_path.stat().st_size
            upload_size = len(file_data)
            compression_ratio = (1 - upload_size / original_size) * 100

            print(f"📦 Size: {original_size:,} → {upload_size:,} bytes ({compression_ratio:.1f}% reduction)")

            # Upload to S3
            print(f"☁️  Uploading to s3://{self.bucket_name}/{s3_key}...")

            extra_args = {
                'ContentType': 'text/plain',
                'Metadata': {
                    'original_filename': file_path.name,
                    'upload_timestamp': timestamp,
                    'original_size': str(original_size),
                    'compressed_size': str(upload_size)
                }
            }

            if content_encoding:
                extra_args['ContentEncoding'] = content_encoding

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                **extra_args
            )

            # Update progress
            file_key = str(file_path.absolute())
            self.progress[file_key] = {
                'last_upload': time.time(),
                'hash': self._get_file_hash(file_path),
                's3_key': s3_key,
                'upload_count': self.progress.get(file_key, {}).get('upload_count', 0) + 1
            }
            self._save_progress()

            print(f"✅ Upload successful: {s3_key}")
            print(f"📊 Total uploads for this file: {self.progress[file_key]['upload_count']}")

            return s3_key

        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def estimate_monthly_usage(self, batch_interval: int):
        """
        Estimate monthly AWS usage based on batch interval

        Args:
            batch_interval: Upload interval in minutes
        """
        uploads_per_day = (24 * 60) / batch_interval
        uploads_per_month = uploads_per_day * 30

        print(f"\n📈 ESTIMATED MONTHLY USAGE")
        print(f"{'='*50}")
        print(f"Batch interval: {batch_interval} minutes")
        print(f"Uploads per day: {uploads_per_day:.0f}")
        print(f"Uploads per month: {uploads_per_month:.0f}")
        print(f"\n💰 FREE TIER LIMITS:")
        print(f"S3 PUT Requests: {uploads_per_month:.0f} / 2,000 free")

        if uploads_per_month > 2000:
            print(f"⚠️  WARNING: Exceeds free tier! Increase batch interval to {(24*60*30)/2000:.0f} minutes")
        else:
            print(f"✅ Within free tier ({uploads_per_month/2000*100:.1f}% usage)")

        print(f"{'='*50}\n")


def watch_and_upload(uploader: GPULogUploader, file_path: Path, batch_interval: int):
    """
    Continuously watch file and upload at intervals

    Args:
        uploader: GPULogUploader instance
        file_path: Path to GPU-Z log file
        batch_interval: Upload interval in minutes
    """
    print(f"👀 Watching file: {file_path}")
    print(f"⏰ Upload interval: {batch_interval} minutes")
    print(f"Press Ctrl+C to stop\n")

    try:
        while True:
            if uploader.should_upload(file_path, batch_interval):
                uploader.upload_file(file_path, compress=True)

            # Wait before next check (check every minute)
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")


def main():
    parser = argparse.ArgumentParser(
        description='Upload GPU-Z logs to S3 (free tier optimized)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload once
  python upload_to_s3.py --bucket gpu-monitoring-raw-logs-dev --file "data/GPU-Z Sensor Log.txt"

  # Continuous upload every 5 minutes
  python upload_to_s3.py --bucket gpu-monitoring-raw-logs-dev --file "data/GPU-Z Sensor Log.txt" --watch

  # Change batch interval to 10 minutes
  python upload_to_s3.py --bucket gpu-monitoring-raw-logs-dev --file "data/GPU-Z Sensor Log.txt" --watch --interval 10
        """
    )

    parser.add_argument('--bucket', '-b', required=True,
                       help='S3 bucket name')
    parser.add_argument('--file', '-f', required=True,
                       help='Path to GPU-Z Sensor Log file')
    parser.add_argument('--region', '-r', default='us-east-1',
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--watch', '-w', action='store_true',
                       help='Continuously watch and upload')
    parser.add_argument('--interval', '-i', type=int, default=DEFAULT_BATCH_INTERVAL,
                       help=f'Batch upload interval in minutes (default: {DEFAULT_BATCH_INTERVAL})')
    parser.add_argument('--no-compress', action='store_true',
                       help='Disable compression (not recommended)')
    parser.add_argument('--estimate', action='store_true',
                       help='Show monthly usage estimate and exit')

    args = parser.parse_args()

    # Initialize uploader
    uploader = GPULogUploader(args.bucket, args.region)

    # Show estimate if requested
    if args.estimate:
        uploader.estimate_monthly_usage(args.interval)
        return

    # Validate file path
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return

    print(f"🚀 GPU-Z Log Uploader")
    print(f"{'='*50}")
    print(f"Bucket: s3://{args.bucket}")
    print(f"File: {file_path}")
    print(f"Region: {args.region}")
    print(f"Compression: {'enabled' if not args.no_compress else 'disabled'}")
    print(f"{'='*50}\n")

    # Upload mode
    if args.watch:
        watch_and_upload(uploader, file_path, args.interval)
    else:
        # Single upload
        if uploader.should_upload(file_path, 0):  # 0 = always upload
            uploader.upload_file(file_path, compress=not args.no_compress)
        else:
            print("ℹ️  File already uploaded recently. Use --watch for continuous uploads.")


if __name__ == "__main__":
    main()
