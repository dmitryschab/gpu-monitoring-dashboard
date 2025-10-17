# Security Checklist for Git

Before pushing to Git, complete this checklist:

## ✅ Environment Variables Setup

- [x] `.env.example` created with template values
- [x] `.env` file added to `.gitignore`
- [x] All Python scripts refactored to use `os.getenv()`
- [x] `python-dotenv` added to `requirements.txt`
- [x] InfluxDB token removed from all `.py` files

## ✅ Files Status

### Safe to Commit (✅):
- `automated_pipeline.py` - Uses environment variables
- `load_s3_to_influxdb_v2.py` - Uses environment variables
- `.env.example` - Template only, no secrets
- `.gitignore` - Includes `.env` and secrets
- `requirements.txt` - Dependencies only
- `terraform/*.tf` - Infrastructure code (no secrets)
- `*.md` - Documentation
- `*.json` - Grafana dashboards
- `*.yaml` - Kubernetes manifests

### Never Commit (❌):
- `.env` - **Contains actual secrets!**
- `terraform/*.tfstate` - May contain sensitive data
- `terraform/*.tfvars` - May contain secrets
- `processed_logs/` - Data files
- `pipeline_state.json` - State file
- `*.log` - Log files
- `GPU-Z Sensor Log.txt` - Raw data

## 🔒 Secrets Removed

The following secrets have been refactored to environment variables:

| Secret | Old Location | New Location |
|--------|-------------|--------------|
| InfluxDB Token | `automated_pipeline.py` line 39 | `.env` → `INFLUXDB_TOKEN` |
| InfluxDB Token | `load_s3_to_influxdb_v2.py` line 21 | `.env` → `INFLUXDB_TOKEN` |
| S3 Bucket Names | Multiple files | `.env` → `S3_BUCKET_*` |
| AWS Region | Multiple files | `.env` → `AWS_REGION` |
| InfluxDB URL | Multiple files | `.env` → `INFLUXDB_URL` |

## 🔍 Pre-Commit Audit Commands

Run these before committing:

```bash
# 1. Check for hardcoded tokens
git add -A
git grep -i "my-super-secret-auth-token" -- "*.py" && echo "❌ FOUND HARDCODED TOKEN!" || echo "✅ No hardcoded tokens"

# 2. Check for hardcoded passwords
git grep -iE "(password|passwd|pwd).*=.*['\"]" -- "*.py" "*.tf" && echo "⚠️ Check passwords" || echo "✅ No hardcoded passwords"

# 3. Verify .env is gitignored
git check-ignore .env && echo "✅ .env is gitignored" || echo "❌ .env NOT gitignored - ADD TO .gitignore NOW!"

# 4. Check what will be committed
git status

# 5. Verify no sensitive files staged
git diff --cached --name-only | grep -E "\.env$|\.tfstate|credentials|\.pem" && echo "❌ SENSITIVE FILES STAGED!" || echo "✅ No sensitive files"
```

## 📝 First Time Git Init

```bash
cd gpu-monitoring-dashboard

# Initialize repository
git init
git branch -M main

# Add all safe files
git add .

# Verify no secrets
git grep "my-super-secret-auth-token" -- "*.py"  # Should return nothing

# Commit
git commit -m "Initial commit: GPU monitoring dashboard

- Terraform AWS infrastructure (S3, Lambda, IAM)
- Python monitoring pipeline with env vars
- InfluxDB integration
- Grafana dashboards
- Kubernetes manifests
- Complete documentation"

# Add remote and push
git remote add origin https://github.com/username/gpu-monitoring-dashboard.git
git push -u origin main
```

## 🚨 If Secrets Were Accidentally Committed

### Option 1: Before Pushing (Easy)

```bash
# Remove last commit
git reset HEAD~1

# Update .gitignore
echo ".env" >> .gitignore

# Re-add files
git add .
git commit -m "Initial commit"
```

### Option 2: After Pushing (Nuclear Option)

```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (⚠️ DANGEROUS - only if repo is private and not shared!)
git push origin --force --all
```

**Then immediately:**
1. Rotate all exposed secrets
2. Generate new InfluxDB token
3. Update `.env` file
4. Notify team if repo was shared

## 📋 Environment Setup for New Users

New users cloning the repo need to:

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Get InfluxDB token:**
   - Open InfluxDB: http://localhost:8086
   - Go to Data → API Tokens
   - Generate Read/Write Token for `gpu-metrics` bucket
   - Copy token to `.env`

3. **Configure AWS:**
   ```bash
   aws configure
   ```

4. **Deploy infrastructure:**
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

5. **Update `.env` with outputs:**
   ```bash
   # Copy bucket names from Terraform output
   S3_BUCKET_RAW=<from-terraform>
   S3_BUCKET_PROCESSED=<from-terraform>
   ```

## ✅ Final Checklist

Before pushing to GitHub/GitLab:

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` has no real secrets
- [ ] All Python files use `os.getenv()`
- [ ] `requirements.txt` includes `python-dotenv`
- [ ] Ran audit commands (no hardcoded secrets found)
- [ ] `README.md` documents environment setup
- [ ] `GIT_SETUP.md` provides detailed instructions
- [ ] Terraform state files gitignored
- [ ] No AWS credentials in repo
- [ ] Grafana dashboards have no hardcoded credentials
- [ ] Documentation mentions `.env` requirement

## 🎯 Current Status

**Repository is ready for Git! ✅**

All hardcoded credentials have been refactored to environment variables. The repository can now be safely pushed to a public Git hosting service.

**Next Steps:**
1. Run audit commands above
2. Initialize git repository
3. Push to GitHub/GitLab
4. Share `.env.example` with team
5. Document how to get InfluxDB token

## 📚 Additional Resources

- [Git Security Best Practices](https://docs.github.com/en/code-security)
- [Managing Secrets in Git](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [InfluxDB Token Management](https://docs.influxdata.com/influxdb/v2/security/tokens/)
