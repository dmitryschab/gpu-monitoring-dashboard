# AWS Terraform Deployment Checklist ✅

Use this checklist to ensure successful deployment.

## Pre-Deployment

### AWS Account Setup
- [ ] AWS account created ([aws.amazon.com/free](https://aws.amazon.com/free))
- [ ] IAM user created with programmatic access
- [ ] Access Key ID obtained
- [ ] Secret Access Key obtained
- [ ] Billing alerts configured (optional but recommended)

### Local Environment
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Terraform installed (`terraform version` >= 1.0)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] boto3 installed (`pip install boto3`)
- [ ] Git installed (for version control)

### Verify AWS Access
```bash
aws sts get-caller-identity  # Should show your user info
aws s3 ls                    # Should list buckets (or empty if none)
```

---

## Build & Deploy

### 1. Build Lambda Package
- [ ] Navigate to `terraform/lambda/`
- [ ] Run `build.bat` (Windows) or `./build.sh` (Linux/macOS)
- [ ] Verify `gpu_processor.zip` created (should be ~5-10 MB)

### 2. Configure Terraform
- [ ] Copy `terraform.tfvars.example` to `terraform.tfvars`
- [ ] Review and update variables:
  - [ ] `aws_region` (default: us-east-1)
  - [ ] `environment` (default: dev)
  - [ ] `project_name` (default: gpu-monitoring)
  - [ ] `kafka_endpoint` (leave empty for now)
  - [ ] `kafka_topic` (default: gpu-metrics)

### 3. Initialize Terraform
```bash
cd terraform
terraform init
```
- [ ] Terraform initialized successfully
- [ ] Providers downloaded
- [ ] `.terraform/` directory created

### 4. Preview Changes
```bash
terraform plan
```
- [ ] Plan shows resources to be created
- [ ] No errors in plan
- [ ] Review resources (should be ~15-20 resources)

### 5. Deploy Infrastructure
```bash
terraform apply
```
- [ ] Review resources to be created
- [ ] Type `yes` to confirm
- [ ] Deployment successful (typically 2-3 minutes)
- [ ] Note output values (bucket names, Lambda ARN, etc.)

### 6. Save Outputs
```bash
terraform output > outputs.txt
```
- [ ] Outputs saved to `outputs.txt`
- [ ] Note `s3_raw_bucket_name` for upload script

---

## Post-Deployment Verification

### Verify AWS Resources
- [ ] S3 buckets created:
  ```bash
  aws s3 ls | grep gpu-monitoring
  ```
- [ ] Lambda function created:
  ```bash
  aws lambda list-functions | grep gpu-monitoring
  ```
- [ ] CloudWatch log group created:
  ```bash
  aws logs describe-log-groups --log-group-name-prefix /aws/lambda/gpu-monitoring
  ```

### Test Lambda Function
- [ ] Lambda shows in AWS Console
- [ ] IAM role attached
- [ ] S3 trigger configured
- [ ] CloudWatch logs enabled

---

## Upload & Process Data

### 1. Test Upload Script
```bash
cd terraform
python upload_to_s3.py \
  --bucket gpu-monitoring-raw-logs-dev \
  --file "../data/GPU-Z Sensor Log.txt" \
  --estimate
```
- [ ] Estimate shows within free tier

### 2. Upload Sample File
```bash
python upload_to_s3.py \
  --bucket gpu-monitoring-raw-logs-dev \
  --file "../data/GPU-Z Sensor Log.txt"
```
- [ ] File uploaded successfully
- [ ] S3 key shown in output

### 3. Verify Lambda Triggered
```bash
# Wait 1-2 minutes, then check logs
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --since 5m
```
- [ ] Lambda invoked
- [ ] No errors in logs
- [ ] Processing completed

### 4. Check Processed Files
```bash
aws s3 ls s3://gpu-monitoring-processed-logs-dev/processed/
```
- [ ] Processed JSON file created
- [ ] File is compressed (.json.gz)

### 5. Download & Verify Processed Data
```bash
aws s3 cp s3://gpu-monitoring-processed-logs-dev/processed/ ./ --recursive
gunzip *.json.gz
cat *.json | head
```
- [ ] JSON file contains parsed GPU metrics
- [ ] All expected fields present

---

## Continuous Upload (Production)

### Start Continuous Upload
```bash
python upload_to_s3.py \
  --bucket gpu-monitoring-raw-logs-dev \
  --file "../data/GPU-Z Sensor Log.txt" \
  --watch \
  --interval 5
```
- [ ] Script running
- [ ] Uploads every 5 minutes
- [ ] Progress tracked in `.upload_progress.json`

### Optional: Run as Background Service

**Windows (Task Scheduler):**
- [ ] Create scheduled task
- [ ] Run on startup
- [ ] Run as service

**Linux (systemd):**
```bash
sudo cp upload_to_s3.service /etc/systemd/system/
sudo systemctl enable upload_to_s3
sudo systemctl start upload_to_s3
```
- [ ] Service created
- [ ] Service enabled
- [ ] Service running

---

## Monitoring & Maintenance

### Daily Checks
- [ ] Lambda invocations successful
- [ ] No errors in CloudWatch logs
- [ ] Processed files being created

### Weekly Checks
- [ ] Review free tier usage:
  ```bash
  # Check S3 storage
  aws s3 ls s3://gpu-monitoring-raw-logs-dev --recursive --summarize

  # Check Lambda invocations
  aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=gpu-monitoring-processor-dev \
    --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 604800 \
    --statistics Sum
  ```
- [ ] Within free tier limits
- [ ] No unexpected costs

### Monthly Checks
- [ ] Review AWS billing dashboard
- [ ] Verify $0.00 charges (free tier)
- [ ] Check for any alerts

---

## Troubleshooting

### Lambda Not Triggering
- [ ] Check S3 event notification:
  ```bash
  aws s3api get-bucket-notification-configuration \
    --bucket gpu-monitoring-raw-logs-dev
  ```
- [ ] Verify Lambda permission
- [ ] Check CloudWatch logs for errors

### Upload Fails
- [ ] Verify AWS credentials: `aws sts get-caller-identity`
- [ ] Check bucket name is correct
- [ ] Verify bucket exists: `aws s3 ls s3://bucket-name`

### Exceeding Free Tier
- [ ] Increase upload interval to 10 minutes
- [ ] Review CloudWatch retention (should be 7 days)
- [ ] Delete old S3 data: `aws s3 rm s3://bucket/old-data/ --recursive`

---

## Optional: Kafka Integration

### Enable Kafka Forwarding
- [ ] Expose Kafka publicly (or use ngrok)
- [ ] Get public IP/endpoint
- [ ] Update `terraform.tfvars`:
  ```hcl
  kafka_endpoint = "YOUR_IP:9092"
  ```
- [ ] Run `terraform apply` to update Lambda
- [ ] Verify Lambda environment variables updated
- [ ] Test: Upload file and check Kafka topic

---

## Cleanup (When Done)

### Tear Down Infrastructure
```bash
# Empty S3 buckets first
aws s3 rm s3://gpu-monitoring-raw-logs-dev --recursive
aws s3 rm s3://gpu-monitoring-processed-logs-dev --recursive

# Destroy infrastructure
terraform destroy
```
- [ ] Buckets emptied
- [ ] Terraform destroy confirmed
- [ ] All resources deleted
- [ ] Verify in AWS Console

---

## Success Criteria ✅

You've successfully deployed when:
- ✅ All AWS resources created
- ✅ Upload script works
- ✅ Lambda processes files
- ✅ Processed JSON in S3
- ✅ CloudWatch logs show success
- ✅ Within free tier limits
- ✅ $0.00 monthly cost

---

## Skills Demonstrated 🎯

Perfect for job interviews - you can now demonstrate:
- ✅ **Terraform** (Infrastructure as Code)
- ✅ **AWS** (S3, Lambda, IAM, CloudWatch)
- ✅ **Python** (Data processing, AWS SDK)
- ✅ **Event-Driven Architecture** (S3 → Lambda)
- ✅ **DevOps** (Automation, CI/CD concepts)
- ✅ **Cost Optimization** (Free tier compliance)
- ✅ **Security** (IAM, encryption, least privilege)
- ✅ **Monitoring** (CloudWatch, alerting)

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Environment:** ☐ Dev ☐ Staging ☐ Prod
**Status:** ☐ Success ☐ Partial ☐ Failed
**Notes:** _______________
