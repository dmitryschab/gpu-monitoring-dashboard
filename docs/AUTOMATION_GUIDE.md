# GPU Monitoring Automation Guide

## 🎯 Your Complete Automated Pipeline

This system automatically:
1. ✅ Monitors your GPU-Z log file
2. ✅ Uploads when file reaches 5MB
3. ✅ Processes through AWS Lambda
4. ✅ Loads into InfluxDB
5. ✅ Detects idle vs gaming sessions
6. ✅ Creates daily aggregates
7. ✅ Cleans up raw data from S3
8. ✅ Archives and clears local file

---

## 📋 Prerequisites

All already set up:
- ✅ AWS Lambda (processing logs)
- ✅ S3 buckets (storage)
- ✅ InfluxDB (time-series database)
- ✅ Grafana (visualization)
- ✅ Python 3.8+ with boto3, influxdb-client

---

## 🚀 Quick Start

### Option 1: Run Manually (Test First)

```bash
cd C:\Users\dmitr\Documents\projects\gpu-monitoring-dashboard
python automated_pipeline.py
```

**What it does:**
- Checks GPU-Z log every 60 seconds
- Uploads when file >= 5MB
- Processes automatically
- Shows progress in terminal

**Press Ctrl+C to stop**

### Option 2: Run as Windows Service (Recommended)

```bash
# Run as Administrator
setup_automated_monitoring.bat
```

This creates a Windows Task that:
- Starts on boot
- Runs in background
- Continues after you log out

---

## ⚙️ Configuration

Edit `automated_pipeline.py` to customize:

```python
# File path
GPU_Z_LOG_PATH = r"C:\Users\dmitr\Documents\projects\GPU-Z Sensor Log.txt"

# Upload threshold (MB)
SIZE_THRESHOLD_MB = 5  # Upload when file reaches this size

# Check interval (seconds)
CHECK_INTERVAL_SECONDS = 60  # Check every minute
```

---

## 🎮 Idle vs Gaming Detection

The system **automatically detects** your activity:

**Idle:**
- Average GPU Load < 30%
- Examples: browsing, coding, watching videos

**Gaming:**
- Average GPU Load >= 30%
- Examples: playing games, 3D rendering

**Tagging:**
- All metrics are tagged with scenario
- Grafana dashboards show separate distributions
- Easy comparison of performance characteristics

---

## 📊 Grafana Dashboard

### Import the Dashboard

1. Open Grafana: http://localhost:3000
2. Go to **Dashboards** → **New** → **Import**
3. Upload: `grafana-idle-vs-gaming-dashboard.json`
4. Select **InfluxDB** datasource
5. Click **Import**

### What You'll See

**Panel 1: Temperature Distribution**
- Histogram showing GPU temps in idle vs gaming
- See how much hotter GPU gets during gaming

**Panel 2: Power Draw Distribution**
- Compare power consumption
- Idle: typically 50-100W
- Gaming: typically 200-350W

**Panel 3: GPU Load Statistics**
- Average load for each scenario
- Min/max/median values

**Panel 4: Daily Trends**
- Long-term temperature trends
- See if thermal paste needs replacing
- Track GPU health over months

---

## 📈 Example Queries

### See Idle Temperature Distribution
```flux
from(bucket: "gpu-metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "gpu_sessions")
  |> filter(fn: (r) => r._field == "gpu_temperature")
  |> filter(fn: (r) => r.scenario == "idle")
```

### See Gaming Power Draw
```flux
from(bucket: "gpu-metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "gpu_sessions")
  |> filter(fn: (r) => r._field == "board_power_draw")
  |> filter(fn: (r) => r.scenario == "gaming")
```

### Compare Average Temps
```flux
from(bucket: "gpu-metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "gpu_sessions")
  |> filter(fn: (r) => r._field == "gpu_temperature")
  |> group(columns: ["scenario"])
  |> mean()
```

---

## 🗑️ Data Cleanup

**What Gets Deleted:**
- ✅ Raw S3 files (after processing)
- ✅ Local GPU-Z log (after archiving)

**What Gets Kept:**
- ✅ Processed data in InfluxDB
- ✅ Daily aggregates in InfluxDB
- ✅ Archived local files in `processed_logs/`

**Storage Requirements:**
- InfluxDB: ~100 MB per month (compressed)
- Archived files: ~50 MB per month
- S3: Minimal (auto-cleaned)

**Clean Old Archives:**
```bash
# Delete archives older than 90 days
cd processed_logs
del /Q *_*.txt (where date < 90 days ago)
```

---

## 🔍 Monitoring the Pipeline

### Check Pipeline Status

```python
# Check state file
import json
with open('pipeline_state.json', 'r') as f:
    state = json.load(f)
    print(f"Last processed: {state['last_processed']}")
    print(f"Total files: {len(state['processed_files'])}")
```

### View Logs

The script prints to console:
```
⏳ 14:30:15 - File too small (2.3 MB < 5 MB)
⏳ 14:31:15 - File too small (2.8 MB < 5 MB)
✅ Processing triggered: Ready to process (5.2 MB, new hash)
📤 Uploading to S3: logs/20251016_143115_GPU-Z_Sensor_Log.txt.gz
✅ Uploaded: 1.2 MB compressed
⏳ Waiting for Lambda to process...
✅ Lambda processed: processed/20251016_143120_GPU-Z_Sensor_Log.json.gz
⬇️  Downloading processed data...
✅ Downloaded 15070 records
📊 Loading 15070 records to InfluxDB...
✅ Loaded 15070 points to InfluxDB
🏷️  Tagging session as: gaming
✅ Tagged 15070 points as gaming
📈 Creating daily aggregates for 2025-10-15...
✅ Created 240 daily aggregate points
🗑️  Cleaning up raw S3 data
✅ Deleted from S3
📦 Archiving local file
✅ Local file cleared and archived
```

---

## 🐛 Troubleshooting

### Pipeline Not Starting

```bash
# Check if Python is in PATH
python --version

# Check dependencies
pip list | findstr "boto3 influxdb"

# Check state file
type pipeline_state.json
```

### Lambda Not Processing

```bash
# Check Lambda logs
aws logs tail /aws/lambda/gpu-monitoring-processor-dev --region us-east-1 --follow

# Check S3 upload
aws s3 ls s3://gpu-monitoring-raw-logs-dev/logs/
```

### InfluxDB Connection Error

```bash
# Check InfluxDB is running
kubectl get pods -n gpu-monitoring | findstr influx

# Port forward if needed
kubectl port-forward -n gpu-monitoring svc/influxdb 8086:8086
```

### Grafana Shows "0 series returned"

**Fix: Adjust time range**
- Your data is from October 12th
- Change Grafana time range to `-30d` (30 days)
- Or query with: `range(start: -30d)`

---

## 📊 Expected Results

### After 1 Week:
- ~7 processing runs
- ~100K+ data points
- Clear idle vs gaming patterns
- Daily aggregates for 7 days

### After 1 Month:
- ~30 processing runs
- ~450K+ data points
- Statistical distributions visible
- Trends emerging (temperature drift, performance changes)

### After 3 Months:
- ~90 processing runs
- ~1.3M+ data points
- Comprehensive performance profile
- Degradation tracking (thermal paste aging, etc.)

---

## 🎯 Use Cases

### 1. Thermal Management
**Question:** Is my GPU running too hot?

**Answer:**
- Compare idle temps (should be 30-50°C)
- Gaming temps (should be 60-85°C)
- If gaming temps > 85°C → check cooling

### 2. Power Efficiency
**Question:** How much power does gaming use?

**Answer:**
- See exact wattage distribution
- Calculate cost: kWh × electricity rate
- Optimize settings for efficiency

### 3. Performance Monitoring
**Question:** Is my GPU performing consistently?

**Answer:**
- Track clock speeds over time
- Detect thermal throttling (clocks dropping)
- Compare before/after driver updates

### 4. Hardware Health
**Question:** Is my GPU degrading?

**Answer:**
- Monitor temperature trends (increasing = bad thermal paste)
- Check power draw trends (increasing = efficiency loss)
- Track fan speed (increasing RPM = dust buildup)

---

## 💡 Advanced Tips

### Customize Thresholds

```python
# In automated_pipeline.py, modify detect_scenario():
def detect_scenario(self, records):
    avg_load = sum(loads) / len(loads)

    # Custom thresholds:
    if avg_load > 50:  # Heavy gaming
        return "heavy_gaming"
    elif avg_load > 20:  # Light gaming
        return "light_gaming"
    elif avg_load > 5:  # Video playback
        return "video"
    else:  # Idle
        return "idle"
```

### Export Data for Analysis

```python
# Export to CSV
from influxdb_client import InfluxDBClient
client = InfluxDBClient(url="http://localhost:8086", token="my-super-secret-auth-token", org="gpu-monitoring")

query = '''
from(bucket: "gpu-metrics")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "gpu_sessions")
'''

result = client.query_api().query_csv(query)
with open('export.csv', 'w') as f:
    f.write(result)
```

### Schedule Daily Reports

Create a script that emails you daily summaries:
```python
# daily_report.py
# - Query yesterday's data
# - Calculate statistics
# - Send email with summary
# - Schedule with Task Scheduler (daily at 9 AM)
```

---

## 📁 File Structure

```
gpu-monitoring-dashboard/
├── automated_pipeline.py          # Main pipeline script
├── pipeline_state.json            # State tracking
├── processed_logs/                # Archived GPU-Z logs
│   ├── archived_20251016_143120.txt
│   └── ...
├── grafana-idle-vs-gaming-dashboard.json  # Dashboard
├── AUTOMATION_GUIDE.md            # This file
└── setup_automated_monitoring.bat # Windows setup
```

---

## 🎉 Summary

You now have a **fully automated pipeline** that:

1. ✅ **Monitors** GPU-Z logs continuously
2. ✅ **Uploads** to S3 when threshold reached
3. ✅ **Processes** through AWS Lambda (serverless)
4. ✅ **Detects** idle vs gaming automatically
5. ✅ **Stores** in InfluxDB (time-series optimized)
6. ✅ **Aggregates** daily statistics
7. ✅ **Visualizes** in Grafana dashboards
8. ✅ **Cleans up** raw data (S3 + local)
9. ✅ **Costs $0.00/month** (AWS free tier)

**Just run it and forget it!** The system handles everything automatically.

---

## 🚀 Next Steps

1. **Test the pipeline:**
   ```bash
   python automated_pipeline.py
   ```

2. **Set up auto-start:**
   ```bash
   setup_automated_monitoring.bat
   ```

3. **Import Grafana dashboard:**
   - Go to Grafana
   - Import `grafana-idle-vs-gaming-dashboard.json`

4. **Let it run for a week** to collect data

5. **View your performance profile** in Grafana!

---

**Questions? Check the troubleshooting section or review logs in the console!**
