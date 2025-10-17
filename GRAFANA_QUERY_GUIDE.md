# Grafana Query Guide - InfluxDB 2.x

## ✅ Quick Fix for "Bad Request (400)" Error

The error happens because you're using the SQL-style query builder, but InfluxDB 2.x requires **Flux** query language.

### Step 1: Switch to Flux Query Mode

1. In the Grafana Explore view, look at the query builder
2. Find the **query language selector** (usually near the top of the query panel)
3. Click where it might say "Builder" or show a toggle
4. Switch to **"Code"** or **"Flux"** mode

OR

1. Click the **pencil icon** (✏️) or **"Edit"** button near the query
2. This should give you a text editor to write Flux queries directly

### Step 2: Use This Flux Query

Once in Flux/Code mode, paste this query:

```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) => r._field == "gpu_temperature")
```

### Step 3: Run Query

Click the **"Run query"** button or press **Ctrl+Enter**

---

## 📊 Sample Queries for Different Metrics

### GPU Temperature
```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) => r._field == "gpu_temperature")
```

### Power Draw
```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) => r._field == "board_power_draw")
```

### GPU Load %
```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) => r._field == "gpu_load")
```

### Multiple Metrics (Temperature + Power)
```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) =>
    r._field == "gpu_temperature" or
    r._field == "cpu_temperature" or
    r._field == "board_power_draw"
  )
```

### All Available Fields (See What You Have)
```flux
from(bucket: "gpu-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> limit(n: 100)
```

---

## 🎯 Available Fields in Your Data

Based on the loaded data, you have these fields:

**Temperature:**
- `gpu_temperature`
- `cpu_temperature`
- `hot_spot`
- `memory_temperature`

**Clock Speeds:**
- `gpu_clock`
- `memory_clock`

**Load/Usage:**
- `gpu_load`
- `memory_controller_load`
- `video_engine_load`
- `bus_interface_load`

**Power:**
- `board_power_draw`
- `gpu_chip_power_draw`
- `mvddc_power_draw`
- `pwr_src_power_draw`
- `pcie_slot_power`
- `8-pin_1_power`
- `8-pin_2_power`
- `8-pin_3_power`
- `power_consumption_pct`

**Memory:**
- `memory_used`
- `system_memory_used`

**Voltage:**
- `gpu_voltage`
- `pwr_src_voltage`
- `pcie_slot_voltage`
- `8-pin_1_voltage`
- `8-pin_2_voltage`
- `8-pin_3_voltage`

**Fans:**
- `fan_1_speed_pct`
- `fan_1_speed_rpm`
- `fan_2_speed_pct`
- `fan_2_speed_rpm`

**Other:**
- `perfcap_reason`

---

## 🔍 If You Still Can't Find Flux Mode

Try this alternative approach:

1. **Close the Explore tab**
2. **Go to Dashboards** → **New Dashboard**
3. **Add a new panel**
4. **Select InfluxDB as datasource**
5. In the query editor, look for a **toggle button** or **dropdown** that says:
   - "Builder" → switch to "Code"
   - "InfluxQL" → switch to "Flux"

The toggle is usually in the top-right area of the query editor section.

---

## 💡 Alternative: Check InfluxDB Datasource Settings

If nothing works, the datasource might be misconfigured:

1. Go to **Configuration** (⚙️) → **Data Sources**
2. Click on **InfluxDB**
3. Check that:
   - **Query Language**: Flux
   - **Organization**: gpu-monitoring
   - **Default Bucket**: gpu-metrics
   - **Token**: (should be set)
4. Click **"Save & Test"** at the bottom

---

## 🎨 Create Your First Dashboard

Once you have a working query:

1. Click **"Add to dashboard"** button (top right)
2. Choose **"Add new panel"** or **"Apply"**
3. Customize the visualization:
   - Change graph type (Line, Gauge, Bar, etc.)
   - Set title
   - Configure thresholds
   - Add more queries for multiple metrics

---

## 📞 Need Help?

If you're still seeing the error, take a screenshot showing:
1. The full query editor area
2. Any buttons/toggles visible
3. The error message

Then I can give you more specific instructions!
