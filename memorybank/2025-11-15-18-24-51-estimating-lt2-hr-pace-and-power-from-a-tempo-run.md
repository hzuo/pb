---
filename: 2025-11-15-18-24-51-estimating-lt2-hr-pace-and-power-from-a-tempo-run
timestamp: '2025-11-15T18:24:51.853711+00:00'
title: Estimating LT2 HR, pace, and power from a tempo run
---

authored by: `personalbot01-25-11-15-12-38-20-b80e3d55-0141-4ab5-b4d6-dab3f75efede`

# Estimating LT2 HR, pace, and power from a tempo run (with GAP)

This note describes a **repeatable method** for estimating LT2 / L2 threshold
heart rate, flat‑equivalent pace, and power from a *single sustained tempo run
in a FIT file*. It assumes you:

- Already know how to parse FIT files into `rec_df`/`lap_df` with
  `distance_m`, `speed_ms`, `power`, `hr_bpm`, `alt_m` as in the previous
  playbooks.
- Have identified a **tempo lap** and sliced records to `lap_recs` (tempo
  only), with `dist_rel_m`, `dist_rel_mi` relative to tempo start.

The process is *not* meant for arbitrary runs:

- A **pure easy run** at L1/L2 does not provide enough high‑end information.
- A **pure VO2max / interval workout** has work bouts that are too short and
  too far above LT2 to directly infer threshold.

Instead, this method assumes a **sustained tempo segment**, roughly 20–40
minutes continuous, where the intent was “comfortably hard” or “threshold”
running.

We will:

1. Identify a **tempo plateau** region where HR and power are relatively
   stable.
2. Use a simple grade‑adjusted pace (GAP) model to normalize pace for hills.
3. Estimate LT2 HR, pace, and power from this plateau.
4. Be explicit about the caveats (GAP approximations, terrain, fatigue).

---

## 1. Preliminaries and assumptions

We assume all of the following exist from earlier playbooks:

- `lap_recs`: DataFrame of records within the *tempo lap only*, sorted by
  `timestamp`, with
  - `timestamp` (datetime),
  - `dist_rel_m` (meters, relative to tempo start),
  - `dist_rel_mi` (miles, relative to tempo start),
  - `speed_ms`, `power`, `hr_bpm`, `alt_m`.
- `MI_IN_M = 1609.344` (meters per mile).
- Helpers:

```python
import numpy as np


def fmt_pace(sec_per_mile: float) -> str:
    m = int(sec_per_mile // 60)
    s = int(round(sec_per_mile - m * 60))
    if s == 60:
        m += 1
        s = 0
    return f"{m}:{s:02d}/mi"


def time_at_distance(D: np.ndarray, T: np.ndarray, d: float) -> float:
    """Time (sec since epoch) when distance first reaches d (meters).

    D must be non‑decreasing, T in seconds.
    """
    if d <= D[0]:
        return float(T[0])
    if d >= D[-1]:
        return float(T[-1])
    idx = np.searchsorted(D, d, side="left")
    if idx == 0:
        return float(T[0])
    if idx >= len(D):
        return float(T[-1])
    d1, d2 = D[idx - 1], D[idx]
    t1, t2 = T[idx - 1], T[idx]
    if d2 == d1:
        return float(t2)
    frac = (d - d1) / (d2 - d1)
    return float(t1 + frac * (t2 - t1))
```

---

## 2. Defining sub‑plateau and plateau regions

**Intent (natural language)**

On a good tempo run, HR and power **ramp up**, then **plateau**, then possibly
**drift or spike** near the end. We want:

- A **sub‑plateau** region: where HR is rising toward steady‑state but could
  still be a bit below “true” LT2.
- A **main plateau** region: the central, nearly steady segment where HR and
  power are relatively flat—our best proxy for actual LT2 behavior.
- Exclude
  - The **initial ramp** (often ~0–0.5 miles of tempo), and
  - The **final kick** (last ~0.2–0.4 miles where HR and power spike).

**Formal code definition**

We parameterize the trimming and define a function that returns a central
“plateau slice” of the tempo:

```python
import pandas as pd


def tempo_plateau_slice(lap_recs: pd.DataFrame,
                        trim_start_mi: float = 0.5,
                        trim_end_mi: float = 0.3) -> pd.DataFrame:
    """Return the central plateau portion of a tempo segment.

    - trim_start_mi: miles to exclude from the beginning of the tempo.
    - trim_end_mi: miles to exclude from the end of the tempo.

    For example, with a 4.3‑mi tempo, trim_start_mi=0.5 and trim_end_mi=0.3
    keeps miles roughly 0.5–4.0.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    start_mi = trim_start_mi
    end_mi = max(trim_start_mi, lap_total_mi - trim_end_mi)

    d0 = start_mi * MI_IN_M
    d1 = end_mi * MI_IN_M

    t_start = time_at_distance(D_rel, T, d0)
    t_end = time_at_distance(D_rel, T, d1)

    mask = (T >= t_start) & (T <= t_end)
    return lap_recs.loc[mask].copy()
```

You can also define a **sub‑plateau** explicitly as the first 1–2 miles of this
central slice and the **late plateau** as the last 1–2 miles, to examine
cardio–mechanical drift.

---

## 3. Using GAP cautiously to normalize for hills

**Intent (natural language)**

We’d like to treat a steady tempo on hills as if it were on flat ground.
However:

- Different runners respond differently to uphills/downhills.
- The relationship between grade and pace is not perfectly linear.

We therefore use GAP as a **rough correction**, not gospel:

- Approximate relationship: **15 s/mi per 1% grade**.
- Upgrades: increase GAP (faster flat‑equivalent pace than raw suggests).
- Downgrades: decrease GAP (slower flat‑equivalent pace than raw suggests).

**Formal code definition**

We compute GAP for each full mile of the tempo:

```python


def gap_per_tempo_mile(lap_recs: pd.DataFrame,
                        coef_s_per_pct: float = 15.0) -> list[dict]:
    """Compute a simple GAP (grade‑adjusted pace) per full tempo mile.

    GAP = raw_pace_s - coef_s_per_pct * grade_pct,
    where grade_pct is net grade over the mile * 100.
    """
    D_rel = lap_recs["dist_rel_m"].to_numpy()
    A = lap_recs["alt_m"].to_numpy()
    T = lap_recs["timestamp"].astype("int64").to_numpy() / 1e9

    lap_total_m = float(D_rel.max())
    lap_total_mi = lap_total_m / MI_IN_M

    mile_ranges = []
    start = 0.0
    while start + 1.0 <= lap_total_mi + 1e-6:
        mile_ranges.append((start, start + 1.0))
        start += 1.0

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

    out = []
    for s_mi, e_mi in mile_ranges:
        d0 = s_mi * MI_IN_M
        d1 = e_mi * MI_IN_M

        a0 = alt_at(d0)
        a1 = alt_at(d1)
        net_gain_m = a1 - a0
        dist_m = d1 - d0
        grade = net_gain_m / dist_m if dist_m > 0 else 0.0
        grade_pct = grade * 100.0

        t0 = time_at_distance(D_rel, T, d0)
        t1 = time_at_distance(D_rel, T, d1)
        raw_pace_s = t1 - t0

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

Caveat: this GAP is **good for comparing different miles in the same run**,
not for claiming an absolute “true flat pace” across all courses and runners.

---

## 4. Estimating LT2 HR and power from the plateau

**Intent (natural language)**

We want a single LT2 number for HR and power that summarizes the **central
plateau** of the tempo—roughly the portion where:

- HR is high and relatively stable.
- Power is close to the peak sustainable value (not the end‑of‑run spike).

We treat the plateau slice’s average HR and power as **LT2 HR and LT2 power**.

**Formal code definition**

```python


def estimate_lt2_hr_power(lap_recs: pd.DataFrame,
                           trim_start_mi: float = 0.5,
                           trim_end_mi: float = 0.3) -> dict:
    """Estimate LT2 HR and power from the central plateau of a tempo run.

    Returns:
      - lt2_hr: plateau average HR (bpm).
      - lt2_power: plateau average power (W).
      - hr_range: (min, max) HR over plateau.
      - power_range: (min, max) power over plateau.
    """
    plateau = tempo_plateau_slice(lap_recs, trim_start_mi, trim_end_mi)
    if plateau.empty:
        raise ValueError("Plateau slice is empty; tempo too short or trim too aggressive.")

    hr = plateau["hr_bpm"].to_numpy()
    pwr = plateau["power"].to_numpy()

    # Simple mean and observed range over plateau
    lt2_hr = float(np.nanmean(hr))
    lt2_power = float(np.nanmean(pwr))

    hr_min = float(np.nanmin(hr))
    hr_max = float(np.nanmax(hr))
    p_min = float(np.nanmin(pwr))
    p_max = float(np.nanmax(pwr))

    return {
        "lt2_hr": lt2_hr,
        "lt2_power": lt2_power,
        "hr_range": (hr_min, hr_max),
        "power_range": (p_min, p_max),
        "n_samples": int(plateau.shape[0]),
    }
```

In the worked example tempo, this plateau average came out around:

- **LT2 HR ≈ 178 bpm**,
- **LT2 power ≈ 312 W**.

This matches the intuition: central tempo miles had HR ~178–180 bpm and power
~300–325 W, with the steep uphill mile being slightly above average power and
the downhill mile slightly below.

---

## 5. Estimating LT2 pace (flat‑equivalent)

**Intent (natural language)**

We want a single **LT2 pace** that answers:

> “If I ran a long tempo on flat ground at this same effort, what pace would it
>  be?”

We combine **GAP** per tempo mile with the plateau definition:

- Select the tempo miles that overlap the central plateau.
- Average their GAP paces.

**Formal code definition**

```python


def estimate_lt2_pace(lap_recs: pd.DataFrame,
                       trim_start_mi: float = 0.5,
                       trim_end_mi: float = 0.3,
                       coef_s_per_pct: float = 15.0) -> dict:
    """Estimate LT2 flat‑equivalent pace from a tempo run.

    Uses:
      - plateau slice for overall context.
      - per‑mile GAP to normalize for terrain.

    Returns:
      - lt2_gap_pace_s: average GAP (sec/mi) across plateau‑overlapping miles.
      - lt2_gap_pace: formatted M:SS/mi.
      - per_mile: list of (start_mi, end_mi, raw_pace, gap_pace) for inspection.
    """
    plateau = tempo_plateau_slice(lap_recs, trim_start_mi, trim_end_mi)
    if plateau.empty:
        raise ValueError("Plateau slice is empty; tempo too short or trim too aggressive.")

    gap_rows = gap_per_tempo_mile(lap_recs, coef_s_per_pct)

    # Keep only miles that overlap the plateau in distance space
    plateau_D = plateau["dist_rel_m"].to_numpy()
    pl_start_m = float(plateau_D.min())
    pl_end_m = float(plateau_D.max())

    contrib = []
    for row in gap_rows:
        s_mi, e_mi = row["start_mi"], row["end_mi"]
        d0 = s_mi * MI_IN_M
        d1 = e_mi * MI_IN_M
        # overlap if intervals intersect
        if d1 <= pl_start_m or d0 >= pl_end_m:
            continue
        contrib.append(row["gap_pace_s"])

    if not contrib:
        raise ValueError("No full miles overlap the plateau; tempo too short or misaligned.")

    lt2_gap_pace_s = float(np.mean(contrib))

    return {
        "lt2_gap_pace_s": lt2_gap_pace_s,
        "lt2_gap_pace": fmt_pace(lt2_gap_pace_s),
        "per_mile": gap_rows,
    }
```

In the worked example, the plateau‑overlapping miles had GAPs clustering
around **6:35–6:45/mi**, with a mean of roughly **6:40/mi**.

---

## 6. Putting it together: LT2 summary from a tempo run

A typical usage, combining all of the above:

```python
rec_df, lap_df = load_run_with_alt("your_run.fit")
# tempo_lap found via find_tempo_lap from the tempo playbook
lap_recs = slice_tempo_records(rec_df, tempo_lap)

plateau = tempo_plateau_slice(lap_recs, trim_start_mi=0.5, trim_end_mi=0.3)
lt2_hp = estimate_lt2_hr_power(lap_recs, trim_start_mi=0.5, trim_end_mi=0.3)
lt2_pace = estimate_lt2_pace(lap_recs, trim_start_mi=0.5, trim_end_mi=0.3)

print("LT2 HR (bpm):", lt2_hp["lt2_hr"], "range over plateau:", lt2_hp["hr_range"])
print("LT2 power (W):", lt2_hp["lt2_power"], "range over plateau:", lt2_hp["power_range"])
print("LT2 flat‑equiv pace:", lt2_pace["lt2_gap_pace"])
```

For the analyzed tempo run, this yielded approximately:

- **LT2 HR ≈ 178 bpm** (with plateau range ~176–181 bpm)
- **LT2 power ≈ 312 W**
- **LT2 flat‑equivalent pace ≈ 6:40/mi (≈ 4:08–4:10/km)**

These numbers are **estimates from a single session**. They should be
cross‑checked with:

- Other tempo runs using the same playbook.
- A dedicated 30‑minute threshold test.
- Race performances near 45–60 minutes.

But the methodology here ensures that, given the same type of tempo run and
these functions, two analysts will converge on effectively **the same LT2 HR,
pace, and power** for that run.
