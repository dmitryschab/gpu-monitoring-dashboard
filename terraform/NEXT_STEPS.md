# Next Steps - AWS Setup Required

## ✅ Completed
- [x] Terraform code created
- [x] Lambda function written
- [x] Upload script created
- [x] Documentation complete
- [x] Terraform installed (v1.13.4)
- [x] **Terraform initialized successfully!**

## ⏳ Prerequisites Needed

Before you can deploy to AWS, you need:

### 1. AWS Account (5 minutes)
If you don't have one:
1. Go to https://aws.amazon.com/free/
2. Click "Create a Free Account"
3. Follow the signup process (requires credit card but stays free)
4. Verify your email

### 2. AWS CLI Installation (2 minutes)

**Install AWS CLI:**
```powershell
# Open PowerShell as Administrator and run:
winget install Amazon.AWSCLI
```

After installation, **restart your terminal**.

### 3. AWS Credentials Setup (3 minutes)

1. **Get AWS Access Keys:**
   - Log into AWS Console: https://console.aws.amazon.com
   - Click your name (top right) → Security credentials
   - Scroll to "Access keys" → Create access key
   - Choose "Command Line Interface (CLI)"
   - Click "Create access key"
   - **Save your Access Key ID and Secret Access Key!**

2. **Configure AWS CLI:**
   ```bash
   aws configure
   ```

   Enter:
   - AWS Access Key ID: [paste your key]
   - AWS Secret Access Key: [paste your secret]
   - Default region: us-east-1
   - Default output format: json

3. **Verify it works:**
   ```bash
   aws sts get-caller-identity
   ```

   Should show your AWS account info.

---

## 🚀 Once Prerequisites Are Ready

### Create terraform.tfvars
```bash
cd C:\Users\dmitr\Documents\projects\gpu-monitoring-dashboard\terraform
copy terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` if needed (defaults are fine for testing).

### Run Terraform Plan
```bash
terraform plan
```

This shows what will be created (no changes yet).

### Deploy to AWS
```bash
terraform apply
```

Type `yes` when prompted. Takes 2-3 minutes.

### Upload Your First Log
```bash
python upload_to_s3.py ^
  --bucket gpu-monitoring-raw-logs-dev ^
  --file "..\data\GPU-Z Sensor Log.txt"
```

### Start Continuous Upload
```bash
python upload_to_s3.py ^
  --bucket gpu-monitoring-raw-logs-dev ^
  --file "..\data\GPU-Z Sensor Log.txt" ^
  --watch
```

---

## 📋 Quick Checklist

Before running `terraform apply`, verify:
- [ ] AWS account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws sts get-caller-identity`)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] boto3 installed (`pip install boto3`)
- [ ] terraform.tfvars file created
- [ ] Lambda package built (run `lambda\build.bat`)

---

## 🆘 Need Help?

**AWS CLI Installation Issues:**
- Manual download: https://awscli.amazonaws.com/AWSCLIV2.msi
- Run installer, restart terminal

**AWS Credentials Issues:**
- Check ~/.aws/credentials file exists
- Run `aws configure` again
- Verify keys are correct (no spaces)

**Terraform Issues:**
- Make sure you're in terraform directory
- Run `terraform init` if you get errors
- Check terraform.tfvars file exists

**Python/boto3 Issues:**
```bash
pip install --upgrade boto3
```

---

## 💰 Cost Reminder

Everything in this setup is **100% free** for 12 months with AWS free tier!

Monitor your usage:
```bash
python upload_to_s3.py --estimate --interval 5
```

---

## 📚 Documentation

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - 5-minute guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Validation checklist

---

**Current Status:** ✅ Terraform initialized, ready for AWS credentials
