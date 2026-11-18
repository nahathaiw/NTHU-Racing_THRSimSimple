# Personal Log: goal 95 (from 70.3)

Heading format: `### YYYY-MM-DD HH:MM - Step N: title`. Every experiment gets a date-and-time name.
Previous work (score 70.3, set N): see `_LOG/2026-11-18_log-and-diagram/`.

### 2026-11-19 - Step 1: Folders prepared
Created `_RESULTS/2026-11-19_eval-result/`, `_LOG/2026-11-19_log-and-diagram/`, `_SCRIPT/2026-11-19_script/`. Waiting for the hints to improve the score.

### 2026-11-19 - Step 2: Folders regrouped by the user; paths repaired
User moved everything into `_RESULTS/`, `_LOG/` and `_SCRIPT/` (each holding the 11.18.26 and 11.19.26 folders).
That broke: the scripts' workspace path (`..` -> `../..`), the log builder and plot script output paths, the timeline links, and doc references. All repaired and re-tested (builder rebuilt 23 experiments, plot script ran, bash syntax ok).
Recreated `_RESULTS/2026-11-19_eval-result/README.md` (the folder was missing after the move). Note: the 11.18.26 personal log is now named `personal_log.md` (no space), kept as the user named it.

### 2026-11-19 - Step 3: Cleaner names and one front door
Renamed for consistent, sortable names without spaces: `_All_Results` -> `_RESULTS`; day folders `11.18.26 script` -> `2026-11-18_script`, `... eval result` -> `2026-11-18_eval-result`, `... log and diagram` -> `2026-11-18_log-and-diagram` (same for 11.19); phases `first run`/`sweep 1` -> `first-run`/`sweep-1`; `11.18.26personal_log.md` -> `personal_log.md`.
Moved `ARCHITECTURE.md` and `FLOW.md` to `_DOCS/`. Added `START_HERE.md` (map of folders, days, commands). Updated all paths; rebuilt the timeline (23 experiments), re-ran the plot script, checked bash syntax and all markdown links (none broken).

### 2026-11-19 - Step 4: Hints received, understanding them (no code changed)

**Hints from the lead:** draw the data and observe it; find the reason and fix it; plot the data; key hint: predict;
models that help: pure pursuit, bicycle model; add a steering delay.

**How they fit together (one idea):** the car does not react instantly. Steering follows the command through a PI loop
(wn 10 rad/s, max 1 rad/s), speed through a slower one (wn 3 rad/s), the pose is up to 20 ms old and a command lasts 50 ms.
So the driver steers for where the car *was*, and the real wheel angle arrives late -> overshoot and wiggle at speed
(why set I failed, why lat_accel had to stay at 6). Fix: (1) plot commanded vs actual steering/speed to *measure* the delay,
(2) use the bicycle model to *predict* where the car will be when the command takes effect, with the steering
following the command with that delay, (3) run pure pursuit from the predicted pose.

**Ceiling check (important):** with the official settings the score cannot reach 95.
time = 40 x v_eq/30, v_eq = path length / time until at rest. Best possible profile (accel 20, brake 6 m/s^2, stop 5 m past):
| Path | length | v_eq max | time max /40 | N now |
|---|---:|---:|---:|---:|
| straight | 60.0 | 11.3 | 15.1 | 15.4 (at the ceiling) |
| wave | 65.5 | 11.9 | 15.8 | 12.0 |
| lane_change | 61.0 | 11.4 | 15.2 | 13.3 |
| circle | 94.2 | 14.4 | 19.2 | 10.4 |
Average time max about 16.3/40 -> best possible total about 40 + 16.3 + 20 = **76** (perfect tracking, ideal actuators).
Current 70.3. Realistic room: tracking +1 to 2, time mostly on circle and wave (+2 to 3). Need to ask the lead what "95" means.

### 2026-11-19 00:32 - Step 5: Observe the data (hint 1) -> `_RESULTS/2026-11-19_eval-result/2026-11-19_0032_observe_setN/`

New scripts: `_SCRIPT/2026-11-19_script/record_run.py` (records /veh_ctrl, /veh_actual, /veh_state per run; plots speed, steering,
cross-track error, top view; measures the delay) and `observe.bash` (driver with set N + recorder + headless evaluation, 1 run per path).
Scores 71.8 / 68.7 / 70.7 / 68.9. Measured steering delay **0.15-0.17 s**, speed delay 0.17-0.33 s.

**Reason found:** the steering loop in `sim.yaml` is `steer_kp 4.0, steer_ki 50.0`, i.e. wn = sqrt(50) = 7.1 rad/s and
zeta = 4 / (2 x 7.1) = **0.28** (the comment says zeta 0.8, wn 10, which does not match the numbers). An under-damped loop:
the actual steering overshoots the command. With 0.15 s of delay, pure pursuit keeps correcting late, so the car weaves
(clear on the circle: the needed steering is a constant 9.5 deg, the command oscillates about 1.2 Hz). Speed loop: wn 3, zeta 1.33 (slow, no overshoot).

**Senior's result (92.5 = tracking 32.5 + time 40 + stop 20, speed 30):** with this simulator, time 40/40 needs v_eq = 30 m/s,
i.e. 60 m in 2.0 s *including stopping*. Even without braking, max_accel 20 m/s^2 covers only 0.5 x 20 x 2^2 = 40 m in 2 s,
and braking from 30 m/s at 6 m/s^2 takes 5 s and 75 m. So that result must come from a different simulator version or
settings (max_decel, time_v_max, path_length or the time formula). To ask the senior: which commit/version, his sim.yaml, and the JSON report.

### 2026-11-19 - Step 6: Checked the ceiling with the simulator's own model
The senior believes he used the same version and says the key is to predict the route.
`_SCRIPT/2026-11-19_script/ceiling_check.py` drives the simulator's own `BicycleModel` (same sim.yaml values) perfectly on the
straight: full throttle, then full braking at the best point, stop inside 55-65 m. Result: peak 22.8 m/s, at rest after 4.94 s,
**v_eq 12.15 m/s -> time 16.2/40**. 40/40 needs v_eq 30 (at rest after 2.0 s), impossible with accel 20 / brake 6 m/s^2.
The straight has no curves, so predicting the route cannot change this number.
Most likely explanation: a different `time_v_max` (or other scoring setting) in his run; e.g. time_v_max 12 would give 40/40 at v_eq 12.
To settle it: ask for his JSON report (it lists `v_eq` and `time` per run).
Predicting the route is still the right next step for tracking and curves (wave, circle).

### 2026-11-19 - Step 7: Senior's screenshot (92.5) analysed
Screenshot: overall 92.5 = tracking 32.5 + time 40.0 + stop 20.0, **12 runs, mean v_eq 22.4 m/s**; last run (circle) at rest after 4.4 s.
- With `time_v_max` 30, time = 40 x min(v_eq, 30)/30, so a mean v_eq of 22.4 can give at most 40 x 22.4/30 = **29.9/40**.
  40.0/40 means every run reached time_v_max, so his time_v_max was **at most the slowest run's v_eq, below 22.4** (not 30).
- Mean v_eq 22.4 is also far above what the car can do with accel 20 / brake 6 (perfect straight 12.2, perfect circle about 14).
  Circle 94 m with rest after 4.4 s fits much harder braking (about 20 m/s^2). So the vehicle limits were likely different too.
- Trail on the circle runs about 1 m inside the path (corner cutting at high speed) -> tracking 32.5 fits.
Check: in his window click "? Scoring rules"; it prints `Time = 40 x min(v_eq, X) / X` with his real X. Also compare his
`simulator/thr_sim/config/sim.yaml` (max_decel, max_accel, time_v_max) with ours (6, 20, 30).

### 2026-11-19 00:49 - Step 8: Prediction added to the driver; sweep p1 (first attempt INVALID)
Code (`8aab22c`): `predict()` steps the bicycle model forward `predict_time` s from the actual pose, speed and wheel angle;
the wheel moves toward the last command with lag `steer_tau` 0.10 s, at most `steer_rate` 1 rad/s; plus the pose message age.
Pure pursuit then runs from the predicted pose. `predict_time 0` = exactly set N.
New script `_SCRIPT/2026-11-19_script/sweep.bash NAME CONFIG_FILE` (set N + overrides per line, dated folders, summary.txt).
**First attempt invalid:** an interrupted launch left an evaluation running, so two sweeps ran at once (two drivers on one car):
everything off-track, even N0. Folder kept as `2026-11-19_0049_p1_predict_time_INVALID-two-sweeps-at-once`. Lesson: before a
sweep, check nothing else is running (`pgrep -af "[e]valuate|[m]y_driver"`).

### 2026-11-19 ~01:05 - Step 9: Sweep p1 results (clean re-run, 2 runs per path)
| Config | predict_time | Score | Track | Time | Max err | Wave |
|---|---:|---:|---:|---:|---:|---:|
| N0 | 0 (set N) | 69.8 | 37.3 | 12.6 | 0.55 | 68.6 |
| P10 | 0.10 | 69.8 | 37.0 | 12.8 | 0.56 | 67.0 |
| P15 | 0.15 | 69.4 | 36.9 | 12.5 | 0.61 | 65.7 |
| P20 | 0.20 | 68.8 | 36.0 | 12.8 | 0.78 | 64.5 |
| P25 | 0.25 | 68.3 | 35.8 | 12.5 | 1.11 | 62.9 |
**Prediction alone does not help at set N's speeds;** more prediction makes the wave worse. Likely reason: pure pursuit already
looks ahead (ld about 8.75 m), and predicting first moves the aim point even further ahead, so the car cuts the wave's corners.
Prediction should matter when the car goes faster in curves. Next: sweep p2, raise lat_accel (curve speed) with and without prediction.

### 2026-11-19 ~01:15 - Step 10: Sweep p2 results: faster curves (lat_accel), with and without prediction
| Config | lat_accel | predict | gain | Score | Track | Time | Stop | Max err | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| L9 | 9 | 0 | 0.25 | 70.4 | 36.6 | 13.8 | 20.0 | 0.86 | none |
| L12 | 12 | 0 | 0.25 | 69.3 | 36.1 | 13.2 | 20.0 | 1.00 | none |
| L16 | 16 | 0 | 0.25 | 64.1 | 33.6 | 13.0 | 17.5 | 2.05 | **wave off_track** |
| L12P10 | 12 | 0.10 | 0.25 | 70.2 | 36.6 | 13.6 | 20.0 | 0.83 | none |
| L16P10 | 16 | 0.10 | 0.25 | 71.5 | 36.6 | 14.9 | 19.9 | 1.03 | none |
| **L16P10G** | 16 | 0.10 | 0.20 | **72.0** | 37.2 | 14.8 | 20.0 | 0.82 | none |
**This is where prediction pays off:** at lat_accel 16 the car leaves the track on the wave WITHOUT prediction (L16), and stays
on it WITH prediction (L16P10). Prediction makes faster curves stable, and faster curves bring time points (12.6 -> 14.8).
With prediction a shorter lookahead (0.20) also works and tracks better. New best **72.0** (old 70.3).
Per path now: straight 11.6 m/s (at the ceiling), wave 11.0 (ceiling 11.9), lane 11.4 (ceiling 11.4), circle 10.5 (ceiling 14.4).
Watch: stop errors 4.6-4.7 m on straight/wave/lane, close to the 5 m limit.
Next: sweep p3 around L16P10G (lat 20/25, predict 0.15, gain 0.15).
