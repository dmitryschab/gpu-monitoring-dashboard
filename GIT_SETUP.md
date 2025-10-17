# Git Repository Setup Guide

This guide helps you prepare the repository for GitHub/GitLab with all secrets properly configured.

## ✅ Pre-Commit Checklist

Before pushing to Git, ensure:

- [ ] `.env` file is listed in `.gitignore`
- [ ] No hardcoded credentials in Python files
- [ ] `.env.example` is committed (template without secrets)
- [ ] `terraform/*.tfstate` files are gitignored
- [ ] AWS credentials are not committed

## Setup Steps

### 1. Create .env File (DO NOT COMMIT!)

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# InfluxDB Token (REQUIRED - Get from InfluxDB UI)
INFLUXDB_TOKEN=your-actual-token-here

# AWS Buckets (customize as needed)
S3_BUCKET_RAW=your-raw-bucket-name
S3_BUCKET_PROCESSED=your-processed-bucket-name

# GPU-Z Log Path (your local path)
GPU_Z_LOG_PATH=C:\Users\your-username\Documents\projects\GPU-Z Sensor Log.txt
```

### 2. Initialize Git Repository

```bash
cd gpu-monitoring-dashboard
git init
git add .
git commit -m "Initial commit: GPU monitoring dashboard with Terraform, AWS, InfluxDB, and Grafana"
```

### 3. Verify No Secrets Are Committed

Run this command to check for accidentally committed secrets:

```bash
# Check for InfluxDB tokens
git grep -i "my-super-secret-auth-token" || echo "✅ No hardcoded tokens found"

# Check for AWS bucket names in tracked files
git ls-files | xargs grep "gpu-monitoring-raw-logs-dev" 2>/dev/null | grep -v ".env.example\|.md\|.tf" || echo "✅ No hardcoded bucket names found"

# Verify .env is gitignored
git check-ignore .env && echo "✅ .env is properly gitignored" || echo "⚠️ WARNING: .env is NOT gitignored!"
```

### 4. Create GitHub/GitLab Repository

**GitHub:**
```bash
gh repo create gpu-monitoring-dashboard --public --source=. --remote=origin
git push -u origin main
```

**GitLab:**
```bash
git remote add origin git@gitlab.com:username/gpu-monitoring-dashboard.git
git branch -M main
git push -u origin main
```

**Manual:**
```bash
git remote add origin https://github.com/username/gpu-monitoring-dashboard.git
git branch -M main
git push -u origin main
```

## Files That SHOULD Be Committed

✅ **Safe to commit:**
- `.env.example` - Template without secrets
- `.gitignore` - Git ignore rules
- `*.py` - Python scripts (now use environment variables)
- `*.tf` - Terraform files (no secrets)
- `*.yaml` - Kubernetes manifests
- `*.json` - Grafana dashboards
- `*.md` - Documentation
- `requirements.txt` - Python dependencies

## Files That MUST NOT Be Committed

❌ **Never commit:**
- `.env` - Contains actual secrets
- `terraform/*.tfstate` - May contain sensitive data
- `terraform/*.tfvars` - May contain secrets
- `*.log` - Log files
- `processed_logs/` - Processed data
- `GPU-Z Sensor Log.txt` - Raw GPU data
- `pipeline_state.json` - State file
- `.aws/credentials` - AWS credentials

## Environment Variables Required

When cloning the repo, collaborators need to set:

### Required:
- `INFLUXDB_TOKEN` - Get from InfluxDB UI (Data → API Tokens)

### Optional (have sensible defaults):
- `S3_BUCKET_RAW`
- `S3_BUCKET_PROCESSED`
- `AWS_REGION`
- `INFLUXDB_URL`
- `INFLUXDB_ORG`
- `INFLUXDB_BUCKET`
- `GPU_Z_LOG_PATH`

## For New Contributors

If someone clones your repository, they need to:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure InfluxDB:**
   - Start InfluxDB
   - Create organization "gpu-monitoring"
   - Create bucket "gpu-metrics"
   - Generate API token
   - Add token to `.env` file

4. **Configure AWS:**
   ```bash
   aws configure
   ```

5. **Deploy Terraform:**
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

6. **Update `.env` with Terraform outputs:**
   - Copy S3 bucket names from Terraform output
   - Update `.env` file

## Security Audit

Run these commands to ensure no secrets leaked:

```bash
# Check all tracked files for tokens
git grep -i "token.*=" | grep -v ".env.example\|.md"

# Check for hardcoded URLs with credentials
git grep -E "https?://[^:]+:[^@]+@"

# Check for AWS keys (should return nothing)
git grep -E "(AWS_ACCESS_KEY|AWS_SECRET_KEY)" | grep -v ".example\|.md"

# List all ignored files (should include .env)
git status --ignored
```

## CI/CD Setup (GitHub Actions)

If using GitHub Actions, add secrets in:
`Settings → Secrets and variables → Actions`

Required secrets:
- `INFLUXDB_TOKEN`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET_RAW`
- `S3_BUCKET_PROCESSED`

## Troubleshooting

### "ValueError: INFLUXDB_TOKEN environment variable is required"

**Solution:** Create `.env` file from template:
```bash
cp .env.example .env
# Edit .env and add your INFLUXDB_TOKEN
```

### ".env file was accidentally committed"

**Solution:** Remove from Git history:
```bash
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Remove .env and add to gitignore"
git push --force  # ⚠️ Only if you haven't shared the repo yet!
```

Then rotate all secrets that were in the file!

### "Want to switch between environments"

Create multiple env files:
```bash
.env.dev      # Development
.env.staging  # Staging
.env.prod     # Production
```

Load specific environment:
```bash
cp .env.prod .env
python automated_pipeline.py
```

## Best Practices

1. ✅ Always use `.env.example` as a template
2. ✅ Document all required environment variables
3. ✅ Never commit `.env` files
4. ✅ Rotate secrets if they're accidentally exposed
5. ✅ Use different AWS buckets per environment
6. ✅ Review `.gitignore` before first commit
7. ✅ Run security audit commands regularly

## Getting InfluxDB Token

1. Open InfluxDB UI: http://localhost:8086
2. Login with your credentials
3. Go to: **Data → API Tokens**
4. Click: **Generate API Token → Read/Write Token**
5. Select buckets: `gpu-metrics` and `gpu-metrics-daily`
6. Copy the token
7. Add to `.env`: `INFLUXDB_TOKEN=your-token-here`

## Support

If you have questions about setup, create an issue on GitHub/GitLab.
