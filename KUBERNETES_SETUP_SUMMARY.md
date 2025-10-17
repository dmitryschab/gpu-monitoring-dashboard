# Kubernetes Orchestration - Setup Summary

## What Was Added

Kubernetes orchestration has been added to your GPU Monitoring Dashboard with **automated daily batch analytics**.

### New Files Created

#### Docker Images (`docker/` directory)
- `Dockerfile.kafka-producer` - Container for Kafka producer
- `Dockerfile.influxdb-consumer` - Container for InfluxDB consumer
- `Dockerfile.batch-analytics` - Container for Spark batch analytics

#### Kubernetes Manifests (`kubernetes/` directory)
- `00-namespace.yaml` - Creates gpu-monitoring namespace
- `01-zookeeper.yaml` - Zookeeper deployment and service
- `02-kafka.yaml` - Kafka broker deployment and service
- `03-hadoop.yaml` - HDFS NameNode and DataNode with persistent storage
- `04-spark.yaml` - Spark Master and Workers
- `05-influxdb.yaml` - InfluxDB with persistent storage
- `06-grafana.yaml` - Grafana with persistent storage
- **`07-batch-analytics-cronjob.yaml`** - **Daily analytics CronJob (KEY FEATURE)**
- `08-persistent-volumes.yaml` - Persistent volume claims
- `09-configmaps.yaml` - Configuration data

#### Deployment Scripts
- `build-images.sh` / `build-images.bat` - Build Docker images
- `push-images.sh` - Push images to registry
- `deploy.sh` / `deploy.bat` - Deploy to Kubernetes
- `undeploy.sh` - Remove from Kubernetes
- `README.md` - Quick reference guide

#### Documentation
- `KUBERNETES_DEPLOYMENT.md` - Complete deployment guide
- `KUBERNETES_QUICKSTART.md` - Quick start guide
- `KUBERNETES_SETUP_SUMMARY.md` - This file

## Key Features

### 1. Automated Daily Analytics ✅

**CronJob Configuration:**
- **Schedule**: Daily at 2:00 AM (UTC)
- **Concurrency**: Forbid (prevents overlapping runs)
- **Retry**: Up to 2 retries on failure
- **Timeout**: 2 hours maximum
- **History**: Keeps last 3 successful and 3 failed jobs

**What It Does:**
1. Reads GPU metrics from HDFS
2. Computes daily statistics
3. Analyzes hourly patterns
4. Detects temperature spikes
5. Performs correlation analysis
6. Saves results to HDFS

### 2. Persistent Storage ✅

All data persists across pod restarts:
- HDFS data (50 Gi)
- InfluxDB metrics (20 Gi)
- Grafana dashboards (5 Gi)
- Analytics results

### 3. Scalability ✅

Easily scale components:
```bash
# Scale Spark workers
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=4
```

### 4. Manual Control ✅

Run analytics on-demand anytime:
```bash
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  manual-run-$(date +%s)
```

## Quick Start

### 1. Build Images
```bash
# Windows
.\kubernetes\build-images.bat

# Linux/Mac
./kubernetes/build-images.sh
```

### 2. Deploy
```bash
# Windows
.\kubernetes\deploy.bat

# Linux/Mac
./kubernetes/deploy.sh
```

### 3. Verify
```bash
kubectl get pods -n gpu-monitoring
kubectl get cronjob -n gpu-monitoring
```

### 4. Access Grafana
```bash
kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000
```

Open: http://localhost:3000 (admin/admin)

## How It Ensures Daily Updates

### Automated Execution

The CronJob **guarantees** analytics run at least once daily:

1. **Scheduled Trigger**: Kubernetes automatically starts the job at 2 AM
2. **Failure Recovery**: Retries up to 2 times if job fails
3. **No Overlap**: `concurrencyPolicy: Forbid` prevents concurrent runs
4. **Monitoring**: Job history tracks success/failure

### Manual Override

Don't want to wait? Trigger immediately:
```bash
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  manual-$(date +%s)
```

### Monitoring Execution

```bash
# Check last run
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics

# View logs
kubectl logs -n gpu-monitoring -l app=batch-analytics-pod
```

## Customization

### Change Schedule

Edit `kubernetes/07-batch-analytics-cronjob.yaml`:

```yaml
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
```

Cron format examples:
- `"0 2 * * *"` - Daily at 2 AM (default)
- `"0 */6 * * *"` - Every 6 hours
- `"0 2,14 * * *"` - 2 AM and 2 PM daily
- `"0 2 * * 0"` - Weekly on Sundays

### Adjust Resources

Edit `kubernetes/07-batch-analytics-cronjob.yaml`:

```yaml
resources:
  requests:
    memory: "4Gi"  # Increase for large datasets
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

### Configure Analytics

Edit `kubernetes/09-configmaps.yaml`:

```yaml
data:
  TEMP_SPIKE_THRESHOLD: "5.0"
  HIGH_TEMP_THRESHOLD: "80.0"
  HIGH_LOAD_THRESHOLD: "90.0"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CronJob (Daily 2 AM)                    │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  Batch Analytics Job                          │  │   │
│  │  │  - Read from HDFS                             │  │   │
│  │  │  - Compute statistics                         │  │   │
│  │  │  - Detect anomalies                           │  │   │
│  │  │  - Save results                               │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Spark Cluster (Master + Workers)            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │    HDFS (NameNode + DataNode) - Persistent          │   │
│  │    /gpu-metrics (input)                              │   │
│  │    /gpu-analytics (output)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Real-time Pipeline                           │   │
│  │  Kafka → Streaming → InfluxDB → Grafana            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Resource Requirements

### Storage (Total: ~90 Gi)
- NameNode: 10 Gi
- DataNode: 50 Gi
- InfluxDB: 20 Gi
- Grafana: 5 Gi
- Spark Jobs: 5 Gi

### Compute
- Analytics Job: 1-2 CPU, 2-4 Gi RAM
- Spark Workers: 2 CPU, 2 Gi RAM (per worker)
- Other services: ~4 CPU, 8 Gi RAM

**Minimum Cluster**: 8 CPU cores, 16 Gi RAM, 90 Gi storage

## Common Commands

### Check CronJob
```bash
kubectl get cronjob -n gpu-monitoring
```

### View Recent Jobs
```bash
kubectl get jobs -n gpu-monitoring --sort-by=.metadata.creationTimestamp
```

### Trigger Manual Run
```bash
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  manual-$(date +%s)
```

### View Logs
```bash
kubectl logs -n gpu-monitoring -l app=batch-analytics-pod -f
```

### Scale Workers
```bash
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=4
```

### Access Services
```bash
# Grafana
kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000

# Spark UI
kubectl port-forward -n gpu-monitoring svc/spark-master 8080:8080

# HDFS UI
kubectl port-forward -n gpu-monitoring svc/namenode 9870:9870
```

## Troubleshooting

### Job Not Running
```bash
# Check if suspended
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o jsonpath='{.spec.suspend}'

# Check last schedule
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o jsonpath='{.status.lastScheduleTime}'
```

### Job Failed
```bash
# Get job details
kubectl describe job -n gpu-monitoring <job-name>

# View pod logs
kubectl logs -n gpu-monitoring <pod-name>
```

### Storage Full
```bash
# Check PVC status
kubectl get pvc -n gpu-monitoring

# Clean old data
kubectl exec -n gpu-monitoring namenode-0 -- hdfs dfs -rm -r /gpu-metrics/old
```

## Next Steps

1. **Deploy**: Run `./kubernetes/deploy.sh` (or `.bat` on Windows)
2. **Verify**: Check pods are running
3. **Wait**: Let CronJob run at 2 AM, or trigger manually
4. **Monitor**: Check Grafana for analytics results
5. **Customize**: Adjust schedule, resources, or thresholds as needed

## Documentation

- **[Quick Start Guide](KUBERNETES_QUICKSTART.md)** - Get started in 5 minutes
- **[Full Deployment Guide](KUBERNETES_DEPLOYMENT.md)** - Comprehensive instructions
- **[Kubernetes README](kubernetes/README.md)** - Quick command reference
- **[Architecture](ARCHITECTURE.md)** - System design
- **[Analytics Guide](LONG_TERM_ANALYTICS_GUIDE.md)** - Understanding analytics

## Benefits

✅ **Automated** - No manual intervention needed
✅ **Reliable** - Kubernetes ensures job execution
✅ **Scalable** - Easy to scale for more data
✅ **Persistent** - Data survives pod restarts
✅ **Flexible** - Manual triggers available anytime
✅ **Production-Ready** - Monitoring and error handling included

## Summary

Your GPU monitoring dashboard now has **Kubernetes orchestration** that:

1. **Runs batch analytics daily at 2 AM** (configurable)
2. **Persists all data** across restarts
3. **Scales easily** for larger datasets
4. **Provides manual control** for on-demand execution
5. **Includes monitoring** for job success/failure

The system ensures your historical analysis is **always up-to-date**, running **at least once daily**, with the ability to run **more frequently** if needed!
