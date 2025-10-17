# How to Import the Pre-Built Dashboard

I've created a complete dashboard with 11 panels ready to import! Here's how:

## Method 1: Quick Import via UI (Easiest)

1. **Open Grafana** (should already be open at http://localhost:3000)
2. **Login** with `admin` / `admin`
3. Click **"Dashboards"** in the left sidebar (icon with 4 squares)
4. Click **"New"** → **"Import"**
5. Click **"Upload JSON file"**
6. Navigate to: `gpu-monitoring-dashboard\dashboard\gpu-monitoring-dashboard.json`
7. Click **"Load"**
8. Select **"InfluxDB"** as the data source
9. Click **"Import"**

**Done!** Your dashboard should now be live with all 11 panels!

## Method 2: Copy-Paste JSON

If file upload doesn't work:

1. Open the file: `gpu-monitoring-dashboard\dashboard\gpu-monitoring-dashboard.json`
2. Copy the entire contents (Ctrl+A, Ctrl+C)
3. In Grafana: **Dashboards** → **New** → **Import**
4. Paste the JSON in the text box
5. Click **"Load"**
6. Select **"InfluxDB"** as the data source
7. Click **"Import"**

## What You'll Get

The dashboard includes:

### Row 1: Temperature Monitoring
- **Panel 1:** GPU Temperature (time series) - Shows GPU temp and hot spot temp
- **Panel 2:** CPU Temperature (time series) - Tracks CPU temperature

### Row 2: Load and Power Gauges
- **Panel 3:** GPU Load (gauge) - Current GPU utilization 0-100%
- **Panel 4:** Power Draw (gauge) - Current power consumption
- **Panel 5:** Power Over Time (time series) - Historical power consumption

### Row 3: Memory and Clocks
- **Panel 6:** Memory Usage (time series) - GPU and system memory
- **Panel 7:** Clock Speeds (time series) - GPU and memory clock speeds

### Row 4: Quick Stats
- **Panel 8:** Current GPU Temp (stat) - Big number display
- **Panel 9:** Current GPU Load (stat) - Big number display
- **Panel 10:** Current Power Draw (stat) - Big number display
- **Panel 11:** Fan Speeds (time series) - Fan 1 and Fan 2 speeds

## Dashboard Features

✅ **Auto-refresh every 5 seconds** - Live data updates
✅ **5-minute time window** - Shows recent history
✅ **Color-coded thresholds** - Green/Yellow/Red based on values
✅ **Multi-metric panels** - Multiple metrics on same graph
✅ **Statistics in legends** - Shows last, max, mean values
✅ **Smooth line interpolation** - Clean, professional look

## Troubleshooting

### "No data" showing?

1. **Check InfluxDB datasource connection:**
   - Go to **Configuration** (gear icon) → **Data Sources**
   - Click on **InfluxDB**
   - Scroll down and click **"Save & Test"**
   - Should show green "Data source is working"

2. **Verify data is flowing:**
   ```bash
   tail -f gpu-monitoring-dashboard/kafka-producer/consumer.log
   ```
   You should see "Written X metrics to InfluxDB"

3. **Check time range:**
   - Make sure dashboard time range is set to "Last 5 minutes"
   - Click the time picker in top right

### Datasource not found?

If you get "datasource not found" error:

1. Go to **Configuration** → **Data Sources** → **Add data source**
2. Choose **InfluxDB**
3. Configure:
   - **Name:** InfluxDB
   - **Query Language:** Flux
   - **URL:** http://influxdb:8086
   - **Organization:** gpu-monitoring
   - **Token:** my-super-secret-auth-token
   - **Default Bucket:** gpu-metrics
4. Click **"Save & Test"**
5. Try importing the dashboard again

## Customize Your Dashboard

After importing, you can:

- **Resize panels** - Drag the corners
- **Move panels** - Drag by the title bar
- **Edit panels** - Click panel title → Edit
- **Add more panels** - Click "Add panel" button
- **Change colors** - Edit → Field tab → Color scheme
- **Add alerts** - Edit → Alert tab
- **Change refresh rate** - Top right dropdown

## All Available Metrics

You can add more panels using any of these metrics:

### Temperature
- `gpu_temperature`
- `hot_spot_temperature`
- `memory_temperature`
- `cpu_temperature`

### Performance
- `gpu_clock`
- `memory_clock`
- `gpu_load`
- `memory_controller_load`

### Power
- `board_power_draw`
- `gpu_chip_power_draw`
- `power_consumption_percent`

### Memory
- `gpu_memory_used`
- `system_memory_used`

### Cooling
- `fan1_speed_percent`
- `fan2_speed_percent`

### Electrical
- `gpu_voltage`

## Sample Query Template

To add a new panel:

```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "METRIC_NAME_HERE")
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
```

Replace `METRIC_NAME_HERE` with any metric from the list above.

---

**Enjoy your real-time GPU monitoring dashboard!** 🎉📊
