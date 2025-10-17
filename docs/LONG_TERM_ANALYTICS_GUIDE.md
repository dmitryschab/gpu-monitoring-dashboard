# 📊 Long-Term Analytics Dashboard Guide

## Overview

This dashboard provides **statistical analysis and distributions** of your GPU metrics over a 12-hour period. Perfect for understanding usage patterns, identifying idle vs. gaming loads, and analyzing temperature distributions.

**Auto-refreshes:** Every 12 hours (configurable)

---

## 🎯 Dashboard Panels (11 Total)

### Row 1: Distribution Histograms

#### **Panel 1: GPU Temperature Distribution**
- **Type:** Histogram (bar chart)
- **Purpose:** Shows how often your GPU runs at different temperature ranges
- **Bins:** 30°C to 90°C in 5°C increments
- **Use Case:**
  - Identify your most common operating temperature
  - See if GPU stays mostly cool (30-50°C) = idle
  - Or runs hot (60-80°C) = gaming/load

**What to look for:**
- Tall bar at 30-40°C = Mostly idle
- Tall bar at 60-70°C = Moderate gaming
- Tall bar at 75-85°C = Heavy gaming/rendering

#### **Panel 2: GPU Load Distribution**
- **Type:** Histogram (bar chart)
- **Purpose:** Shows distribution of GPU utilization
- **Bins:** 0% to 100% in 10% increments
- **Use Case:**
  - Understand workload patterns
  - See if GPU is mostly idle (0-10%)
  - Or under constant load (70-100%)

**What to look for:**
- Tall bar at 0-10% = Desktop/idle work
- Spread across 50-100% = Gaming/rendering
- Two peaks = Mixed usage (idle + gaming)

---

### Row 2: Statistical Analysis Tables

#### **Panel 3: GPU Temperature Percentiles**
- **Type:** Table
- **Metrics:**
  - **Min:** Lowest temperature (idle temp)
  - **P50 (Median):** Middle value - 50% below, 50% above
  - **Mean:** Average temperature
  - **P95:** 95% of time, temp is below this (excludes spikes)
  - **P99:** 99% of time, temp is below this
  - **Max:** Highest temperature reached

**How to interpret:**
```
Example:
Min: 35°C  → Idle temp
P50: 45°C  → Half the time below 45°C = mostly light usage
Mean: 52°C → Average temp
P95: 75°C  → Gaming temp (spends <5% above this)
Max: 82°C  → Peak during heavy gaming
```

#### **Panel 4: Power Draw Percentiles**
- **Type:** Table
- **Same percentile breakdown** but for power consumption
- **Use Case:** Understand power consumption patterns

**How to interpret:**
```
Example:
Min: 50W   → Idle power
P50: 115W  → Typical power
Mean: 145W → Average consumption
P95: 280W  → Gaming power
Max: 320W  → Peak power
```

#### **Panel 5: GPU Load Percentiles**
- **Type:** Table
- **Use Case:** Statistical breakdown of GPU utilization

---

### Row 3: Trend Analysis

#### **Panel 6: Temperature Trends (10min averages)**
- **Type:** Time series
- **Purpose:** Shows GPU and CPU temperature trends over 12 hours
- **Aggregation:** 10-minute moving averages (smooths data)
- **Use Case:**
  - Identify when you game vs. idle
  - See thermal patterns throughout the day
  - Spot thermal throttling (temp plateaus)

**What to look for:**
- Flat low temps = Idle periods
- Sharp spikes = Gaming sessions
- Gradual rise = Sustained workload (rendering)

#### **Panel 7: Power Draw Trends (10min averages)**
- **Type:** Time series
- **Purpose:** Power consumption trends over time
- **Use Case:**
  - Correlate with temperature trends
  - Identify power-hungry workloads
  - Estimate electricity cost

---

### Row 4: Workload Classification

#### **Panel 8: Time in Idle (<10% load)**
- **Type:** Stat (percentage)
- **Purpose:** Shows what % of time GPU is idle
- **Formula:** `(time_at_<10%_load / total_time) × 100`

**Color coding:**
- Green: >70% idle (light usage)
- Yellow: 20-70% idle (mixed usage)
- Red: <20% idle (heavy usage)

**Example:**
```
85% = Mostly desktop work, occasional gaming
45% = Balanced mix of idle and gaming
15% = Heavy gaming or constant rendering
```

#### **Panel 9: Time Under Load (>70%)**
- **Type:** Stat (percentage)
- **Purpose:** Shows what % of time GPU is heavily utilized
- **Formula:** `(time_at_>70%_load / total_time) × 100`

**Color coding:**
- Green: <10% (light gamer)
- Yellow: 10-30% (moderate gamer)
- Red: >30% (heavy gamer/workstation)

**Example:**
```
5% = Casual gaming, mostly desktop work
25% = Regular gaming sessions
60% = Streamer/content creator/heavy gaming
```

#### **Panel 10: Average GPU Temp (12h)**
- **Type:** Stat (°C)
- **Purpose:** Overall average temperature
- **Use Case:** Quick health check

**Color coding:**
- Green: <20°C (impossible - check sensors!)
- Yellow: 20-50°C (good - mostly idle)
- Orange: 50-80°C (normal - gaming/work)
- Red: >80°C (hot - heavy load or cooling issue)

#### **Panel 11: Average Power Draw (12h)**
- **Type:** Stat (watts)
- **Purpose:** Overall average power consumption
- **Use Case:** Estimate electricity usage

**Color coding:**
- Green: <150W (light usage)
- Yellow: 150-250W (moderate gaming)
- Red: >250W (heavy gaming/workstation)

---

## 🎓 How to Use This Dashboard

### Scenario 1: Understand Your Usage Patterns

**Steps:**
1. Look at **GPU Load Distribution** (Panel 2)
   - Two peaks? You have distinct idle and gaming modes
   - One peak at 0-10%? Mostly idle
   - Spread across 50-100%? Heavy user

2. Check **Time in Idle vs. Time Under Load** (Panels 8 & 9)
   - Calculate: Idle% + Load% + (100-both) = Medium usage
   - This tells you your usage balance

3. Review **Temperature Distribution** (Panel 1)
   - Should correlate with load distribution
   - High load = higher temps

### Scenario 2: Identify Thermal Issues

**Steps:**
1. Look at **GPU Temperature Percentiles** (Panel 3)
   - P95 > 85°C? You're running hot under load
   - Max > 90°C? Possible thermal throttling

2. Check **Temperature Trends** (Panel 6)
   - Look for flat tops (plateaus) = thermal throttling
   - Consistent high temps = cooling issue

3. Compare **Idle (P50) vs. Load (P95) temps**
   - Should be 20-40°C difference
   - Small difference = always hot (cooling problem)

### Scenario 3: Optimize Power Settings

**Steps:**
1. Check **Power Draw Percentiles** (Panel 4)
   - P50 too high? GPU not idling properly
   - Mean much lower than P95? Good power management

2. Review **Power Trends** (Panel 7)
   - Correlate with gaming sessions
   - Identify power-hungry games

3. Calculate daily cost:
   ```
   kWh = (Avg Power Draw / 1000) × 24 hours
   Daily Cost = kWh × Your electricity rate

   Example:
   150W average × 24h = 3.6 kWh
   At $0.12/kWh = $0.43 per day = $13/month
   ```

### Scenario 4: Compare Idle vs. Gaming

**Look at percentiles to understand each mode:**

**Idle Mode (desktop work):**
- GPU Load: P50 should be 0-10%
- GPU Temp: P50 should be 35-45°C
- Power: P50 should be 50-100W

**Gaming Mode (heavy load):**
- GPU Load: P95 should be 70-100%
- GPU Temp: P95 should be 60-80°C
- Power: P95 should be 200-350W

**Your P50 vs. P95 tells the story:**
- Large gap = Distinct idle and gaming periods
- Small gap = Consistent usage pattern

---

## 📈 Advanced Analysis

### Identify Game Types

**By looking at distributions, you can categorize games:**

**Esports (Low Load):**
- Load: 30-50% (GPU not maxed)
- Temp: 50-65°C
- Power: 100-150W
- Examples: CS:GO, Valorant, League of Legends

**AAA Games (High Load):**
- Load: 80-100% (GPU maxed)
- Temp: 70-85°C
- Power: 250-350W
- Examples: Cyberpunk, Red Dead Redemption 2

**Streaming/Recording:**
- Load: Consistent 60-80%
- Temp: Sustained 70-75°C
- Power: Steady 200-250W

### Seasonal Analysis

**Run this dashboard in different seasons:**
- **Summer:** Higher temps (ambient temp affects GPU)
- **Winter:** Lower temps
- Track **P50 and P95 temps** across seasons
- Expect 5-10°C difference

### Before/After Upgrades

**Capture metrics before changes:**
1. Take screenshot of percentiles
2. Make change (new cooler, thermal paste, fan curve)
3. Wait 24 hours
4. Compare new percentiles

**What to expect:**
- New cooler: 5-15°C drop in P95
- Thermal paste: 2-8°C drop
- Fan curve: 3-10°C drop, louder fans

---

## 🔧 Customization

### Change Time Range

Currently set to **12 hours**, but you can modify:

1. Click **gear icon** (⚙️) → **Dashboard settings**
2. Click **JSON Model**
3. Find and replace:
   ```json
   "range(start: -12h)"
   ```
   With:
   - `-24h` for 24 hours
   - `-7d` for 7 days
   - `-30d` for 30 days

4. Also update refresh interval:
   ```json
   "refresh": "12h"
   ```
   To:
   - `"24h"` for daily refresh
   - `"1d"` for daily refresh (same as above)
   - `"manual"` for manual only

### Adjust Histogram Bins

**Temperature bins** (currently 30-90°C in 5°C steps):

Edit Panel 1 query, change:
```flux
histogram(bins: [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0])
```

To finer granularity (2.5°C steps):
```flux
histogram(bins: [30.0, 32.5, 35.0, 37.5, 40.0, 42.5, 45.0, ..., 90.0])
```

Or wider buckets (10°C steps):
```flux
histogram(bins: [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0])
```

### Add More Percentiles

Want P75, P90? Edit table query:
```flux
p75 = data |> quantile(q: 0.75) |> findRecord(fn: (key) => true, idx: 0)
p90 = data |> quantile(q: 0.90) |> findRecord(fn: (key) => true, idx: 0)

// Add to array:
{_time: now(), metric: "P75", value: p75._value},
{_time: now(), metric: "P90", value: p90._value},
```

---

## 🎯 Key Insights to Track

### Daily Monitoring

**Check these metrics every day:**
1. **Average GPU Temp** - Should be consistent ±3°C
2. **Time in Idle %** - Know your usage balance
3. **P95 Temperature** - Your "gaming temperature"

### Weekly Monitoring

**Track trends over 7 days:**
1. **Temperature Distributions** - Look for shifts
2. **Power Trends** - Identify new power-hungry games
3. **Load Distribution** - Has usage pattern changed?

### Monthly Monitoring

**Compare month-over-month:**
1. Take screenshots of all percentile tables
2. Compare P50, P95, Max values
3. Look for degradation (higher temps over time = dust buildup)

---

## 🚨 Warning Signs

### Red Flags in Data

**Temperature Red Flags:**
- P95 > 85°C = Running too hot
- Max > 95°C = Critical, thermal throttling
- P50 > 55°C = Not idling properly (driver issue or app in background)

**Power Red Flags:**
- P50 > 150W = Not idling (check background apps)
- Max > 400W = Beyond TDP (check power limit)

**Load Red Flags:**
- P50 > 30% = Background app using GPU
- Always 100% = Stuck in performance mode or crypto mining malware

---

## 📊 Export Data

### Save Percentile Tables

1. Click table panel → **Inspect** → **Data**
2. Click **Download CSV**
3. Import to Excel/Google Sheets for tracking

### Track Over Time

**Create a tracking spreadsheet:**
| Date | P50 Temp | P95 Temp | Avg Power | Gaming Time % |
|------|----------|----------|-----------|---------------|
| 2025-10-12 | 45°C | 75°C | 145W | 25% |
| 2025-10-19 | 47°C | 76°C | 148W | 28% |

---

## 💡 Pro Tips

1. **Run overnight** - Let dashboard collect data for full 12 hours
2. **Compare weekday vs. weekend** - Usage patterns differ
3. **Track before/after game patches** - Some patches increase GPU load
4. **Seasonal baseline** - Save summer and winter baselines
5. **Share with friends** - Compare your distributions with others' same GPU

---

## 🆘 Troubleshooting

### "No data" in histogram panels?

**Histograms need data to bin.** If showing "No data":
1. Increase time range (12h → 24h)
2. Check if data exists in InfluxDB
3. Verify metric names in queries

### Percentiles seem wrong?

**Check data quality:**
1. Look at raw data in InfluxDB
2. Ensure metrics are numeric (not strings)
3. Verify field names match exactly

### Tables show errors?

**Flux queries are complex:**
1. Edit panel → View query
2. Click "Run queries" to test
3. Check Grafana logs: `docker-compose logs grafana`

---

## 📚 Learn More

**Understanding Percentiles:**
- P50 (median): Half above, half below - typical value
- P95: 95% below this - represents "loaded" state
- P99: 99% below this - near-maximum values

**Why Percentiles > Averages:**
- Averages can be skewed by outliers
- P50 shows "typical" better than mean
- P95 shows "under load" without extreme spikes

---

## ✅ Import Instructions

**File Location:**
```
gpu-monitoring-dashboard\dashboard\long-term-analytics-dashboard.json
```

**Steps:**
1. Open Grafana → Dashboards
2. New → Import
3. Upload: `long-term-analytics-dashboard.json`
4. Select InfluxDB datasource
5. Import

**Auto-refresh:** Set to 12 hours (or manually refresh anytime)

---

**Enjoy deep insights into your GPU usage patterns!** 📊🔍

---

*Perfect for: Long-term health monitoring, usage pattern analysis, thermal performance tracking, power consumption analysis*
