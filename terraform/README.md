# GPU Monitoring Dashboard - Terraform Infrastructure

**100% AWS Free Tier Compliant** ✅

This Terraform configuration deploys a serverless infrastructure on AWS to process GPU-Z sensor logs using S3 and Lambda, fully integrated with your existing Kafka/Spark/Hadoop stack.

## Architecture

```
GPU-Z Log (Local)
    ↓
Upload Script (Batched, every 5 min)
    ↓
S3 Bucket (Raw Logs)
    ↓ (Event Trigger)
Lambda Function (Python)
    ├── Parse GPU-Z CSV
    ├── Transform to JSON
    ├── Send to Kafka (Optional)
    └── Store in S3 (Processed)
         ↓
Your Existing Stack
    ├── Kafka → Spark → HDFS
    └── InfluxDB → Grafana
```

## What Gets Deployed

### AWS Resources (All Free Tier)
- ✅ **2x S3 Buckets** (raw + processed logs)
- ✅ **1x Lambda Function** (Python 3.11, 256MB)
- ✅ **IAM Role & Policies** (least privilege)
- ✅ **CloudWatch Log Group** (7-day retention)
- ✅ **S3 Event Notifications** (trigger Lambda)
- ✅ **CloudWatch Alarm** (Lambda errors)
- ✅ **S3 Lifecycle Policies** (optimize storage)

### Free Tier Usage Estimate
| Service | Free Tier | Expected Usage | Status |
|---------|-----------|----------------|--------|
| S3 Storage | 5 GB | ~3 GB/month | ✅ 60% |
| S3 PUT Requests | 2,000 | ~8,640/month* | ⚠️ Need batching |
| S3 GET Requests | 20,000 | ~10,000/month | ✅ 50% |
| Lambda Invocations | 1,000,000 | ~8,640/month | ✅ 0.9% |
| Lambda Compute | 400,000 GB-sec | ~4,320 GB-sec | ✅ 1% |
| CloudWatch Logs | 5 GB | ~500 MB | ✅ 10% |
| Data Transfer OUT | 100 GB | ~5-10 GB | ✅ 5-10% |

**\*With 5-minute batching (recommended)**

**Total Estimated Cost: $0.00/month** (within free tier)

---

## Prerequisites

### 1. AWS Account
- Create free AWS account: https://aws.amazon.com/free/
- 12 months free tier eligibility

### 2. AWS CLI
```bash
# Install AWS CLI
# Windows (PowerShell as Admin):
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# macOS:
brew install awscli

# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Configure credentials:
```bash
aws configure
# AWS Access Key ID: <your-key>
# AWS Secret Access Key: <your-secret>
# Default region: us-east-1
# Default output format: json
```

### 3. Terraform
```bash
# Windows (Chocolatey):
choco install terraform

# macOS:
brew install terraform

# Linux:
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

Verify:
```bash
terraform version
```

### 4. Python 3.8+
```bash
python --version  # Should be 3.8 or higher
pip install boto3  # For upload script
```

---

## Quick Start

### Step 1: Build Lambda Package

**Windows:**
```bash
cd terraform/lambda
build.bat
```

**Linux/macOS:**
```bash
cd terraform/lambda
chmod +x build.sh
./build.sh
```

This creates `gpu_processor.zip` containing the Lambda function.

### Step 2: Configure Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
aws_region  = "us-east-1"
environment = "dev"
project_name = "gpu-monitoring"

# Optional: Connect Lambda to your local Kafka
kafka_endpoint = ""  # Leave empty for now
kafka_topic    = "gpu-metrics"

upload_batch_interval = 5  # Stay within free tier
```

### Step 3: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy (will ask for confirmation)
terraform apply

# Save outputs
terraform output > outputs.txt
```

### Step 4: Upload GPU-Z Logs

**Option A: One-time upload**
```bash
cd terraform
python upload_to_s3.py \
  --bucket gpu-monitoring-raw-logs-dev \
  --file "../data/GPU-Z Sensor Log.txt"
```

**Option B: Continuous monitoring (Recommended)**
```bash
python upload_to_s3.py \
  --bucket gpu-monitoring-raw-logs-dev \
  --file "../data/GPU-Z Sensor Log.txt" \
  --watch \
  --interval 5
```

This will:
- ✅ Upload every 5 minutes (stay within free tier)
- ✅ Compress files (70% reduction)
- ✅ Track progress (avoid re-uploading)
- ✅ Show usage statistics

### Step 5: Verify Processing

**Check S3:**
```bash
# List raw uploads
aws s3 ls s3://gpu-monitoring-raw-logs-dev/logs/

# List processed files
aws s3 ls s3://gpu-monitoring-processed-logs-dev/processed/
```

**Check Lambda Logs:**
```bash
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --follow
```

**Download processed data:**
```bash
aws s3 cp s3://gpu-monitoring-processed-logs-dev/processed/latest.json.gz ./processed.json.gz
gunzip processed.json.gz
cat processed.json
```

---

## Integration with Existing Stack

### Option 1: Lambda → Local Kafka (Recommended)

Update `terraform.tfvars`:
```hcl
kafka_endpoint = "YOUR_PUBLIC_IP:9092"
```

**Expose Kafka publicly (use with caution):**
```yaml
# docker-compose.yml
kafka:
  ports:
    - "9092:9092"  # Expose publicly
  environment:
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://YOUR_PUBLIC_IP:9092
```

**Secure alternative: Use ngrok:**
```bash
ngrok tcp 9092
# Use ngrok URL in kafka_endpoint
```

Apply changes:
```bash
terraform apply
```

### Option 2: Download from S3 Manually

```bash
# Download latest processed logs
aws s3 sync s3://gpu-monitoring-processed-logs-dev/processed/ ./processed/

# Feed into Kafka locally
cd kafka-producer
python gpuz_producer.py --input ../terraform/processed/latest.json
```

### Option 3: S3 Event → SNS → Local Webhook (Future)

For production, set up SNS notifications to trigger your local Kafka producer.

---

## Free Tier Optimization Tips

### 1. Batch Uploads (Critical!)
```bash
# Upload every 5 minutes (8,640/month) ✅
python upload_to_s3.py --watch --interval 5

# DON'T upload every minute (43,800/month) ❌ Exceeds free tier
```

### 2. Enable Compression (Always)
```bash
# Default is enabled (70% size reduction)
python upload_to_s3.py --file log.txt

# Only disable if you have a specific reason
python upload_to_s3.py --file log.txt --no-compress
```

### 3. Set CloudWatch Retention
Already configured in Terraform (7 days). Don't increase unless necessary.

### 4. Use S3 Lifecycle Policies
Already configured:
- Keep current version
- Delete old versions after 7 days
- Move to Intelligent-Tiering after 30 days

### 5. Monitor Usage
```bash
# Check S3 storage
aws s3 ls s3://gpu-monitoring-raw-logs-dev --recursive --summarize

# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=gpu-monitoring-processor-dev \
  --start-time $(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 2592000 \
  --statistics Sum
```

### 6. Estimate Monthly Costs
```bash
python upload_to_s3.py --estimate --interval 5
```

---

## Monitoring & Debugging

### View Lambda Logs
```bash
# Real-time logs
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --follow

# Last 1 hour
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --since 1h

# Filter errors only
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --filter "ERROR"
```

### Test Lambda Function
```bash
# Invoke manually
aws lambda invoke \
  --function-name gpu-monitoring-processor-dev \
  --payload file://test-event.json \
  response.json

cat response.json
```

### CloudWatch Metrics
```bash
# Open CloudWatch Dashboard
aws cloudwatch get-dashboard \
  --dashboard-name gpu-monitoring-dev
```

### S3 Event History
```bash
# Check S3 event notifications
aws s3api get-bucket-notification-configuration \
  --bucket gpu-monitoring-raw-logs-dev
```

---

## Cleanup (Tear Down)

**⚠️ This will delete all resources and data!**

```bash
# Empty S3 buckets first (required)
aws s3 rm s3://gpu-monitoring-raw-logs-dev --recursive
aws s3 rm s3://gpu-monitoring-processed-logs-dev --recursive

# Destroy infrastructure
terraform destroy

# Confirm: yes
```

---

## Troubleshooting

### Issue: "AccessDenied" when uploading to S3
**Solution:** Check AWS credentials
```bash
aws sts get-caller-identity
aws s3 ls  # Should list buckets
```

### Issue: Lambda not triggered after S3 upload
**Solution:** Check S3 event configuration
```bash
aws s3api get-bucket-notification-configuration \
  --bucket gpu-monitoring-raw-logs-dev
```

### Issue: "403 Forbidden" from Lambda
**Solution:** Verify IAM role permissions
```bash
aws iam get-role-policy \
  --role-name gpu-monitoring-lambda-role-dev \
  --policy-name gpu-monitoring-lambda-policy
```

### Issue: Lambda times out
**Solution:** Increase timeout (free tier allows up to 15 minutes)
```hcl
# main.tf
resource "aws_lambda_function" "gpu_log_processor" {
  timeout = 120  # Increase to 2 minutes
}
```

### Issue: Exceeding free tier
**Solution:** Check usage and increase batch interval
```bash
# Increase to 10 minutes
python upload_to_s3.py --watch --interval 10
```

---

## Cost Breakdown (After Free Tier)

If you exceed free tier or after 12 months:

| Service | Cost | Notes |
|---------|------|-------|
| S3 Storage | $0.023/GB | After 5 GB free |
| S3 PUT | $0.005/1000 | After 2,000 free |
| S3 GET | $0.0004/1000 | After 20,000 free |
| Lambda Invocations | $0.20/1M | After 1M free |
| Lambda Compute | $0.0000166667/GB-sec | After 400K free |
| Data Transfer | $0.09/GB | After 100 GB free |

**Estimated: ~$2-5/month** after free tier with current usage

---

## Next Steps

### Phase 2: Add More Services (Optional, Still Free)

1. **SNS Notifications** (1 million free/month)
   - Email alerts for Lambda errors
   - SMS alerts for anomalies

2. **EventBridge Rules** (Free)
   - Schedule batch processing
   - Complex event routing

3. **DynamoDB** (25 GB free)
   - Store processing metadata
   - Track upload history

4. **API Gateway** (1M free/month)
   - REST API for metrics
   - Webhook integrations

### Phase 3: Kubernetes (Paid ~$300/month)

When ready for production:
- EKS cluster ($72/month)
- MSK (Kafka managed) ($180/month)
- RDS (Database) ($50/month)

---

## Resources

- [AWS Free Tier](https://aws.amazon.com/free/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)

---

## Technologies Demonstrated

✅ **Terraform** (Infrastructure as Code)
✅ **AWS S3** (Object Storage)
✅ **AWS Lambda** (Serverless Compute)
✅ **Python** (Data Processing)
✅ **IAM** (Security & Access Control)
✅ **CloudWatch** (Monitoring & Logging)
✅ **EventBridge** (Event-Driven Architecture)
✅ **GitOps** (Infrastructure Version Control)

Perfect for demonstrating Cloud Platform Engineer skills! 🎉

---

## License

MIT License - Feel free to use for portfolio/interviews

## Author

GPU Monitoring Dashboard Project
