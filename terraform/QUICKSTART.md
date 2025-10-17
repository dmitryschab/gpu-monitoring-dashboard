# Terraform Quick Start - 5 Minutes to AWS ☁️

**100% Free Tier - $0.00/month** ✅

## Prerequisites (5 min setup)

1. **AWS Account** → [aws.amazon.com/free](https://aws.amazon.com/free)
2. **AWS CLI** → `aws configure` (enter your keys)
3. **Terraform** → `terraform version` (install if needed)
4. **Python 3.8+** → `pip install boto3`

---

## Step 1: Build Lambda (1 min)

**Windows:**
```bash
cd terraform\lambda
build.bat
```

**Linux/macOS:**
```bash
cd terraform/lambda
./build.sh
```

✅ Creates `gpu_processor.zip`

---

## Step 2: Configure (1 min)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

**Optional:** Edit `terraform.tfvars` if you want to change region/names

---

## Step 3: Deploy (2 min)

```bash
terraform init
terraform apply
```

Type **yes** when prompted.

✅ Deployed! Note the bucket name from output.

---

## Step 4: Upload Logs (1 min)

```bash
cd terraform

# One-time upload
python upload_to_s3.py -b gpu-monitoring-raw-logs-dev -f "../data/GPU-Z Sensor Log.txt"

# OR continuous (recommended)
python upload_to_s3.py -b gpu-monitoring-raw-logs-dev -f "../data/GPU-Z Sensor Log.txt" --watch
```

**Leave it running!** It uploads every 5 min.

---

## Verify It Works

**Check processed files:**
```bash
aws s3 ls s3://gpu-monitoring-processed-logs-dev/processed/
```

**View Lambda logs:**
```bash
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --follow
```

**Download processed data:**
```bash
aws s3 cp s3://gpu-monitoring-processed-logs-dev/processed/20241016_120000_GPU-Z_Sensor_Log.json.gz ./
gunzip *.json.gz
cat *.json
```

---

## What's Happening?

```
Your GPU-Z log → Upload Script (every 5 min) → S3
                                                 ↓
                                           Lambda parses
                                                 ↓
                                        Processed JSON → S3
```

**All free!** You're using:
- S3: 3 GB / 5 GB free ✅
- Lambda: 8,640 / 1,000,000 invocations free ✅
- CloudWatch: 500 MB / 5 GB free ✅

---

## Cleanup (Delete Everything)

```bash
aws s3 rm s3://gpu-monitoring-raw-logs-dev --recursive
aws s3 rm s3://gpu-monitoring-processed-logs-dev --recursive
terraform destroy
```

Type **yes** to confirm.

---

## Next Steps

1. **Connect to Kafka:** Edit `terraform.tfvars`, add your Kafka IP
2. **Add monitoring:** View CloudWatch dashboard
3. **Automate:** Schedule upload script with cron/Task Scheduler

**Full docs:** See [README.md](README.md)

---

## Common Issues

**"AccessDenied"** → Run `aws configure` again

**"Lambda not triggered"** → Wait 1-2 min, Lambda has cold start

**"Exceeding free tier"** → Increase `--interval` to 10 minutes

---

🎉 **You just deployed serverless infrastructure with Terraform!**

Perfect for job interviews demonstrating:
- ✅ Terraform (IaC)
- ✅ AWS (S3, Lambda, IAM, CloudWatch)
- ✅ Python
- ✅ Event-driven architecture
- ✅ Cost optimization
