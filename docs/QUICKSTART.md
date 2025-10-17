# Quick Start Guide

Get your GPU monitoring dashboard up and running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Python 3.8+
- Your GPU-Z log file

## Step 1: Start Services (2 minutes)

### Windows:
```cmd
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

Wait for all services to start. You should see green checkmarks.

## Step 2: Copy Your GPU-Z Log (30 seconds)

```bash
# Windows
copy "GPU-Z Sensor Log.txt" data\

# Linux/Mac
cp "GPU-Z Sensor Log.txt" data/
```

Or just copy it using your file explorer to the `data/` folder.

## Step 3: Install Python Dependencies (1 minute)

```bash
cd kafka-producer
pip install -r requirements.txt
```

## Step 4: Start Data Pipeline (1 minute)

Open **3 separate terminals/command prompts**:

### Terminal 1 - Kafka Producer:
```bash
cd kafka-producer
python gpuz_producer.py --file "../data/GPU-Z Sensor Log.txt" --speed 2.0 --loop
```

(Using `--speed 2.0` to replay 2x faster. Use `1.0` for real-time)

### Terminal 2 - InfluxDB Consumer:
```bash
cd kafka-producer
python influxdb_consumer.py
```

You should see messages like:
```
INFO - Written 10 metrics to InfluxDB
INFO - Written 20 metrics to InfluxDB
...
```

### Terminal 3 - Spark Streaming (Optional - for HDFS storage):
```bash
docker exec -it spark-master /bin/bash
cd /opt/spark-jobs
pip install -r requirements.txt
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 streaming_processor.py
```

## Step 5: Create Grafana Dashboard (1 minute)

1. Open http://localhost:3000
2. Login with `admin` / `admin` (change password when prompted, or skip)
3. Click **☰** menu → **Dashboards** → **New** → **New Dashboard**
4. Click **Add visualization**
5. Select **InfluxDB** as data source
6. Use this query for GPU Temperature:

```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_temperature")
```

7. Click **Apply**
8. Add more panels for other metrics!

## Ready-Made Panels

### Panel 1: GPU Temperature
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_temperature" or r["_field"] == "hot_spot_temperature")
```
**Visualization**: Time series
**Y-Axis Unit**: Celsius (°C)

### Panel 2: CPU Temperature
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "cpu_temperature")
```
**Visualization**: Time series
**Y-Axis Unit**: Celsius (°C)

### Panel 3: GPU Load
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_load")
```
**Visualization**: Gauge
**Unit**: Percent (0-100)
**Thresholds**: Green (0-70), Yellow (70-90), Red (90-100)

### Panel 4: Power Consumption
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "board_power_draw")
```
**Visualization**: Time series
**Y-Axis Unit**: Watt (W)

### Panel 5: Memory Usage
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_memory_used" or r["_field"] == "system_memory_used")
```
**Visualization**: Time series
**Y-Axis Unit**: Megabytes (MB)

### Panel 6: Clock Speeds
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_clock" or r["_field"] == "memory_clock")
```
**Visualization**: Time series
**Y-Axis Unit**: MHz

## Troubleshooting

### "No data" in Grafana?

1. Check Terminal 2 - is the consumer running and showing "Written X metrics"?
2. Check InfluxDB has data:
   - Go to http://localhost:8086
   - Login: admin / adminpassword
   - Click "Data Explorer" (left sidebar)
   - Select bucket "gpu-metrics"
   - You should see data

3. Check Grafana time range - set it to "Last 5 minutes" or "Last 15 minutes"

### Producer says "Failed to connect to Kafka"?

Wait a bit longer (Kafka takes ~30 seconds to fully start), then try again.

### Services won't start?

Check Docker Desktop is running and you have enough RAM allocated (8GB recommended).

```bash
docker-compose logs kafka
docker-compose logs influxdb
```

## What's Next?

Once you see data flowing in Grafana:

1. **Add alerts** - Set up Grafana alerts for high temps
2. **Run batch analytics** - Analyze historical patterns
3. **Customize thresholds** - Adjust anomaly detection thresholds
4. **Add more metrics** - Extend the dashboard with more panels

## Stopping Everything

```bash
# Stop services
docker-compose down

# Stop Python scripts
# Press Ctrl+C in each terminal
```

## Need Help?

Check the full [README.md](README.md) for detailed documentation!

---

**Happy Monitoring!** 🚀
