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
