# 🎯 Final Steps - Import Your Dashboard (2 Minutes!)

## Current Status: ✅ Everything is Ready!

- ✅ **All Docker services running** (Kafka, Spark, Hadoop, InfluxDB, Grafana)
- ✅ **Kafka producer streaming** - Sending GPU-Z metrics
- ✅ **InfluxDB consumer writing** - 9,000+ metrics in database
- ✅ **Grafana open** at http://localhost:3000
- ✅ **Dashboard JSON created** with 11 pre-configured panels

## 📊 Just Import the Dashboard!

### Visual Step-by-Step Guide:

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Open Grafana (already done!)                        │
│ URL: http://localhost:3000                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 2: Login                                                │
│                                                              │
│   Username: admin                                            │
│   Password: admin                                            │
│                                                              │
│   [Skip changing password or set a new one]                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 3: Navigate to Import                                   │
│                                                              │
│   Look at LEFT SIDEBAR:                                      │
│   ┌─────┐                                                   │
│   │ ☰   │  <- Menu (top)                                   │
│   │ 🏠  │  <- Home                                          │
│   │ 📊  │  <- Dashboards (4 squares icon) <- CLICK HERE!   │
│   │ 🔍  │  <- Explore                                       │
│   │ ⚠️  │  <- Alerting                                      │
│   │ ⚙️  │  <- Configuration                                 │
│   └─────┘                                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 4: Start Import Process                                 │
│                                                              │
│   After clicking "Dashboards", you'll see:                   │
│                                                              │
│   [New ▼]  [Import]  [Folder]                              │
│                                                              │
│   Click: "New" button (blue, top right)                     │
│   Then: Select "Import" from dropdown                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 5: Upload JSON File                                     │
│                                                              │
│   You'll see "Import dashboard" page with options:          │
│                                                              │
│   Option 1: [Upload JSON file] <- CLICK THIS                │
│   Option 2: Import via grafana.com                          │
│   Option 3: Paste dashboard JSON                            │
│                                                              │
│   Browse to file:                                            │
│   gpu-monitoring-dashboard\dashboard\                        │
│       gpu-monitoring-dashboard.json                          │
│                                                              │
│   Select file and click "Open"                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 6: Configure Import                                     │
│                                                              │
│   After loading, you'll see:                                 │
│                                                              │
│   Dashboard Name: GPU Monitoring Dashboard                   │
│   Folder: [General]                                          │
│   UID: gpu-monitoring                                        │
│                                                              │
│   InfluxDB: [Select a datasource ▼]                         │
│              ↑                                               │
│              └─ IMPORTANT: Select "InfluxDB" here!          │
│                                                              │
│   [Import] <- CLICK THIS                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Step 7: SUCCESS! 🎉                                         │
│                                                              │
│   You should now see your dashboard with 11 panels:         │
│                                                              │
│   ┌──────────────┐ ┌──────────────┐                        │
│   │ GPU Temp     │ │ CPU Temp     │  <- Temperature graphs │
│   └──────────────┘ └──────────────┘                        │
│                                                              │
│   ┌────┐ ┌────┐ ┌──────────────┐                          │
│   │Load│ │Pwr │ │ Power Chart  │  <- Gauges & power       │
│   └────┘ └────┘ └──────────────┘                          │
│                                                              │
│   ┌──────────────┐ ┌──────────────┐                        │
│   │ Memory       │ │ Clocks       │  <- Memory & clocks    │
│   └──────────────┘ └──────────────┘                        │
│                                                              │
│   Plus: Stats & Fan Speed panels!                           │
│                                                              │
│   All panels auto-refresh every 5 seconds!                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 If InfluxDB Datasource Doesn't Appear:

### Quick Fix:

1. Click **Settings** (gear icon ⚙️) in left sidebar
2. Click **Data Sources**
3. Click **Add data source**
4. Search for "InfluxDB" and click it
5. Configure:
   ```
   Name:         InfluxDB
   Query Language: Flux
   URL:          http://influxdb:8086
   Organization: gpu-monitoring
   Token:        my-super-secret-auth-token
   Default Bucket: gpu-metrics
   ```
6. Click **Save & Test** (should show green success)
7. Go back to Dashboards > New > Import
8. Upload the JSON file again
9. Now InfluxDB should appear in the dropdown

## 📊 What You'll See:

### Your Live Dashboard Panels:

**Row 1:**
- 📈 GPU Temperature (with hot spot)
- 📈 CPU Temperature

**Row 2:**
- 🎯 GPU Load Gauge (0-100%)
- ⚡ Power Draw Gauge (watts)
- 📈 Power Consumption Over Time

**Row 3:**
- 💾 Memory Usage (GPU + System)
- ⚙️ Clock Speeds (GPU + Memory)

**Row 4:**
- 📊 Current GPU Temp (big number)
- 📊 Current GPU Load (big number)
- 📊 Current Power (big number)
- 🌀 Fan Speeds Chart

### Features:
- ⏱️ **Auto-refresh:** 5 seconds
- 📅 **Time window:** Last 5 minutes
- 🎨 **Color coding:** Green/Yellow/Red thresholds
- 📊 **Statistics:** Last, Max, Mean values in legends

## 💡 Tips:

### Navigate Dashboard:
- **Pan:** Click and drag
- **Zoom:** Time range selector (top right)
- **Resize panels:** Drag panel corners
- **Move panels:** Drag panel title

### Customize:
- **Edit panel:** Click panel title > Edit
- **Change time range:** Top right time picker
- **Adjust refresh rate:** Top right dropdown (5s, 10s, 30s, etc.)
- **Full screen:** Click panel title > View

### Save Changes:
- Click **💾 Save dashboard** (top toolbar)
- Add optional comment
- Click **Save**

## 🐛 Troubleshooting:

### No Data in Panels?

**Check 1:** Verify consumer is running
```bash
tail -f gpu-monitoring-dashboard/kafka-producer/consumer.log
```
Should see: "Written X metrics to InfluxDB"

**Check 2:** Test datasource connection
- Settings > Data Sources > InfluxDB > Save & Test
- Should show green "✓ Data source is working"

**Check 3:** Verify time range
- Make sure it's set to "Last 5 minutes" or wider
- Click time picker (top right)

**Check 4:** Refresh browser
- Press F5 or Ctrl+R

### Panels Show "N/A"?

- Wait 10-20 seconds for data to populate
- Check if producer/consumer are still running
- Verify InfluxDB datasource is selected

### Dashboard Looks Different?

- Make sure you uploaded the correct JSON file
- Check that InfluxDB was selected during import
- Try re-importing the dashboard

## 📁 File Location:

The JSON file you need to upload is at:

```
C:\Users\dmitr\Documents\projects\gpu-monitoring-dashboard\
    dashboard\
        gpu-monitoring-dashboard.json
```

Or navigate in File Explorer:
1. Open File Explorer
2. Navigate to: Documents > projects > gpu-monitoring-dashboard > dashboard
3. Select: gpu-monitoring-dashboard.json

## 🎉 That's It!

Once imported, you'll have a beautiful real-time monitoring dashboard showing:
- Your GPU temperatures, loads, and power consumption
- CPU temperature trends
- Memory usage patterns
- Clock speeds
- Fan speeds

All updating live every 5 seconds with data from your GPU-Z logs!

---

## 📚 Additional Resources:

- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete visual guide
- **[QUICKSTART.md](QUICKSTART.md)** - Initial setup guide
- **[README.md](README.md)** - Full documentation
- **[IMPORT_DASHBOARD.md](IMPORT_DASHBOARD.md)** - Import instructions

---

**Need help?** All the documentation is in the project folder!

**Enjoying the dashboard?** Try adding custom panels with the query templates in [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)!

🚀 **Happy Monitoring!** 📊
