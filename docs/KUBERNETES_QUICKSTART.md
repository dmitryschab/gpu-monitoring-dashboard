# Kubernetes Quick Start - GPU Monitoring Dashboard

## Overview

This setup adds **Kubernetes orchestration** with a **daily CronJob** that automatically runs batch analytics on your GPU monitoring data.

### Key Features

✅ **Automated Daily Analytics** - Runs at 2 AM every day
✅ **Persistent Storage** - All data persists across restarts
✅ **Scalable** - Easy to scale Spark workers
✅ **Manual Triggers** - Run analytics on-demand anytime
✅ **Production Ready** - Includes monitoring, logging, and error handling

## What Gets Deployed

| Component | Purpose | Schedule |
|-----------|---------|----------|
| **CronJob** | Batch analytics | Daily at 2 AM |
| Kafka + Zookeeper | Real-time streaming | Always running |
| Hadoop HDFS | Data storage | Always running |
| Spark Cluster | Analytics processing | Always running |
| InfluxDB | Metrics database | Always running |
| Grafana | Visualization | Always running |

## 5-Minute Setup

### Step 1: Prerequisites

Ensure you have:
- [ ] Kubernetes cluster running
- [ ] `kubectl` configured
- [ ] Docker installed
- [ ] ~90 Gi storage available

### Step 2: Build Images

```bash
cd gpu-monitoring-dashboard

# Windows
.\kubernetes\build-images.bat

# Linux/Mac
./kubernetes/build-images.sh
```

### Step 3: Deploy

```bash
# Windows
.\kubernetes\deploy.bat

# Linux/Mac
./kubernetes/deploy.sh
```

### Step 4: Verify

```bash
# Check all pods are running
kubectl get pods -n gpu-monitoring

# Check CronJob is scheduled
kubectl get cronjob -n gpu-monitoring
```

Expected output:
```
NAME                  SCHEDULE    SUSPEND   ACTIVE   LAST SCHEDULE   AGE
gpu-batch-analytics   0 2 * * *   False     0        <none>          2m
```

### Step 5: Access Grafana

```bash
kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000
```

Open: http://localhost:3000
Login: `admin` / `admin`

## Daily Analytics Automation

### How It Works

1. **CronJob runs daily at 2 AM** (UTC)
2. Reads data from HDFS `/gpu-metrics`
3. Computes:
   - Daily statistics
   - Hourly patterns
   - Temperature spike detection
   - Correlation analysis
4. Saves results to HDFS `/gpu-analytics`
5. Results visible in Grafana dashboards

### View Last Run

```bash
# Check last schedule time
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics

# View logs from last job
kubectl logs -n gpu-monitoring -l app=batch-analytics-pod --tail=100
```

### Manually Trigger Analytics

Don't want to wait until 2 AM? Run immediately:

```bash
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  manual-run-$(date +%s)
```

Check progress:
```bash
# Watch job status
kubectl get jobs -n gpu-monitoring --watch

# View real-time logs
kubectl logs -n gpu-monitoring -l app=batch-analytics-pod -f
```

## Change Schedule

### Every 6 Hours

Edit [kubernetes/07-batch-analytics-cronjob.yaml](kubernetes/07-batch-analytics-cronjob.yaml):

```yaml
spec:
  schedule: "0 */6 * * *"
```

### Twice Daily (2 AM and 2 PM)

```yaml
spec:
  schedule: "0 2,14 * * *"
```

### Weekly (Sundays at 2 AM)

```yaml
spec:
  schedule: "0 2 * * 0"
```

Apply changes:
```bash
kubectl apply -f kubernetes/07-batch-analytics-cronjob.yaml
```

## Common Tasks

### View All Jobs

```bash
kubectl get jobs -n gpu-monitoring
```

### Delete Old Jobs

```bash
# Delete completed jobs
kubectl delete jobs -n gpu-monitoring --field-selector status.successful=1

# Delete failed jobs
kubectl delete jobs -n gpu-monitoring --field-selector status.failed=1
```

### Check Storage Usage

```bash
# View persistent volumes
kubectl get pvc -n gpu-monitoring
```

### Scale Spark Workers

```bash
# Increase to 4 workers for faster processing
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=4

# Decrease to 1 worker to save resources
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=1
```

### View Spark UI

```bash
kubectl port-forward -n gpu-monitoring svc/spark-master 8080:8080
```

Open: http://localhost:8080

### View HDFS UI

```bash
kubectl port-forward -n gpu-monitoring svc/namenode 9870:9870
```

Open: http://localhost:9870

## Troubleshooting

### CronJob Not Running

```bash
# Check if suspended
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o jsonpath='{.spec.suspend}'

# Resume if suspended
kubectl patch cronjob -n gpu-monitoring gpu-batch-analytics -p '{"spec":{"suspend":false}}'
```

### Job Failed

```bash
# Get failed job name
kubectl get jobs -n gpu-monitoring --field-selector status.failed=1

# View failure details
kubectl describe job -n gpu-monitoring <job-name>

# Check pod logs
kubectl logs -n gpu-monitoring <pod-name>
```

### Out of Storage

```bash
# Check PVC status
kubectl get pvc -n gpu-monitoring

# Clean old data from HDFS
kubectl exec -n gpu-monitoring namenode-0 -- hdfs dfs -rm -r /gpu-metrics/old-data
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n gpu-monitoring

# Describe problematic pod
kubectl describe pod -n gpu-monitoring <pod-name>

# Check events
kubectl get events -n gpu-monitoring --sort-by='.lastTimestamp'
```

## Configuration

### Adjust Analytics Parameters

Edit [kubernetes/09-configmaps.yaml](kubernetes/09-configmaps.yaml):

```yaml
data:
  TEMP_SPIKE_THRESHOLD: "5.0"   # Change to "10.0" for less sensitive
  HIGH_TEMP_THRESHOLD: "80.0"   # Change warning threshold
  HIGH_LOAD_THRESHOLD: "90.0"   # Change load threshold
```

Apply:
```bash
kubectl apply -f kubernetes/09-configmaps.yaml
```

### Change Resource Limits

Edit [kubernetes/07-batch-analytics-cronjob.yaml](kubernetes/07-batch-analytics-cronjob.yaml):

```yaml
resources:
  requests:
    memory: "4Gi"  # Increase for large datasets
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

Apply:
```bash
kubectl apply -f kubernetes/07-batch-analytics-cronjob.yaml
```

## Cleanup

### Remove Everything (Keep Data)

```bash
# Windows
.\kubernetes\undeploy.bat

# Linux/Mac
./kubernetes/undeploy.sh

# Choose 'N' when asked about namespace
```

### Complete Removal (Delete Data)

```bash
kubectl delete namespace gpu-monitoring
```

**Warning**: This deletes all historical data!

## Next Steps

1. ✅ **Monitor First Run** - Wait for 2 AM or trigger manually
2. ✅ **Check Grafana** - View analytics results
3. ✅ **Review Logs** - Ensure no errors
4. ✅ **Adjust Schedule** - Change if needed
5. ✅ **Set Alerts** - Configure Grafana alerts for anomalies

## Production Checklist

Before deploying to production:

- [ ] Change default passwords in manifests
- [ ] Use Kubernetes Secrets for credentials
- [ ] Configure appropriate storage class
- [ ] Set resource limits for all pods
- [ ] Enable persistent storage backups
- [ ] Set up monitoring (Prometheus)
- [ ] Configure log aggregation
- [ ] Use private container registry
- [ ] Enable network policies
- [ ] Set up TLS/SSL for services

## Documentation

- **[Full Deployment Guide](KUBERNETES_DEPLOYMENT.md)** - Detailed instructions
- **[Kubernetes README](kubernetes/README.md)** - Quick reference
- **[Architecture](ARCHITECTURE.md)** - System architecture
- **[Analytics Guide](LONG_TERM_ANALYTICS_GUIDE.md)** - Understanding analytics

## Support

### View Logs
```bash
kubectl logs -n gpu-monitoring <pod-name>
```

### Check Events
```bash
kubectl get events -n gpu-monitoring
```

### Describe Resources
```bash
kubectl describe <resource> -n gpu-monitoring <name>
```

## Summary

You now have:

✅ **Automated batch analytics** running daily
✅ **Persistent storage** for all data
✅ **Scalable infrastructure** on Kubernetes
✅ **Manual control** to run analytics anytime
✅ **Production-ready** monitoring and logging

The CronJob ensures your GPU monitoring dashboard always has fresh historical analysis data, updated **at least once daily** or on-demand whenever you need it!
