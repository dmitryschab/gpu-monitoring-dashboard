# Complete Dashboard Setup Guide

## 🎯 Quick Import (2 Minutes)

Your Grafana is open at **http://localhost:3000** - Now let's import the pre-built dashboard!

### Step 1: Login
- Username: `admin`
- Password: `admin`
- (Skip changing password or set a new one)

### Step 2: Import Dashboard
1. Look at the **left sidebar** - click the icon that looks like **4 squares** (Dashboards)
2. Click **"New"** button (top right)
3. Click **"Import"** from the dropdown
4. Click **"Upload JSON file"**
5. Browse to: `gpu-monitoring-dashboard\dashboard\gpu-monitoring-dashboard.json`
6. Click **"Load"**
7. In the dropdown that says "Select a datasource", choose **"InfluxDB"**
8. Click **"Import"** button at the bottom

### Step 3: Enjoy!
Your dashboard is now live with **11 panels** showing real-time GPU/CPU metrics!

---

## 📊 What You'll See

### Panel Layout (3 Rows x 11 Panels):

#### **Row 1: Temperature Monitoring** (Top row)
```
┌──────────────────────────┐ ┌──────────────────────────┐
│ GPU Temperature          │ │ CPU Temperature          │
│ (Time Series)            │ │ (Time Series)            │
│                          │ │                          │
│ Red line:    GPU Temp    │ │ Blue line:   CPU Temp    │
│ Orange line: Hot Spot    │ │                          │
│                          │ │ Shows: Last & Max values │
│ Shows: Last & Max values │ │                          │
└──────────────────────────┘ └──────────────────────────┘
```

#### **Row 2: Load, Power & History** (Middle row)
```
┌─────────┐ ┌─────────┐ ┌──────────────────────────┐
│ GPU Load│ │  Power  │ │ Power Over Time          │
│ (Gauge) │ │ (Gauge) │ │ (Time Series)            │
│         │ │         │ │                          │
│ 0-100%  │ │  Watts  │ │ Historical power draw    │
│ Green   │ │ Yellow  │ │ Shows: Mean & Max        │
│ Yellow  │ │ Red at  │ │                          │
│ Red at  │ │ >350W   │ │                          │
│  >90%   │ │         │ │                          │
└─────────┘ └─────────┘ └──────────────────────────┘
```

#### **Row 3: Memory & Clocks**
```
┌──────────────────────────┐ ┌──────────────────────────┐
│ Memory Usage             │ │ Clock Speeds             │
│ (Time Series)            │ │ (Time Series)            │
│                          │ │                          │
│ Purple: GPU Memory       │ │ Blue: GPU Clock          │
│ Green:  System Memory    │ │ Purple: Memory Clock     │
│                          │ │                          │
│ Shows: Last & Max (MB)   │ │ Shows: Mean & Last (MHz) │
└──────────────────────────┘ └──────────────────────────┘
```

#### **Row 4: Quick Stats & Fans** (Bottom row)
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────────────┐
│ Current │ │ Current │ │ Current │ │ Fan Speeds               │
│GPU Temp │ │GPU Load │ │  Power  │ │ (Time Series)            │
│ (Stat)  │ │ (Stat)  │ │ (Stat)  │ │                          │
│         │ │         │ │         │ │ Green: Fan 1             │
│ Big #   │ │ Big #   │ │ Big #   │ │ Blue:  Fan 2             │
│  °C     │ │   %     │ │   W     │ │                          │
│         │ │         │ │         │ │ Shows: Mean & Max        │
└─────────┘ └─────────┘ └─────────┘ └──────────────────────────┘
```

---

## 🎨 Dashboard Features

### Auto-Refresh
- Dashboard refreshes **every 5 seconds** automatically
- See the dropdown in top-right corner (shows "5s")
- Can change to 10s, 30s, 1m, etc.

### Time Range
- Default: **Last 5 minutes** of data
- Click the time picker (top-right, next to refresh dropdown)
- Options: Last 15m, Last 30m, Last 1h, Last 6h, Last 24h
- Or set custom range

### Color Coding
- **Green**: Normal operation
- **Yellow**: Getting warm/high load
- **Red**: High temperature/load/power (threshold exceeded)

### Legends
Each time-series panel shows:
- **Last**: Most recent value
- **Max**: Highest value in time range
- **Mean**: Average value

### Smooth Lines
- All graphs use smooth line interpolation
- No jagged edges - professional look
- Points are hidden for cleaner view

---

## 🔧 Customization Options

### Resize Panels
- Hover over panel corner
- When cursor changes to ↔️, drag to resize

### Move Panels
- Click and hold panel title bar
- Drag to new position
- Dashboard auto-saves

### Edit Panel
1. Click panel title
2. Select "Edit" from dropdown
3. Modify:
   - Query (change metric)
   - Visualization type (line, bar, gauge, etc.)
   - Colors and thresholds
   - Units and decimals
   - Legend position

### Add More Panels
- Click **"Add panel"** button (top toolbar)
- Select "Add a new panel"
- Choose visualization
- Write Flux query (see templates below)

---

## 📝 Query Templates

### Basic Query Pattern
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "METRIC_NAME")
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
```

### Available Metrics

**Temperature:**
- `gpu_temperature` - GPU core temp
- `hot_spot_temperature` - Hottest point on GPU
- `memory_temperature` - VRAM temp
- `cpu_temperature` - CPU temp

**Performance:**
- `gpu_clock` - GPU frequency (MHz)
- `memory_clock` - Memory frequency (MHz)
- `gpu_load` - GPU utilization (%)
- `memory_controller_load` - Memory controller usage (%)

**Power:**
- `board_power_draw` - Total board power (W)
- `gpu_chip_power_draw` - GPU chip only (W)
- `power_consumption_percent` - % of TDP

**Memory:**
- `gpu_memory_used` - VRAM used (MB)
- `system_memory_used` - RAM used (MB)

**Cooling:**
- `fan1_speed_percent` - Fan 1 speed (%)
- `fan2_speed_percent` - Fan 2 speed (%)

**Electrical:**
- `gpu_voltage` - GPU voltage (V)

### Multi-Metric Query
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) =>
      r["_field"] == "gpu_temperature" or
      r["_field"] == "cpu_temperature"
  )
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
```

### Latest Value Only (for Gauges/Stats)
```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_load")
  |> last()
```

---

## 🚨 Alerts (Optional Setup)

### Create Alert Rules
1. Edit any panel
2. Go to **"Alert"** tab
3. Click **"Create alert rule from this panel"**
4. Set conditions:
   - **Threshold**: e.g., Temperature > 85°C
   - **Evaluation interval**: How often to check (30s, 1m, etc.)
   - **For duration**: How long condition must be true (1m, 5m, etc.)

### Alert Channels
Configure where alerts go:
- **Email**: Get emails for alerts
- **Slack**: Post to Slack channel
- **Discord**: Send to Discord webhook
- **Webhook**: Custom HTTP endpoint

### Example Alert: High GPU Temperature
```
Condition: WHEN last() OF gpu_temperature IS ABOVE 85
Evaluate: Every 30s FOR 1m
```

---

## 📊 Dashboard Tips

### Best Practices
1. **Keep time range reasonable** - 5-15 minutes for real-time monitoring
2. **Use auto-refresh** - 5s for active monitoring, 30s for passive
3. **Organize panels logically** - Group related metrics
4. **Use color coding** - Make thresholds meaningful
5. **Show legends** - Users need context

### Performance
- Shorter time ranges = faster queries
- Fewer panels = less load
- Aggregate data for long time ranges

### Sharing
- **Snapshot**: Share static view
  - Click share icon → Snapshot
- **Export JSON**: Backup dashboard
  - Settings (gear icon) → JSON Model → Copy
- **Link**: Direct URL to dashboard
  - Just copy browser URL

---

## 🐛 Troubleshooting

### No Data Showing?

**Check 1: Is data flowing?**
```bash
tail -f gpu-monitoring-dashboard/kafka-producer/consumer.log
```
Should see: "Written X metrics to InfluxDB"

**Check 2: Test InfluxDB connection**
1. Go to Settings (gear icon) → Data Sources
2. Click "InfluxDB"
3. Scroll down → "Save & Test"
4. Should show green "Data source is working"

**Check 3: Verify query**
- Edit panel
- Check query syntax
- Make sure field names match exactly
- Try simpler query first

**Check 4: Time range**
- Make sure time range covers your data
- Try "Last 15 minutes" or "Last 1 hour"

### Slow Dashboard?

**Solutions:**
1. Reduce refresh rate (30s instead of 5s)
2. Shorter time range (5m instead of 1h)
3. Remove unused panels
4. Use `aggregateWindow` in queries

### Panel Shows "N/A"?

- Metric name might be wrong
- No data in time range
- Query syntax error
- Check browser console (F12) for errors

---

## 📚 Learn More

### Grafana Docs
- [Grafana Documentation](https://grafana.com/docs/)
- [Flux Query Language](https://docs.influxdata.com/flux/)
- [Panel Options](https://grafana.com/docs/grafana/latest/panels-visualizations/)

### Video Tutorials
- Search "Grafana tutorial" on YouTube
- Official Grafana channel has great content

### Community
- [Grafana Community Forums](https://community.grafana.com/)
- [InfluxDB Community](https://community.influxdata.com/)

---

## 🎉 You're All Set!

Your GPU monitoring dashboard is now live with:
- ✅ 11 pre-configured panels
- ✅ Real-time data updates (5s refresh)
- ✅ 5-minute rolling window
- ✅ Color-coded thresholds
- ✅ Professional visualizations

**Enjoy monitoring your GPU/CPU in real-time!** 📊🚀

---

*Need help? Check [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)*
