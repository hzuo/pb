---
filename: 2025-11-15-18-04-33-tempo-run-analysis-playbook
timestamp: '2025-11-15T18:04:33.796876+00:00'
title: Tempo run analysis playbook
---

authored by: `personalbot01-25-11-15-12-38-20-b80e3d55-0141-4ab5-b4d6-dab3f75efede`

# Tempo run analysis playbook (within a FIT file)

This playbook standardizes how to:

1. **Identify a tempo segment** in a running FIT file.
2. **Define a set of fixed and rolling sub‑regions** within that tempo segment.
3. **Compute comparable metrics** (pace, HR, power, elevation) for each sub‑region.

It builds on the general FIT parsing patterns from the previous memory file
**“Practical guide: analyzing running FIT files with fitdecode”**, and assumes
you have `parse_fit_run` or equivalent utilities available.

All definitions here are precise so that two people running this code on the
same FIT file will get the **same numbers**.

---

## 1. Parse the FIT file and pre‑process

We assume you can get a *record* DataFrame (`rec_df`) and *lap* DataFrame (`lap_df`)
from a FIT file as in the previous guide. For tempo analysis we also need
altitude.

```python
from pathlib import Path
import fitdecode
import pandas as pd
import numpy as np
from fitdecode.records import FitDataMessage

MI_IN_M = 1609.344  # meters in one statute mile


def load_run_with_alt(path: str | Path):
    path = Path(path)
    records, laps = [], []

    with fitdecode.FitReader(path) as fr:
        for frame in fr:
            if not isinstance(frame, FitDataMessage):
                continue
            d = {f.name: getattr(f.value, "value", f.value) for f in frame.fields}

            if frame.name == "record":
                alt = d.get("enhanced_altitude") if d.get("enhanced_altitude") is not None else d.get("altitude")
                records.append({
                    "timestamp": d.get("timestamp"),
                    "distance_m": d.get("distance"),
                    "speed_ms": d.get("speed") if d.get("speed") is not None else d.get("enhanced_speed"),
                    "power": d.get("power"),
                    "hr_bpm": d.get("heart_rate"),
                    "alt_m": alt,
                })

            elif frame.name == "lap":
                laps.append({
                    "start_time": d.get("start_time"),
                    "total_timer_time_s": d.get("total_timer_time"),
                    "total_distance_m": d.get("total_distance"),
                    "avg_power": d.get("avg_power"),
                    "avg_heart_rate": d.get("avg_heart_rate"),
                })

    rec_df = pd.DataFrame(records).dropna(subset=["timestamp", "distance_m"]).sort_values("timestamp").reset_index(drop=True)
    rec_df["timestamp"] = pd.to_datetime(rec_df["timestamp"])
    for col in ["distance_m", "speed_ms", "power", "hr_bpm", "alt_m"]:
        rec_df[col] = rec_df[col].astype(float)

    # enforce monotonic non‑decreasing distance for all downstream distance‑based logic
    rec_df["distance_m_mono"] = np.maximum.accumulate(rec_df["distance_m"].to_numpy())

    lap_df = pd.DataFrame(laps)
    if not lap_df.empty:
        lap_df["start_time"] = pd.to_datetime(lap_df["start_time"])
        lap_df["dist_mi"] = lap_df["total_distance_m"] / MI_IN_M

    return rec_df, lap_df
```

---

## 2. Identify the tempo region (a single lap)

We treat the tempo as a **single continuous lap** that:

- Has **distance within a configurable range**, e.g. 3–10 miles, and
- Has relatively **high average heart rate and/or power**.

For the playbook we define:

- Only consider laps with `dist_mi` between `MIN_TEMPO_MI` and `MAX_TEMPO_MI`.
- Among those, pick the lap with **highest `avg_power`**. If `avg_power` is
  missing, fall back to highest `avg_heart_rate`.

```python
def find_tempo_lap(lap_df: pd.DataFrame,
                   min_tempo_mi: float = 3.0,
                   max_tempo_mi: float = 10.0) -> pd.Series:
    """Identify the tempo lap.

    Heuristic: choose the longest, hardest lap in a given distance band,
    prioritizing avg_power then avg_heart_rate.
    """
    if lap_df.empty:
        raise ValueError("No laps found")

    cand = lap_df[(lap_df["dist_mi"] >= min_tempo_mi) & (lap_df["dist_mi"] <= max_tempo_mi)].copy()
    if cand.empty:
        raise ValueError("No candidate tempo laps in requested distance range")

    cand["_difficulty_score"] = cand["avg_power"].fillna(0) + cand["avg_heart_rate"].fillna(0)
    cand = cand.sort_values(["_difficulty_score", "total_distance_m"], ascending=[False, False])
    return cand.iloc[0]
```

We then slice `rec_df` to the tempo time window and re‑zero distance at tempo start:

```python
def slice_tempo_records(rec_df: pd.DataFrame, tempo_lap: pd.Series) -> pd.DataFrame:
    lap_start = tempo_lap["start_time"]
    lap_end = lap_start + pd.to_timedelta(float(tempo_lap["total_timer_time_s"]), unit="s")

    sub = rec_df[(rec_df["timestamp"] >= lap_start) & (rec_df["timestamp"] <= lap_end)].copy()
    sub = sub.sort_values("timestamp").reset_index(drop=True)

    first_dist = float(sub["distance_m_mono"].iloc[0])
    sub["dist_rel_m"] = sub["distance_m_mono"].astype(float) - first_dist
    sub["dist_rel_m"] = np.maximum.accumulate(sub["dist_rel_m"].to_numpy())
    sub["dist_rel_mi"] = sub["dist_rel_m"] / MI_IN_M

    return sub
```

From here on, **all distances are relative to tempo start** and stored in
`dist_rel_m` / `dist_rel_mi`.

---

## 3. Common helper utilities

We use the same helper definitions for **pace, trimming, and interpolation**
across all sub‑regions.

```python
SEMICIRCLES_TO_DEG = 180.0 / (2**31)


def fmt_pace(sec_per_mile: float) -> str:
    """Format seconds per mile as M:SS/mi, rounding seconds."""
    m = int(sec_per_mile // 60)
    s = int(round(sec_per_mile - m * 60))
    if s == 60:
        m += 1
        s = 0
    return f"{m}:{s:02d}/mi"


def time_at_distance(D_rel: np.ndarray, T: np.ndarray, d: float) -> float:
    """Time (sec since epoch) when distance first reaches d, via linear interpolation.

    D_rel must be non‑decreasing distances in meters, T must be seconds.
    """
    if d <= D_rel[0]:
        return float(T[0])
    if d >= D_rel[-1]:
        return float(T[-1])

    idx = np.searchsorted(D_rel, d, side="left")
    if idx == 0:
        return float(T[0])
    if idx >= len(D_rel):
        return float(T[-1])

    d1, d2 = D_rel[idx - 1], D_rel[idx]
    t1, t2 = T[idx - 1], T[idx]
    if d2 == d1:
        return float(t2)
    frac = (d - d1) / (d2 - d1)
    return float(t1 + frac * (t2 - t1))


def trimmed_stats(x: np.ndarray, low_q: float = 0.02, high_q: float = 0.98):
    """Return (mean, q_low, q_high) with NaNs removed.

    Used for HR, power, and instantaneous pace.
    """
    x = x[~np.isnan(x)]
    if x.size == 0:
        return float("nan"), float("nan"), float("nan")
    avg = float(x.mean())
    q_low = float(np.quantile(x, low_q))
    q_high = float(np.quantile(x, high_q))
    return avg, q_low, q_high
```

---

## 4. Fixed sub‑regions within the tempo

Once we have `lap_recs` (tempo records) with `dist_rel_m` and `dist_rel_mi`,
we define the following fixed regions (all distances in miles, relative to
`dist_rel_mi`):

1. **Tempo mile 1**: 0.0–1.0
2. **Tempo mile 2**: 1.0–2.0
3. **Tempo mile 3**: 2.0–3.0
4. **Tempo mile 4**: 3.0–4.0
5. **Tempo final chunk**: from 4.0 mi to tempo end (if the tempo is longer
   than 4 miles; clipped to actual tempo distance).
6. **Tempo last full mile**: last full 1‑mile window inside the tempo,
   i.e. from \( D_	ext{tempo,max} - 1\,	ext{mi} \) to \( D_	ext{tempo,max} \).

For each region we compute:

- **Distance** in miles
- **Duration** in seconds
- **Average pace** (distance‑normalized): `duration / distance_mi`, formatted
  via `fmt_pace`.
- **Instantaneous pace distribution** (from speed):
  - `speed_ms` → `pace_s = MI_IN_M / speed_ms`
  - Clip pace to [100, 10_000] s/mi (avoid extreme spikes).
  - **Min pace**: 2nd percentile of `pace_s` (converted to `M:SS/mi`).
  - **Max pace**: 98th percentile of `pace_s`.
- **Heart rate** (from `hr_bpm`): average, 2nd percentile, 98th percentile.
- **Power** (from `power`): average, 2nd percentile, 98th percentile.

Implementation:

```python
def segment_stats_fixed(lap_recs: pd.DataFrame,
                        start_mi: float,
                        end_mi: float) -> dict:
    """Compute stats for a [start_mi, end_mi] segment in the tempo.

    Distances are in miles relative to tempo start.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    d0 = max(0.0, start_mi * MI_IN_M)
    d1_target = end_mi * MI_IN_M
    d1 = min(d1_target, lap_total_m)

    if d0 >= lap_total_m or d1 <= d0:
        return {"name": f"[{start_mi},{end_mi}] mi", "note": "no data"}

    t_start = time_at_distance(D_rel, T, d0)
    t_end = time_at_distance(D_rel, T, d1)
    dur = t_end - t_start
    dist_m = d1 - d0
    dist_mi = dist_m / MI_IN_M

    mask = (lap_recs["dist_rel_m"] >= d0) & (lap_recs["dist_rel_m"] <= d1)
    sub = lap_recs.loc[mask].copy()

    # Pace samples from speed
    S_seg = sub["speed_ms"].to_numpy()
    S_seg = S_seg[~np.isnan(S_seg) & (S_seg > 0)]
    if S_seg.size:
        pace_s = MI_IN_M / S_seg
        pace_s = np.clip(pace_s, 100, 10_000)
        avg_pace_inst_s, pace_min_s, pace_max_s = trimmed_stats(pace_s)
    else:
        avg_pace_inst_s = dur / dist_mi if dist_mi > 0 else float("nan")
        pace_min_s = pace_max_s = avg_pace_inst_s

    # Chunk‑level average pace (sec/mi)
    avg_pace_chunk_s = dur / dist_mi if dist_mi > 0 else float("nan")

    # HR stats
    H_seg = sub["hr_bpm"].to_numpy()
    avg_hr, hr_min, hr_max = trimmed_stats(H_seg)

    # Power stats
    P_seg = sub["power"].to_numpy()
    avg_power, p_min, p_max = trimmed_stats(P_seg)

    return {
        "start_mi_rel": d0 / MI_IN_M,
        "end_mi_rel": d1 / MI_IN_M,
        "distance_mi": dist_mi,
        "duration_s": float(dur),
        "avg_pace": fmt_pace(avg_pace_chunk_s),
        "min_pace": fmt_pace(pace_min_s),
        "max_pace": fmt_pace(pace_max_s),
        "avg_hr": avg_hr,
        "min_hr": hr_min,
        "max_hr": hr_max,
        "avg_power": avg_power,
        "min_power": p_min,
        "max_power": p_max,
    }


def fixed_tempo_segments(lap_recs: pd.DataFrame) -> list[dict]:
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    segments = [
        ("Tempo mile 1 (0–1)", 0.0, 1.0),
        ("Tempo mile 2 (1–2)", 1.0, 2.0),
        ("Tempo mile 3 (2–3)", 2.0, 3.0),
        ("Tempo mile 4 (3–4)", 3.0, 4.0),
    ]

    # Final chunk from 4.0 to end (if any remains)
    segments.append(("Tempo final chunk (4.0–end)", 4.0, lap_total_mi))

    # Last full mile inside tempo (if tempo is >= 1 mi)
    if lap_total_mi > 1.0:
        segments.append((
            "Tempo last full mile",
            max(0.0, lap_total_mi - 1.0),
            lap_total_mi,
        ))

    out = []
    for name, s_mi, e_mi in segments:
        stats = segment_stats_fixed(lap_recs, s_mi, e_mi)
        stats["name"] = name
        out.append(stats)

    return out
```

The concrete numbers we reported earlier for your specific run were computed
with this logic (modulo the exact last‑mile definition; this version uses the
most general definition).

---

## 5. Rolling 1‑mile sub‑regions within the tempo

We also identify **rolling** 1‑mile windows *inside the tempo* that optimize
various criteria:

- **Fastest rolling mile**: smallest duration for 1 mile.
- **Slowest rolling mile**: largest duration for 1 mile (still constrained to
  be fully within the tempo).
- **Highest‑power rolling mile**: highest average `power`.
- **Lowest‑power rolling mile**: lowest average `power`.
- **Max‑gain rolling mile**: largest cumulative elevation gain.
- **Max‑loss rolling mile**: largest cumulative elevation loss.

### 5.1 Rolling miles by pace and power

We step over all record indices inside the tempo and, for each starting
distance \(d_0\), determine the end of a 1‑mile window \(d_1 = d_0 + 1\,	ext{mi}\)
via interpolation. We then compute duration and averaging.

```python
def rolling_mile_extremes_pace_power(lap_recs: pd.DataFrame) -> dict:
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9
    P = lap_recs["power"].to_numpy()
    H = lap_recs["hr_bpm"].to_numpy()
    S = lap_recs["speed_ms"].to_numpy()

    lap_total_m = float(D_rel.max())
    mile_m = MI_IN_M
    n = len(D_rel)

    best_fast = best_slow = best_high_p = best_low_p = None

    for i in range(n):
        d0 = D_rel[i]
        d1 = d0 + mile_m
        if d1 > lap_total_m:
            break  # cannot form a full mile starting here

        j = np.searchsorted(D_rel, d1, side="left")
        if j >= n:
            break

        # precise end time via distance interpolation
        d1_prev, d1_next = D_rel[j - 1], D_rel[j]
        t1_prev, t1_next = T[j - 1], T[j]
        if d1_next == d1_prev:
            t_end = t1_next
        else:
            frac = (d1 - d1_prev) / (d1_next - d1_prev)
            t_end = t1_prev + frac * (t1_next - t1_prev)
        dur = t_end - T[i]

        mask = (D_rel >= d0) & (D_rel <= d1)
        idxs = np.nonzero(mask)[0]
        if idxs.size == 0:
            continue
        P_seg = P[idxs]
        P_seg = P_seg[~np.isnan(P_seg)]
        if P_seg.size == 0:
            continue
        avg_power = float(P_seg.mean())

        seg = {"start_idx": i, "start_d_rel": float(d0), "dur": float(dur), "avg_power": avg_power}

        if best_fast is None or dur < best_fast["dur"]:
            best_fast = seg
        if best_slow is None or dur > best_slow["dur"]:
            best_slow = seg
        if best_high_p is None or avg_power > best_high_p["avg_power"]:
            best_high_p = seg
        if best_low_p is None or avg_power < best_low_p["avg_power"]:
            best_low_p = seg

    def enrich(seg: dict, label: str) -> dict:
        if seg is None:
            return {"name": label, "note": "not found"}
        d0 = seg["start_d_rel"]
        d1 = d0 + mile_m
        i0 = seg["start_idx"]
        j = np.searchsorted(D_rel, d1, side="left")
        d1_prev, d1_next = D_rel[j - 1], D_rel[j]
        t1_prev, t1_next = T[j - 1], T[j]
        if d1_next == d1_prev:
            t_end = t1_next
        else:
            frac = (d1 - d1_prev) / (d1_next - d1_prev)
            t_end = t1_prev + frac * (t1_next - t1_prev)
        dur = t_end - T[i0]

        mask = (D_rel >= d0) & (D_rel <= d1)
        sub = lap_recs.loc[mask].copy()

        # Pace stats
        S_seg = sub["speed_ms"].to_numpy()
        S_seg = S_seg[~np.isnan(S_seg) & (S_seg > 0)]
        if S_seg.size:
            pace_s = MI_IN_M / S_seg
            pace_s = np.clip(pace_s, 100, 10_000)
            avg_pace_inst_s, pace_min_s, pace_max_s = trimmed_stats(pace_s)
        else:
            avg_pace_inst_s = dur
            pace_min_s = pace_max_s = dur

        # Chunk avg pace (1 mile)
        avg_pace_chunk_s = dur

        # HR stats
        H_seg = sub["hr_bpm"].to_numpy()
        avg_hr, hr_min, hr_max = trimmed_stats(H_seg)

        # Power stats
        P_seg = sub["power"].to_numpy()
        avg_power, p_min, p_max = trimmed_stats(P_seg)

        return {
            "name": label,
            "start_mi_rel": d0 / MI_IN_M,
            "end_mi_rel": (d0 + mile_m) / MI_IN_M,
            "distance_mi": 1.0,
            "duration_s": float(dur),
            "avg_pace": fmt_pace(avg_pace_chunk_s),
            "min_pace": fmt_pace(pace_min_s),
            "max_pace": fmt_pace(pace_max_s),
            "avg_hr": avg_hr,
            "min_hr": hr_min,
            "max_hr": hr_max,
            "avg_power": avg_power,
            "min_power": p_min,
            "max_power": p_max,
        }

    return {
        "fastest": enrich(best_fast, "Fastest rolling mile"),
        "slowest": enrich(best_slow, "Slowest rolling mile"),
        "highest_power": enrich(best_high_p, "Highest-power rolling mile"),
        "lowest_power": enrich(best_low_p, "Lowest-power rolling mile"),
    }
```

### 5.2 Rolling miles by elevation gain and loss

We use the same rolling 1‑mile windows, but for each window we compute
**cumulative elevation gain and loss** from the `alt_m` field.

Definition (within a window):

- Let `alt[i]` be altitude samples along distance.
- **Gain** = sum of all positive `alt[i+1] - alt[i]`.
- **Loss** = absolute value of sum of all negative `alt[i+1] - alt[i]`.

We linearly interpolate altitude at the precise 1‑mile endpoint if necessary.

```python
def rolling_mile_extremes_elevation(lap_recs: pd.DataFrame) -> dict:
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    A = lap_recs["alt_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    mile_m = MI_IN_M
    lap_total_m = float(D_rel.max())
    n = len(D_rel)

    best_gain = best_loss = None

    for i in range(n):
        d0 = D_rel[i]
        d1 = d0 + mile_m
        if d1 > lap_total_m:
            break
        j = np.searchsorted(D_rel, d1, side="left")
        if j >= n:
            break

        mask = (D_rel >= d0) & (D_rel <= d1)
        idxs = np.nonzero(mask)[0]
        if idxs.size == 0:
            continue
        ds = D_rel[idxs].astype(float)
        alts = A[idxs].astype(float)

        # Interpolate altitude at exact d1 if needed
        if ds[-1] < d1:
            d1_prev, d1_next = D_rel[j - 1], D_rel[j]
            a1_prev, a1_next = A[j - 1], A[j]
            if d1_next == d1_prev:
                alt_end = a1_next
            else:
                frac = (d1 - d1_prev) / (d1_next - d1_prev)
                alt_end = a1_prev + frac * (a1_next - a1_prev)
            ds = np.concatenate((ds, [d1]))
            alts = np.concatenate((alts, [alt_end]))

        diffs = np.diff(alts)
        gain = float(np.sum(diffs[diffs > 0]))
        loss = float(np.sum(diffs[diffs < 0]))  # negative
        loss_abs = -loss

        seg = {"start_idx": i, "start_d_rel": float(d0), "gain_m": gain, "loss_m": loss_abs}

        if best_gain is None or gain > best_gain["gain_m"]:
            best_gain = seg
        if best_loss is None or loss_abs > best_loss["loss_m"]:
            best_loss = seg

    # Reuse segment_metrics‑style logic from the pace/power extremes,
    # but just label the segments differently.
    def enrich(seg: dict, label: str) -> dict:
        if seg is None:
            return {"name": label, "note": "not found"}
        d0 = seg["start_d_rel"]
        d1 = d0 + mile_m
        i0 = seg["start_idx"]

        j = np.searchsorted(D_rel, d1, side="left")
        d1_prev, d1_next = D_rel[j - 1], D_rel[j]
        t1_prev, t1_next = T[j - 1], T[j]
        if d1_next == d1_prev:
            t_end = t1_next
        else:
            frac = (d1 - d1_prev) / (d1_next - d1_prev)
            t_end = t1_prev + frac * (t1_next - t1_prev)
        dur = t_end - T[i0]

        mask = (D_rel >= d0) & (D_rel <= d1)
        sub = lap_recs.loc[mask].copy()

        # Pace, HR, Power metrics identical to rolling_mile_extremes_pace_power
        S_seg = sub["speed_ms"].to_numpy()
        S_seg = S_seg[~np.isnan(S_seg) & (S_seg > 0)]
        if S_seg.size:
            pace_s = MI_IN_M / S_seg
            pace_s = np.clip(pace_s, 100, 10_000)
            avg_pace_inst_s, pace_min_s, pace_max_s = trimmed_stats(pace_s)
        else:
            avg_pace_inst_s = dur
            pace_min_s = pace_max_s = dur

        avg_pace_chunk_s = dur

        H_seg = sub["hr_bpm"].to_numpy()
        avg_hr, hr_min, hr_max = trimmed_stats(H_seg)

        P_seg = sub["power"].to_numpy()
        avg_power, p_min, p_max = trimmed_stats(P_seg)

        return {
            "name": label,
            "start_mi_rel": d0 / MI_IN_M,
            "end_mi_rel": (d0 + mile_m) / MI_IN_M,
            "distance_mi": 1.0,
            "duration_s": float(dur),
            "avg_pace": fmt_pace(avg_pace_chunk_s),
            "min_pace": fmt_pace(pace_min_s),
            "max_pace": fmt_pace(pace_max_s),
            "avg_hr": avg_hr,
            "min_hr": hr_min,
            "max_hr": hr_max,
            "avg_power": avg_power,
            "min_power": p_min,
            "max_power": p_max,
            "gain_m": seg["gain_m"],
            "loss_m": seg["loss_m"],
        }

    return {
        "max_gain": enrich(best_gain, "Max-gain rolling mile"),
        "max_loss": enrich(best_loss, "Max-loss rolling mile"),
    }
```

---

## 6. Putting it all together

A typical workflow for a given FIT file:

```python
path = "your_run.fit"
rec_df, lap_df = load_run_with_alt(path)

# 1) Identify tempo lap and slice records
tempo_lap = find_tempo_lap(lap_df, min_tempo_mi=3.0, max_tempo_mi=10.0)
lap_recs = slice_tempo_records(rec_df, tempo_lap)

# 2) Fixed segments: miles 1–4, final chunk, last full mile
fixed_segments = fixed_tempo_segments(lap_recs)

# 3) Rolling 1‑mile extremes within tempo
roll_pace_power = rolling_mile_extremes_pace_power(lap_recs)
roll_elev = rolling_mile_extremes_elevation(lap_recs)

# 4) Combine everything into a table‑ready structure
all_segments = []
all_segments.extend(fixed_segments)
all_segments.extend([
    roll_pace_power["fastest"],
    roll_pace_power["slowest"],
    roll_pace_power["highest_power"],
    roll_pace_power["lowest_power"],
    roll_elev["max_gain"],
    roll_elev["max_loss"],
])

# From here you can turn `all_segments` into a Markdown or CSV table
```

With this playbook, anyone using the same FIT file and code paths will:

- Identify the *same* tempo lap.
- Derive the *same* fixed segments in tempo space.
- Select the *same* rolling miles for fastest, slowest, highest/lowest power,
  and max elevation gain/loss.
- Compute **identical pace, HR, power, and elevation statistics** for
  each sub‑region.

---

## 7. Appendix: Advanced tempo analyses

This appendix describes three deeper analyses that build on the core tempo
playbook:

1. **Elevation‑adjusted pace (GAP)** per tempo mile.
2. **Cardio–mechanical decoupling** across the tempo.
3. **Micro‑structure of the finishing segment.**

Each follows the same pattern: natural language intent, then a precise code
implementation that reuses the earlier helpers (`fmt_pace`, `time_at_distance`,
`trimmed_stats`, `lap_recs` with `dist_rel_m`, `dist_rel_mi`, `alt_m`).

### 7.1 Elevation‑adjusted pace (GAP) per tempo mile

**Intent (natural language)**

Raw pace on hilly terrain can be misleading. We want a **grade‑adjusted pace
(GAP)** per full tempo mile that answers:

> “If this mile had been run on flat ground, what pace would correspond to the
> same effort, given its average grade?”

We define a simple model:

- For each full mile of the tempo (0–1, 1–2, 2–3, 3–4 miles relative to tempo
  start):
  - Compute **net grade** as `(alt_end − alt_start) / distance`.
  - Convert to percent: `grade_pct = grade * 100`.
  - Adjust pace by **15 s/mi per 1% grade** (positive grade = uphill):

    \[ 	ext{GAP} = 	ext{raw pace} - 15\,	ext{s/mi} 	imes 	ext{grade\_%} \]

This coefficient is a reasonable rule‑of‑thumb. The goal is consistency inside
this playbook, not perfect physiology.

**Formal code definition**

```python
import numpy as np

# Assumes: lap_recs from slice_tempo_records, MI_IN_M, fmt_pace, time_at_distance


def gap_per_tempo_mile(lap_recs: pd.DataFrame,
                        coef_s_per_pct: float = 15.0) -> list[dict]:
    """Compute GAP (grade‑adjusted pace) for each full mile of the tempo.

    coef_s_per_pct: seconds per mile per 1% grade.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    A = lap_recs["alt_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    # Define full‑mile segments strictly inside the tempo
    mile_ranges = []
    start = 0.0
    while start + 1.0 <= lap_total_mi + 1e-6:
        mile_ranges.append((start, start + 1.0))
        start += 1.0

    out = []
    for s_mi, e_mi in mile_ranges:
        d0 = s_mi * MI_IN_M
        d1 = e_mi * MI_IN_M

        # Interpolate altitudes at boundaries
        def alt_at(d: float) -> float:
            if d <= D_rel[0]:
                return float(A[0])
            if d >= D_rel[-1]:
                return float(A[-1])
            idx = np.searchsorted(D_rel, d, side="left")
            if idx == 0:
                return float(A[0])
            if idx >= len(D_rel):
                return float(A[-1])
            d_prev, d_next = D_rel[idx - 1], D_rel[idx]
            a_prev, a_next = A[idx - 1], A[idx]
            if d_next == d_prev:
                return float(a_next)
            frac = (d - d_prev) / (d_next - d_prev)
            return float(a_prev + frac * (a_next - a_prev))

        a0 = alt_at(d0)
        a1 = alt_at(d1)
        net_gain_m = a1 - a0
        dist_m = d1 - d0
        grade = net_gain_m / dist_m if dist_m > 0 else 0.0
        grade_pct = grade * 100.0

        # Raw pace from duration of the exact 1‑mile window
        t_start = time_at_distance(D_rel, T, d0)
        t_end = time_at_distance(D_rel, T, d1)
        raw_pace_s = t_end - t_start  # 1‑mile duration

        gap_pace_s = raw_pace_s - coef_s_per_pct * grade_pct

        out.append({
            "start_mi": s_mi,
            "end_mi": e_mi,
            "grade_pct": grade_pct,
            "raw_pace_s": raw_pace_s,
            "gap_pace_s": gap_pace_s,
            "raw_pace": fmt_pace(raw_pace_s),
            "gap_pace": fmt_pace(gap_pace_s),
        })

    return out
```

This gives, for each tempo mile, a `raw_pace` and `gap_pace` that can be
compared across miles to assess whether apparent pace differences are driven
by terrain or by effort.

---

### 7.2 Cardio–mechanical decoupling across the tempo

**Intent (natural language)**

We want to quantify how much **heart‑rate drifts relative to mechanical output**
over the tempo segment. In other words:

> “As the tempo progresses, do I need more HR to maintain the same pace/power?”

We define decoupling at two levels:

1. **Per full mile within the tempo**:
   - For each 1‑mile window (0–1, 1–2, 2–3, 3–4):
     - Compute avg HR, avg power, and average pace.
     - Derive **pace per watt** (sec/mi/W) and **pace per bpm** (sec/mi/bpm).

2. **First half vs second half of the tempo** (e.g. miles 0–2 vs 2–4):
   - Compare mean HR, mean power, and mean GAP or raw pace between halves.
   - A large increase in HR for similar or slower pace/power indicates
     cardio–mechanical decoupling.

**Formal code definition**

```python
import numpy as np

# Assumes: lap_recs, MI_IN_M, fmt_pace, time_at_distance, gap_per_tempo_mile


def cardio_mechanical_decoupling(lap_recs: pd.DataFrame) -> dict:
    """Compute decoupling metrics per tempo mile and for first vs second half.

    Returns:
      - 'per_mile': list of dicts for each full tempo mile.
      - 'halves': summary for first and second half.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    # Full mile windows inside tempo
    mile_ranges = []
    start = 0.0
    while start + 1.0 <= lap_total_mi + 1e-6:
        mile_ranges.append((start, start + 1.0))
        start += 1.0

    per_mile = []
    for s_mi, e_mi in mile_ranges:
        d0 = s_mi * MI_IN_M
        d1 = e_mi * MI_IN_M
        t_start = time_at_distance(D_rel, T, d0)
        t_end = time_at_distance(D_rel, T, d1)
        dur = t_end - t_start  # seconds for exactly 1 mile

        mask = (lap_recs["dist_rel_m"] >= d0) & (lap_recs["dist_rel_m"] <= d1)
        sub = lap_recs.loc[mask]

        avg_hr = float(sub["hr_bpm"].mean()) if not sub.empty else float("nan")
        avg_pwr = float(sub["power"].mean()) if not sub.empty else float("nan")

        pace_per_watt = dur / avg_pwr if avg_pwr > 0 else float("nan")
        pace_per_bpm = dur / avg_hr if avg_hr > 0 else float("nan")

        per_mile.append({
            "start_mi": s_mi,
            "end_mi": e_mi,
            "avg_hr": avg_hr,
            "avg_power": avg_pwr,
            "avg_pace_s": dur,
            "avg_pace": fmt_pace(dur),
            "pace_per_watt": pace_per_watt,
            "pace_per_bpm": pace_per_bpm,
        })

    # Halves: split miles into early and late sets
    if not per_mile:
        return {"per_mile": [], "halves": {}}

    mid_mi = 0.5 * (per_mile[0]["start_mi"] + per_mile[-1]["end_mi"])

    first_half = [m for m in per_mile if m["end_mi"] <= mid_mi]
    second_half = [m for m in per_mile if m["start_mi"] >= mid_mi]

    def avg_dict(group):
        if not group:
            return {}
        return {
            "avg_hr": float(np.mean([g["avg_hr"] for g in group])),
            "avg_power": float(np.mean([g["avg_power"] for g in group])),
            "avg_pace_s": float(np.mean([g["avg_pace_s"] for g in group])),
        }

    halves = {
        "first_half": avg_dict(first_half),
        "second_half": avg_dict(second_half),
    }

    return {"per_mile": per_mile, "halves": halves}
```

Interpretation example:

- If first‑half and second‑half **avg_hr** differ significantly while
  **avg_power** and **GAP pace** are similar, you have clear decoupling.
- In the worked example, HR rises by ~8 bpm while GAP pace only slows by a
  few seconds per mile—a small, normal amount of decoupling over ~4+ tempo
  miles.

---

### 7.3 Micro‑structure of the finishing segment

**Intent (natural language)**

We want to understand **how the finish ramps**, not just the average over the
last chunk. The question is:

> “Across the last X miles of the tempo, do I gradually squeeze the pace, or is
>  there a distinct final kick?”

We define:

- Let the tempo end at `lap_total_mi` miles (relative to tempo start).
- Choose a finishing window length, e.g. `last_len_mi = 0.4`.
- Divide the last `last_len_mi` into equal bins (e.g. `0.1`‑mile bins).
- For each bin, compute **avg pace, avg HR, avg power**.

**Formal code definition**

```python
# Assumes: lap_recs, MI_IN_M, fmt_pace, time_at_distance


def finishing_microstructure(lap_recs: pd.DataFrame,
                             last_len_mi: float = 0.4,
                             bin_size_mi: float = 0.1) -> list[dict]:
    """Analyze micro‑structure of the finishing segment of the tempo.

    Returns a list of bins from (lap_total_mi - last_len_mi) to lap_total_mi,
    each with avg pace, HR, and power.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    start_mi = max(0.0, lap_total_mi - last_len_mi)
    end_mi = lap_total_mi

    bins = []
    cur = start_mi
    while cur < end_mi - 1e-6:
        bins.append((cur, min(cur + bin_size_mi, end_mi)))
        cur += bin_size_mi

    out = []
    for s_mi, e_mi in bins:
        d0 = s_mi * MI_IN_M
        d1 = e_mi * MI_IN_M

        t_start = time_at_distance(D_rel, T, d0)
        t_end = time_at_distance(D_rel, T, d1)
        dur = t_end - t_start

        dist_m = d1 - d0
        dist_mi = dist_m / MI_IN_M if dist_m > 0 else float("nan")

        mask = (lap_recs["dist_rel_m"] >= d0) & (lap_recs["dist_rel_m"] <= d1)
        sub = lap_recs.loc[mask]

        avg_pace_s = dur / dist_mi if dist_mi > 0 else float("nan")
        avg_hr = float(sub["hr_bpm"].mean()) if not sub.empty else float("nan")
        avg_power = float(sub["power"].mean()) if not sub.empty else float("nan")

        out.append({
            "start_mi_rel": s_mi,
            "end_mi_rel": e_mi,
            "distance_mi": dist_mi,
            "avg_pace_s": avg_pace_s,
            "avg_pace": fmt_pace(avg_pace_s) if not np.isnan(avg_pace_s) else "nan",
            "avg_hr": avg_hr,
            "avg_power": avg_power,
        })

    return out
```

On your example tempo, using `last_len_mi=0.4` and `bin_size_mi=0.1` produced:

- Three bins around ~6:14–6:20/mi at ~330 W and ~183 bpm.
- A final ~0.07‑mile bin at ~5:47/mi and ~352 W with HR ≈185 bpm.

That pattern is a classic **late kick**: strong but controlled effort for most
of the finishing segment, then a distinct final surge. Running this on other
tempos with the same code makes those comparisons objective.

---
