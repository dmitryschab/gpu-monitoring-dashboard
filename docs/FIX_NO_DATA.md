# 🔧 Fix "No Data" Issue - Quick Solution

## Problem
Your dashboard imported successfully but shows "No data" in all panels.

## Cause
The dashboard panels are using a placeholder datasource UID that doesn't match your actual InfluxDB datasource UID.

## ✅ Solution (2 Options)

---

### Option 1: Re-import Fixed Dashboard (Recommended - 1 minute)

I've created a fixed version with the correct datasource UID!

**Steps:**

1. **In Grafana, delete the current dashboard:**
   - Click the gear icon (⚙️) at the top of your dashboard
   - Scroll down to "Delete dashboard"
   - Click "Delete" and confirm

2. **Import the fixed dashboard:**
   - Click **Dashboards** (left sidebar)
   - Click **New** → **Import**
   - Click **Upload JSON file**
   - Select: `dashboard\gpu-monitoring-dashboard-fixed.json` ⭐ (NEW FILE!)
   - Click **Load**
   - Click **Import** (datasource should auto-select)

3. **Refresh the page (F5)**

**DONE!** All panels should now show live data! 🎉

---

### Option 2: Manually Edit Each Panel (5 minutes)

If you want to keep the current dashboard:

**For EACH panel (11 panels total):**

1. Click the panel title
2. Select **Edit**
3. At the bottom of the query section, you'll see a datasource dropdown
4. Change from `influxdb` → **InfluxDB** (the one with the green dot)
5. Click **Apply** (top right)
6. Repeat for all 11 panels

**OR use this faster method:**

1. Click the gear icon (⚙️) at top to open Dashboard Settings
2. Click **JSON Model** (left sidebar)
3. Press **Ctrl+H** (Find and Replace)
4. Find: `"uid": "influxdb"`
5. Replace with: `"uid": "P951FEA4DE68E13C5"`
6. Click **Replace All**
7. Click **Save changes** at the bottom
8. Click **Save dashboard** (top right)
9. Go back to the dashboard view

---

## Verify It's Working

After either fix, you should see:

✅ **GPU Temperature** - Red and orange lines with data
✅ **CPU Temperature** - Blue line showing CPU temp
✅ **GPU Load** - Gauge showing 0-100%
✅ **Power Draw** - Gauge showing wattage
✅ **All other panels** - Showing live metrics

**Auto-refresh every 5 seconds!**

---

## Current System Status

- ✅ **InfluxDB**: Working perfectly (12,330+ metrics stored)
- ✅ **Datasource**: Connected and tested (3 buckets found)
- ✅ **Data flow**: Active (producer & consumer running)
- ⚠️ **Dashboard panels**: Need correct datasource UID

**Everything is working except the panel datasource references!**

---

## Files

**Use this file for re-import:**
```
gpu-monitoring-dashboard\dashboard\gpu-monitoring-dashboard-fixed.json
```

**Backup of original:**
```
gpu-monitoring-dashboard\dashboard\gpu-monitoring-dashboard-backup.json
```

---

## Quick Test Query

Want to test if data is really there? Edit any panel and paste this query:

```flux
from(bucket: "gpu-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "gpu_temperature")
```

Change datasource to **InfluxDB** and you should see data!

---

## Need Help?

**Check data is flowing:**
```bash
tail -f gpu-monitoring-dashboard/kafka-producer/consumer.log
```

Should show: "Written X metrics to InfluxDB" increasing every 2 seconds.

**Check datasource:**
- Go to: Settings (⚙️) → Data Sources → InfluxDB
- Click "Save & Test"
- Should show: "✓ datasource is working. 3 buckets found"

---

## Summary

**Quick Fix:** Just re-import `gpu-monitoring-dashboard-fixed.json` and you're done! 🚀

All your data is there - we just need to point the panels to the right datasource!
