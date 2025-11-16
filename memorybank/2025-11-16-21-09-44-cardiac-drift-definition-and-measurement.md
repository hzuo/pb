---
filename: 2025-11-16-21-09-44-cardiac-drift-definition-and-measurement
timestamp: '2025-11-16T21:09:44.360248+00:00'
title: 'Cardiac drift: definition and measurement'
---

# Measuring cardiac drift (HR–power decoupling)

This note defines a consistent method for measuring **cardiac drift** (also
called HR–power or HR–pace decoupling) from FIT files, reusing the data
structures and helpers from the tempo and LT2 playbooks.

We treat cardiac drift as:

> How much does **heart rate increase relative to mechanical output** (power or
> pace) over the course of an **active segment**?

The goal is to make HR–power decoupling:

- **Comparable across runs**.
- **Robust** to warm‑up and cool‑down.
- Clearly defined for different session types:
  - Long runs (entire run is the active segment).
  - Tempo runs (only the tempo segment is the active segment).

---

## 1. Active segment vs. the whole activity

**Intent (natural language)**

Cardiac drift only makes sense when you are trying to hold a **roughly steady
intensity**. Mixing warm‑up, cool‑down, or very different paces in the same
window will contaminate the drift measurement.

We therefore define an **active segment** for each run type:

- **Long run:**
  - Active segment = the entire continuous run, minus an initial warm‑up trim
    (e.g. first 1–2 miles or first ~10–15 minutes).
- **Tempo run:**
  - Active segment = the identified **tempo lap / segment** only.
  - The warm‑up and cool‑down before/after the tempo are **excluded**.

Concretely:

- For a long run we might use **miles 2.0 to the end** as the active segment.
- For a tempo run we would use **tempo_lap start → tempo_lap end**.

The same cardiac drift function can be applied to either, as long as we pass it
records for **just the active segment**.

---

## 2. Define the segment window by distance

We find it convenient to define the active segment by **distance** rather than
by absolute time:

- Distance is monotonic even with minor pauses/pace changes.
- We can specify indices in miles (e.g. 2.0 to 17.0 mi) or meters.

Given a records DataFrame `rec_df` for a run:

- `rec_df['distance_m_mono']` = cumulative distance (m) from activity start.
- We optionally trim off the first `trim_start_mi` and, if needed, any tail.

Example for a long run (conceptual):

```python
start_mi = 2.0
end_mi = total_distance_miles  # or leave None to use full length

D = rec_df['distance_m_mono'].to_numpy()
T = rec_df['timestamp'].astype('int64').to_numpy() / 1e9  # seconds

start_d = start_mi * MI_IN_M
end_d = end_mi * MI_IN_M

# Use time_at_distance(D, T, d) to get t_start and t_end
# Then mask records: T >= t_start and T <= t_end
```

For a tempo run you would pass `lap_recs` (tempo records only), and
`start_mi` would typically be `0.0` (start of tempo) or a small trim like 0.5 mi
if you want to ignore the very first minute or two of the tempo.

---

## 3. Early vs late halves of the active segment

**Intent (natural language)**

We want to compare the relationship between HR and power in the **early
portion** of the segment vs the **late portion**.

Procedure:

1. Extract records in the **active segment** (by distance as above).
2. Split this segment into two halves **by time**, not by sample count:
   - Early half: from `t_start` to midpoint `t_mid`.
   - Late half: from `t_mid` to `t_end`.
3. For each half, compute:
   - Average HR: `HR_early`, `HR_late` (bpm).
   - Average power: `P_early`, `P_late` (W).
   - Ratio: `R_early = HR_early / P_early`, `R_late = HR_late / P_late`.

**Cardiac drift %** is then defined as:

\[
	ext{drift} \% = \left(rac{R_{late}}{R_{early}} - 1
ight) 	imes 100\%
\]

- If `drift % > 0`: HR is **rising relative to power** (positive drift).
- If `drift % ≈ 0`: HR and power remain proportionate (little/no drift).
- If `drift % < 0`: HR is stable or lower while power increases (negative drift,
  sometimes seen when you warm into the effort or push late).

---

## 4. Practical drift computation (HR–power)

Below is a reference implementation of **HR–power decoupling** for a single
run, given a `rec_df` of the full activity and a chosen distance window.

```python
import numpy as np

MI_IN_M = 1609.344


def time_at_distance(D: np.ndarray, T: np.ndarray, d: float) -> float:
    """Time (sec) when distance first reaches d (meters), via linear interpolation."""
    if d <= D[0]:
        return float(T[0])
    if d >= D[-1]:
        return float(T[-1])
    idx = np.searchsorted(D, d, side='left')
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


def compute_cardiac_drift(rec_df: pd.DataFrame,
                           start_mi: float = 2.0,
                           end_mi: float | None = None) -> dict:
    """Compute HR–power drift over an active segment of a run.

    rec_df: full activity records with columns ['timestamp','distance_m_mono','power','hr_bpm'].
    start_mi: starting mile of the active segment (distance trim).
    end_mi: ending mile of the active segment; None = use full length.

    Returns a dict with early/late HR/P and drift percentage.
    """
    D = rec_df['distance_m_mono'].to_numpy()
    T = rec_df['timestamp'].astype('int64').to_numpy() / 1e9
    H = rec_df['hr_bpm'].to_numpy()
    P = rec_df['power'].to_numpy()

    total_m = float(D[-1])
    total_mi = total_m / MI_IN_M

    if end_mi is None or end_mi > total_mi:
        end_mi = total_mi

    start_d = start_mi * MI_IN_M
    end_d = end_mi * MI_IN_M

    t_start = time_at_distance(D, T, start_d)
    t_end = time_at_distance(D, T, end_d)

    mask = (T >= t_start) & (T <= t_end)
    sub = rec_df.loc[mask].copy()
    if sub.empty:
        raise ValueError('No data in selected segment')

    T_sub = sub['timestamp'].astype('int64').to_numpy() / 1e9
    t0, t1_ = T_sub[0], T_sub[-1]
    t_mid = t0 + (t1_ - t0) / 2.0

    early = sub[T_sub <= t_mid]
    late = sub[T_sub > t_mid]

    def avg_clean(x):
        vals = x.to_numpy(dtype=float)
        vals = vals[~np.isnan(vals)]
        return float(vals.mean()) if vals.size else float('nan')

    P_e, H_e = avg_clean(early['power']), avg_clean(early['hr_bpm'])
    P_l, H_l = avg_clean(late['power']), avg_clean(late['hr_bpm'])

    R_e = H_e / P_e if (P_e > 0 and not np.isnan(P_e) and not np.isnan(H_e)) else float('nan')
    R_l = H_l / P_l if (P_l > 0 and not np.isnan(P_l) and not np.isnan(H_l)) else float('nan')

    drift_pct = (R_l / R_e - 1.0) * 100.0 if (R_e > 0 and not np.isnan(R_e) and not np.isnan(R_l)) else float('nan')

    return {
        'start_mi': start_mi,
        'end_mi': end_mi,
        'HR_early': H_e,
        'P_early': P_e,
        'HR_late': H_l,
        'P_late': P_l,
        'R_early': R_e,
        'R_late': R_l,
        'drift_pct': drift_pct,
    }
```

### Example usage

- **Long run:** use `start_mi=2.0`, `end_mi=None`.
- **Tempo run:** call this on `lap_recs` (tempo only) with `start_mi=0.5` and
  `end_mi` equal to the tempo length in miles.

From the two 17‑mile long runs we analyzed:

- 25‑11‑08 (miles 2.0–17.4): drift ≈ **+0.65%** (HR up very slightly vs power).
- 25‑11‑15 (miles 2.0–17.4): drift ≈ **−2.3%** (power up a bit, HR essentially flat).

Both indicate **excellent stability**; the second run in particular shows
slightly better HR–power coupling over the full active segment.

---

## 5. Interpreting drift numbers

A rough interpretive scale for **steady, aerobic** efforts:

- **< 3–5% drift:**
  - Very little decoupling.
  - Strong aerobic base at that intensity.
- **5–10% drift:**
  - Moderate decoupling.
  - Possibly a bit above sustainable aerobic intensity or impacted by heat,
    dehydration, or fatigue.
- **> 10% drift:**
  - Substantial drift.
  - Intensity may be too high for the intended aerobic target, or conditions are
    poor.

Important caveats:

- Always compare **similar runs**:
  - Similar terrain, distance, and weather.
  - Similar intended intensity (e.g., at or below LT1 or L2).
- Use the method only on **active segments** where you are genuinely trying to
  hold a steady effort:
  - Long steady runs, easy continuous runs, long tempos.
  - Not suitable for highly variable interval workouts without extra logic to
    pick out steady intervals.

With this definition and implementation, cardiac drift becomes a **durable,
comparable metric** between runs, and can be tracked over time alongside LT2
estimates and tempo analyses to monitor aerobic fitness and durability.
