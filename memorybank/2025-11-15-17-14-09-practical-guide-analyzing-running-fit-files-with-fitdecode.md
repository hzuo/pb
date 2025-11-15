---
filename: 2025-11-15-17-14-09-practical-guide-analyzing-running-fit-files-with-fitdecode
timestamp: '2025-11-15T17:14:09.372464+00:00'
title: 'Practical guide: analyzing running FIT files with fitdecode'
---

# Analyzing running FIT files with fitdecode — practical guide

This is a code-first cookbook for turning a running `.fit` file into actionable analysis using `fitdecode` + `pandas`. Assumes you're comfortable with Python, new to `fitdecode`.

## Quick start

```python
from pathlib import Path
import fitdecode
from fitdecode.records import FitDataMessage  # important import

# Minimal skeleton: iterate frames and handle data messages
fit_path = Path('your_run.fit')
with fitdecode.FitReader(fit_path) as fr:
    for frame in fr:
        if isinstance(frame, FitDataMessage):
            if frame.name == 'record':
                # Access fields by name
                values = {f.name: f.value for f in frame.fields}
                # values['timestamp'], values['distance'], values['speed'], values['heart_rate'], ...
            elif frame.name == 'lap':
                pass
            elif frame.name == 'session':
                pass
```

## Canonical parse into DataFrames (records, laps, sessions)

```python
import pandas as pd

def _get(d, name, default=None):
    # Some fitdecode field values are enum-like wrappers; unwrap with .value when present
    v = d.get(name)
    try:
        from fitdecode.types import FitDataType
        if isinstance(v, FitDataType):
            return v.value
    except Exception:
        pass
    return v if v is not None else default

def parse_fit_run(path: str | Path):
    import fitdecode
    from fitdecode.records import FitDataMessage
    path = Path(path)

    records, laps, sessions, events, file_ids = [], [], [], [], []
    with fitdecode.FitReader(path) as fr:  # add check_crc=False if you hit CRC errors
        for frame in fr:
            if not isinstance(frame, FitDataMessage):
                continue
            name = frame.name
            d = {f.name: f.value for f in frame.fields}

            if name == 'record':
                records.append({
                    'timestamp': _get(d, 'timestamp'),
                    'distance_m': _get(d, 'distance'),
                    'speed_ms': _get(d, 'speed') or _get(d, 'enhanced_speed'),
                    'hr_bpm': _get(d, 'heart_rate'),
                    'cadence': _get(d, 'cadence'),  # running: this is often strides/min; steps/min ≈ cadence*2
                    'alt_m': _get(d, 'enhanced_altitude') if _get(d, 'enhanced_altitude') is not None else _get(d, 'altitude'),
                    'position_lat': _get(d, 'position_lat'),
                    'position_long': _get(d, 'position_long'),
                })

            elif name == 'lap':
                laps.append({
                    'start_time': _get(d, 'start_time'),
                    'total_timer_time_s': _get(d, 'total_timer_time'),
                    'total_elapsed_time_s': _get(d, 'total_elapsed_time'),
                    'total_distance_m': _get(d, 'total_distance'),
                    'avg_speed_ms': _get(d, 'avg_speed') or _get(d, 'enhanced_avg_speed'),
                    'avg_hr_bpm': _get(d, 'avg_heart_rate'),
                    'avg_running_cadence': _get(d, 'avg_running_cadence') or _get(d, 'avg_cadence'),
                    'sport': str(_get(d, 'sport')),
                    'sub_sport': str(_get(d, 'sub_sport')),
                })

            elif name == 'session':
                sessions.append({
                    'start_time': _get(d, 'start_time'),
                    'total_timer_time_s': _get(d, 'total_timer_time'),
                    'total_distance_m': _get(d, 'total_distance'),
                    'avg_speed_ms': _get(d, 'avg_speed') or _get(d, 'enhanced_avg_speed'),
                    'avg_hr_bpm': _get(d, 'avg_heart_rate'),
                    'sport': str(_get(d, 'sport')),
                    'sub_sport': str(_get(d, 'sub_sport')),
                })
            elif name == 'event':
                events.append({k: _get(d, k) for k in d.keys()})
            elif name == 'file_id':
                file_ids.append({k: _get(d, k) for k in d.keys()})

    rec_df = pd.DataFrame(records).dropna(subset=['timestamp','distance_m']).sort_values('timestamp').reset_index(drop=True)
    rec_df['timestamp'] = pd.to_datetime(rec_df['timestamp'])

    lap_df = pd.DataFrame(laps)
    sess_df = pd.DataFrame(sessions)
    return rec_df, lap_df, sess_df

rec_df, lap_df, sess_df = parse_fit_run('your_run.fit')
```

## Field quick reference (running)

- Distance (m): `record.distance` and `lap.total_distance`
- Speed (m/s): `record.speed` or `record.enhanced_speed`
- Heart rate (bpm): `record.heart_rate`, `lap.avg_heart_rate`
- Cadence: `record.cadence` (often strides/min; steps/min ≈ cadence*2). Lap gives `avg_running_cadence` in steps/min when present.
- Altitude (m): prefer `enhanced_altitude` over `altitude` when available.
- GPS lat/long: `position_lat`/`position_long` in semicircles; convert to degrees with `deg = semicircles * 180 / 2**31`.

```python
SEMICIRCLES_TO_DEG = 180.0 / (2**31)
rec_df['lat'] = rec_df['position_lat'] * SEMICIRCLES_TO_DEG
rec_df['lon'] = rec_df['position_long'] * SEMICIRCLES_TO_DEG
```

## Session summary

```python
import numpy as np

def fmt_pace_sec_per_mi(sec):
    m = int(sec//60); s = int(round(sec - m*60));
    if s==60: m+=1; s=0
    return f"{m}:{s:02d}/mi"

if not sess_df.empty:
    s = sess_df.iloc[0]
    dist_m = s['total_distance_m']
    time_s = s['total_timer_time_s']
else:  # derive from records
    dist_m = float(rec_df['distance_m'].iloc[-1])
    time_s = (rec_df['timestamp'].iloc[-1] - rec_df['timestamp'].iloc[0]).total_seconds()

pace = time_s / (dist_m / 1609.344)
print('Distance:', f"{dist_m/1609.344:.2f} mi")
print('Time:', f"{time_s/60:.1f} min")
print('Avg pace:', fmt_pace_sec_per_mi(pace))
```

## Identify a “tempo” lap by distance and HR

```python
lap_df['dist_mi'] = lap_df['total_distance_m'] / 1609.344
# e.g., pick the ~4.3–4.5 mile lap with highest avg HR
cand = lap_df[(lap_df['dist_mi']>3.9) & (lap_df['dist_mi']<4.7)].copy()
tempo_lap = (cand.sort_values(['avg_hr_bpm','total_distance_m'], ascending=[False, False]).iloc[0]
             if not cand.empty
             else lap_df.iloc[lap_df['total_distance_m'].idxmax()])

lap_start = pd.to_datetime(tempo_lap['start_time'])
lap_end = lap_start + pd.to_timedelta(float(tempo_lap['total_timer_time_s']), unit='s')

# Slice records in the lap and make distance/time relative to lap start
lap_recs = rec_df[(rec_df['timestamp']>=lap_start) & (rec_df['timestamp']<=lap_end)].copy()
lap_recs['dist_rel_m'] = lap_recs['distance_m'] - float(lap_recs['distance_m'].iloc[0])
lap_recs['time_rel_s'] = (lap_recs['timestamp'] - lap_recs['timestamp'].iloc[0]).dt.total_seconds()
# Distance can be noisy; enforce monotonic non-decreasing
lap_recs['dist_rel_m'] = lap_recs['dist_rel_m'].cummax()
```

## Per-mile splits within any window (exact miles via interpolation)

```python
import numpy as np, math

D = lap_recs['dist_rel_m'].to_numpy()
T = lap_recs['time_rel_s'].to_numpy()

def time_at_distance(dm):  # seconds from window start at a given distance in meters
    idx = np.searchsorted(D, dm)
    if idx == 0: return float(T[0])
    if idx >= len(D): return float(T[-1])
    d1,d2 = D[idx-1], D[idx]; t1,t2 = T[idx-1], T[idx]
    if d2==d1: return float(t2)
    return float(t1 + (dm - d1)/(d2 - d1) * (t2 - t1))

mile_m = 1609.344
total_m = float(tempo_lap['total_distance_m'])
full_miles = int(math.floor(total_m / mile_m))

splits = []
for i in range(full_miles):
    t0 = time_at_distance(i * mile_m)
    t1 = time_at_distance((i+1) * mile_m)
    splits.append(t1 - t0)

print('Mile splits:', [fmt_pace_sec_per_mi(s) for s in splits])
```

## Best rolling X-mile segment (two-pointer + interpolation)

```python
TARGET_MI = 4.30
TARGET_M = TARGET_MI * 1609.344

D_all = rec_df['distance_m'].to_numpy()
T_all = rec_df['timestamp'].astype('int64').to_numpy()/1e9  # seconds

best = None; j = 0
for i in range(len(D_all)):
    target = D_all[i] + TARGET_M
    while j < len(D_all) and D_all[j] < target:
        j += 1
    if j >= len(D_all): break
    d1,d2 = D_all[j-1], D_all[j]
    t1,t2 = T_all[j-1], T_all[j]
    frac = 0 if d2==d1 else (target - d1)/(d2 - d1)
    t_target = t1 + frac*(t2 - t1)
    dur = t_target - T_all[i]
    if best is None or dur < best['dur']:
        best = {'start_idx': i, 'dur': dur}

print('Best 4.30-mi pace:', fmt_pace_sec_per_mi(best['dur']/TARGET_MI))
```

## Heart-rate averages over exact windows (trapezoid rule)

```python
# Build time-indexed HR series and interpolate across minor gaps
hr_series = (lap_recs[['time_rel_s','hr_bpm']]
             .set_index('time_rel_s')['hr_bpm']
             .sort_index()
             .interpolate(method='index', limit_direction='both'))
x = hr_series.index.to_numpy(float)
y = hr_series.to_numpy(float)

def avg_hr_between(t0, t1):
    import numpy as np
    if t1 <= t0: return float('nan')
    mask = (x > t0) & (x < t1)
    ts = np.concatenate([[t0], x[mask], [t1]])
    hs = np.interp(ts, x, y)
    dt = np.diff(ts)
    h_mid = 0.5*(hs[:-1] + hs[1:])
    return float(np.sum(h_mid * dt) / (t1 - t0))

# Example: HR for each exact mile split
mile_avgs = [avg_hr_between(time_at_distance(i*mile_m), time_at_distance((i+1)*mile_m))
             for i in range(full_miles)]
```

## Elevation gain per mile (smoothed, positive deltas only)

```python
# Smooth altitude with a small rolling median to tame baro noise
alt_s = (lap_recs[['time_rel_s','alt_m']]
         .dropna()
         .set_index('time_rel_s')['alt_m']
         .rolling(window=11, center=True, min_periods=1).median()
         .sort_index()
         .interpolate(method='index', limit_direction='both'))
xa, ya = alt_s.index.to_numpy(float), alt_s.to_numpy(float)

def elevation_gain_between(t0, t1, min_step_m=0.1):
    import numpy as np
    mask = (xa > t0) & (xa < t1)
    ts = np.concatenate([[t0], xa[mask], [t1]])
    alts = np.interp(ts, xa, ya)
    diffs = np.diff(alts)
    diffs = np.where(diffs > min_step_m, diffs, 0.0)  # drop tiny ups
    return float(np.sum(diffs))

mile_gains_m = [elevation_gain_between(time_at_distance(i*mile_m), time_at_distance((i+1)*mile_m))
                for i in range(full_miles)]
mile_gains_ft = [g*3.28084 for g in mile_gains_m]
```

## Visualization: pace and HR with highlighted window

```python
import matplotlib.pyplot as plt

# Pace (min/mi) from speed; clip + smooth for readability
pace_min_per_mi = (1609.344 / rec_df['speed_ms'] / 60).clip(3, 20).rolling(15, center=True, min_periods=1).median()

t0 = rec_df['timestamp'].iloc[0]
t_min = (rec_df['timestamp'] - t0).dt.total_seconds()/60

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,6), sharex=True)
ax1.plot(t_min, pace_min_per_mi)
ax1.invert_yaxis(); ax1.set_ylabel('Pace (min/mi)'); ax1.grid(True, alpha=0.3)
ax2.plot(t_min, rec_df['hr_bpm'].rolling(5, center=True, min_periods=1).median(), color='r')
ax2.set_ylabel('HR (bpm)'); ax2.set_xlabel('Time (min)'); ax2.grid(True, alpha=0.3)
plt.show()
```

---

## Gotchas, quirks, and fixes

- Import shape: there is no `fitdecode.FitFrameData`. Use `from fitdecode.records import FitDataMessage` and check `isinstance(frame, FitDataMessage)`.
- Enum-like values: some fields are wrappers; unwrap with `.value` (see `_get` helper) or convert to `str()` for readable names.
- Enhanced fields: prefer `enhanced_speed`/`enhanced_altitude` when present; fall back to `speed`/`altitude`.
- GPS coordinates: `position_lat`/`position_long` are in semicircles, not degrees. Convert with `180/2**31`.
- Distance irregularities: samples can be non-monotonic (noise, pauses). For within-window analysis, compute distance relative to window start and `cummax()` it.
- Cadence units: `record.cadence` for running is often strides per minute; steps per minute ≈ `cadence * 2`. Lap `avg_running_cadence` is usually in steps/min already.
- Pauses and pace spikes: pace derived from `distance` deltas can blow up during pauses. Use `speed` (m/s) when available, clip to sane bounds, then smooth.
- CRC failures: some exported FITs fail CRC. Open with `FitReader(path, check_crc=False)`.
- Timezones: FIT timestamps are tz-aware (often UTC). Convert with pandas: `pd.to_datetime(ts).tz_convert('America/New_York')`.
- Apple/TP exports: fields like `lap_trigger`, `event` may be sparse or device-specific. Don’t rely on them for segmentation; prefer time/distance heuristics.

## Reusable utilities (copy/paste)

```python
SEMICIRCLES_TO_DEG = 180.0 / (2**31)

def fmt_pace(sec):
    m = int(sec//60); s = int(round(sec - m*60));
    if s==60: m+=1; s=0
    return f"{m}:{s:02d}/mi"

def time_at_distance_arrays(D, T, dm):
    import numpy as np
    idx = np.searchsorted(D, dm)
    if idx == 0: return float(T[0])
    if idx >= len(D): return float(T[-1])
    d1,d2 = D[idx-1], D[idx]; t1,t2 = T[idx-1], T[idx]
    if d2==d1: return float(t2)
    return float(t1 + (dm - d1)/(d2 - d1) * (t2 - t1))

def rolling_best_segment(distance_m, D, T):
    # Return (best_duration_s, start_index)
    best = None; j = 0
    for i in range(len(D)):
        target = D[i] + distance_m
        while j < len(D) and D[j] < target:
            j += 1
        if j >= len(D): break
        d1,d2 = D[j-1], D[j]; t1,t2 = T[j-1], T[j]
        frac = 0 if d2==d1 else (target - d1)/(d2 - d1)
        t_target = t1 + frac*(t2 - t1)
        dur = t_target - T[i]
        if best is None or dur < best[0]:
            best = (dur, i)
    return best
```

## Checklist for a new FIT file

- Can you iterate frames and see `record`/`lap`/`session`? If not, try `check_crc=False`.
- Do `record` fields include `enhanced_speed`/`enhanced_altitude`? Prefer them.
- Are timestamps tz-aware? Convert to your local tz early.
- Is `cadence` ≈ half of lap `avg_running_cadence`? Multiply record cadence by 2 for steps/min comparisons.
- Enforce monotonic distance before interpolation.
- Use interpolation for exact-mile splits and rolling segments.

With these patterns you can replicate: splits per mile, HR-by-mile, best rolling distances, and elevation gain for any device-exported run.
