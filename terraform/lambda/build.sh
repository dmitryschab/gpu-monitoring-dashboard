#!/bin/bash
# Build Lambda deployment package

echo "Building Lambda deployment package..."

# Create temp directory
mkdir -p package
cd package || exit

# Install dependencies
pip install -r ../requirements.txt --target .

# Add Lambda function
cp ../processor.py .

# Create zip file
zip -r ../gpu_processor.zip .

# Cleanup
cd ..
rm -rf package

echo "✅ Lambda package created: gpu_processor.zip"
ls -lh gpu_processor.zip
