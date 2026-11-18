# Personal Log — THRSimSimple

My own learning log. Each entry: what I did, why, what I saw, what I learned.

## Goal

Write a C++ ROS 2 driver (`my_driver`) that follows four paths (`straight`, `wave`,
`lane_change`, `circle`), stops at the finish node, and scores clearly higher than the
Python demo (about 62/100).

## Setup notes

- Repo location: `/home/sigma/Desktop/pleng/NTHU-Racing_THRSimSimple`
  (the README says `~/THRSimSimple`; I use my real path instead).
- ROS 2 Humble is installed at `/opt/ros/humble`.
- Earlier work was backed up to `/home/sigma/Desktop/pleng/THRSimSimple_backup_2026-11-18/`
  and the repo was reset to commit `df29cae` to start fresh.

## Steps

(Entries are added below as I complete each step.)

### 2026-11-18 — Step 1: Build the workspace

**Goal:** compile the simulator packages and the demo driver so ROS can find them.

**Commands (final working version):**

```bash
cd ~/Desktop/pleng/NTHU-Racing_THRSimSimple
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

**Why each line:**
- `cd` to the repo root: colcon searches for packages under the current folder.
- `source /opt/ros/humble/setup.bash`: loads ROS 2 into this terminal (needed in every new terminal).
- `colcon build --symlink-install`: generates code for the messages (`VehCtrl`, `VehState`, `RefPath`) and installs the simulator and demo driver. `--symlink-install` only helps Python; C++ always needs a rebuild after changes.
- `source install/setup.bash`: makes the newly built packages visible to `ros2 run`.

**Problem hit:** first build failed with `ModuleNotFoundError: No module named 'em'` in `thr_sim_msgs`.
- Cause: Anaconda's `python3` was first on `PATH`, so ROS's build tools ran under Conda Python instead of the system Python 3.10. Conda's Python does not have `empy` (`em`).
- Check: `which -a python3` must list `/usr/bin/python3` first; `python3 -c "import em"` must succeed.
- Fix: `conda deactivate` (and strip anaconda from `PATH` if needed), then `rm -rf build install log` to clear the partial build, and rebuild.
- Tip: `conda config --set auto_activate_base false` stops new terminals starting in `(base)`.

**Result:** `Summary: 3 packages finished [9.29s]` — `thr_sim_msgs` (7.5 s), `demo_driver`, `thr_sim`. No failures.

**Learned:** ROS build problems are often environment problems (wrong Python on `PATH`), not code problems. Always check `which python3` first.

### 2026-11-18 — Step 2: Run the demo driver and simulator (baseline)

**Goal:** watch a working driver so I understand the loop and the baseline to beat.

**Commands:**

```bash
# Terminal 1 (driver, leave running)
cd ~/Desktop/pleng/NTHU-Racing_THRSimSimple
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run demo_driver driver

# Terminal 2 (simulator)
cd ~/Desktop/pleng/NTHU-Racing_THRSimSimple
./run_sim.bash        # choose path, click Start
```

**Why:** the simulator only publishes `/path` and `/veh_state`; it needs a driver
publishing `/veh_ctrl` before it will run. The demo shows the whole loop working.

**Result (path = straight, 1 run):**
- Vehicle and Driver both showed "connected"; state DONE, progress 100 %.
- Run time 20.44 s for a ~60 m path, so average speed is about 3 m/s.
- Stopped at x = 60.56, i.e. 0.56 m past the finish line (inside the 5 m free zone).
- Final CTE -0.011 m, RMS CTE 0.037 m (limit is +/-2.0 m), so tracking is excellent.
- Plots: CTE flat near 0; steering is small noise (simulated actuator noise).
- Exact point breakdown: not recorded yet (check the "Run results" tab).

**How to read the screen:** the red line is the finish, the dotted part after it is the
run-out (overshoot margin), the light-green band is the +/-2 m off-track corridor.
Solid plot lines = commanded, dashed = actual.

**Learned:**
- Tracking and stop are already near full marks for the demo; the missing points are
  in **time** (v_eq ~3 m/s gives ~4/40). The goal is to go much faster without losing
  tracking or the stop.
- A stop of 0.56 m past the line means braking distance is small at 3 m/s; at higher
  speed I must start braking earlier.

### 2026-11-18 — Step 2b: Demo baseline on all four paths

**Goal:** record the exact demo-driver scores per path (single run each, 3 m/s).

| Path | Result | Track /40 | Time /40 | Stop /20 | Score /100 | Stop err (m) |
|---|---|---:|---:|---:|---:|---:|
| straight | stopped | 39.6 | 4.0 | 20.0 | 63.5 | +0.47 |
| wave | stopped | 37.2 | 3.9 | 20.0 | 61.1 | +0.62 |
| lane_change | stopped | 38.9 | 3.9 | 20.0 | 62.9 | +0.62 |
| circle | stopped | 37.9 | 3.9 | 20.0 | 61.8 | +0.48 |

**Average score: 62.3/100.**

**Observations:**
- All four runs ended `stopped`, every stop was within ~0.6 m of the finish line.
- Tracking is already 37-40 of 40, and stop is a full 20/20 everywhere.
- Time is only ~4/40 on every path (speed ~3 m/s; full marks need 30 m/s).
- Circle: the car completed one lap and stopped at the start/finish point (it did not
  stop immediately), because the demo tracks progress through ordered nodes.

**Takeaway / target:** ~56 of the 62 points are already secured; the whole opportunity
is the **time score** (~36 points available). Raising speed is what matters, but
only if tracking and the stop survive (README: demo at 15 m/s scores ~21).
Baseline to beat: **62.3**.

### 2026-11-18 — Step 2c: Simulator terminal log (extra baseline detail)

Source: terminal output of `./run_sim.bash` for the same demo-driver runs.

| Path | v_eq (m/s) | RMS CTE (m) | Run time (s) |
|---|---:|---:|---:|
| straight | 2.96 | 0.022 | 20.25 |
| wave | 2.94 | 0.139 | 20.87 |
| lane_change | 2.94 | 0.053 | 20.56 |
| circle | 2.93 | 0.106 | 32.19 |

**Observations:**
- v_eq is ~2.95 m/s on every path, matching the demo's constant 3 m/s command.
  Time score = 40 x v_eq / 30, so ~3.9/40. Doubling v_eq to ~6 would only add ~4 points;
  reaching 15 m/s would give 20/40.
- Wave has the largest tracking error (RMS 0.139 m), then circle (0.106 m): curved paths
  are where tracking will degrade first as I raise the speed.
- Repeated straight runs vary slightly (63.2 / 63.3 / 63.5) because of simulated actuator
  noise, so one run is not enough to compare changes; use `./evaluate.bash -n 3`.
- A run reported "discarded without scoring" when I pressed Start again before the
  first run finished: starting/resetting mid-run aborts it (no score, not a failure).
- Evaluation end: sim publishes an empty path ("driver should stop"), as the README says.
- Environment note: this terminal showed `(base)`. The simulator still ran, but
  anything that builds with colcon needs `conda deactivate` first (see Step 1).

### 2026-11-18 — Step 3a: Create the `my_driver` package

**Goal:** make an empty C++ ROS 2 package that my controller will live in.

**Command:**

```bash
cd ~/Desktop/pleng/NTHU-Racing_THRSimSimple
source /opt/ros/humble/setup.bash
source install/setup.bash        # so ros2 pkg create can find thr_sim_msgs
ros2 pkg create my_driver --build-type ament_cmake \
  --dependencies rclcpp std_msgs thr_sim_msgs
```

**Why:**
- `--build-type ament_cmake`: the homework requires a C++ package, not Python.
- `--dependencies rclcpp std_msgs thr_sim_msgs`: `rclcpp` is the ROS 2 C++ library,
  `std_msgs` gives `Empty` (the `/reset` message), `thr_sim_msgs` gives `RefPath`,
  `VehState`, `VehCtrl`. This adds them to both `package.xml` and `CMakeLists.txt`.

**Result:** created `my_driver/` with `package.xml`, `CMakeLists.txt`, `src/`, `include/my_driver/`.
Checked `package.xml` and `CMakeLists.txt`: all three dependencies are present.
No executable yet; nothing to build until `src/driver_node.cpp` exists.

**Mistakes / learned:**
- A typo (`~cd` instead of `cd`) gave "Command '~cd' not found"; the line before it
  was cut off in my paste, so I re-pasted partial commands. Paste whole blocks.
- Re-running `ros2 pkg create` gave "The directory already exists" — that is the tool
  refusing to overwrite, not a failure. The first run had already worked.

### 2026-11-18 — Step 3b: Skeleton driver written and built

**Goal:** a C++ node with all topic plumbing but no controller yet (publishes zero speed).

**What I did:**
- Typed `my_driver/src/driver_node.cpp` (81 lines): `Driver` node with subscriptions to
  `/path` (transient-local QoS, depth 1), `/veh_state`, `/reset`; publisher on `/veh_ctrl`;
  a 50 ms (20 Hz) timer calling `control()`; `main()` that spins the node.
- `CMakeLists.txt`: added `find_package(geometry_msgs REQUIRED)`, `add_executable(driver ...)`,
  `cxx_std_17`, `ament_target_dependencies(...)`, `install(TARGETS driver ...)`.
- `package.xml`: added `<depend>geometry_msgs</depend>` (path nodes are `geometry_msgs::msg::Point`).

**Why the design:**
- Transient-local `/path`: the sim publishes the path once; a late-starting driver still gets it.
- Timer-driven publishing (not callback-driven): commands must keep flowing at 20 Hz, because
  the sim stops the car after `cmd_timeout` = 0.5 s of silence.
- `on_reset` clears the pose and progress but keeps the path (`/path` and `/reset` can arrive in either order).
- `std::optional<VehState>` = "no pose yet"; empty/invalid path or no pose gives zero speed.

**Problem hit:** first build failed with `undefined reference to 'main'`.
- Cause: `driver_node.cpp` was 0 bytes — the code was in the editor but not saved.
- Check: `wc -l my_driver/src/driver_node.cpp` (should not be 0). Fix: save (Ctrl+S) and rebuild.

**Build:** `colcon build --symlink-install --packages-select my_driver` ->
`Summary: 1 package finished [14.9s]`.

**Learned:** the "undefined reference to main" linker error means the file compiled but contains
no `main`. Always check the file is saved. C++ needs a rebuild after every change
(`--symlink-install` does not help compiled code).

**Review notes:** file matches the README skeleton; nothing missing. `progress_index_` is stored
but unused until the controller exists.

### 2026-11-18 — Step 4: Run the skeleton driver with the simulator

**Goal:** verify the ROS plumbing works before writing any control logic.

**Commands:**

```bash
# Terminal 1
ros2 run my_driver driver
# Terminal 2
./run_sim.bash                      # select straight, click Start
# Terminal 3 (must source ROS + workspace first)
ros2 topic info /path --verbose
ros2 topic echo /veh_ctrl --once
```

**Why:** with only zero commands, a connected driver plus a stationary car proves
subscriptions, publisher, timer and QoS are all correct. Any later problem is then the
controller, not the setup.

**Result:**
- `/path`: publisher `sim_ctrl` and subscriber `my_driver`, both RELIABLE + TRANSIENT_LOCAL
  (QoS matches, so a late-started driver still receives the path).
- `/veh_ctrl`: `velocity: 0.0`, `steer: 0.0` (stamp populated), as expected for the skeleton.
- Simulator: after Start, the car stayed still.

**Mistakes / learned:**
- A new terminal has no ROS loaded: `ros2: command not found` just means run
  `source /opt/ros/humble/setup.bash` and `source install/setup.bash` first.
- A stray `~` before a command (`~ros2`) gives "command not found" too.
- `ros2 topic info --verbose` is a quick way to check QoS compatibility between nodes.

### 2026-11-18 — Step 5: First real controller (written by Claude under time pressure)

**Context:** only ~1 hour left for learning + control + slides, so Claude wrote the controller
and I read/run/tune it instead of typing it.

**Facts from `sim.yaml` / path generator that drive the design:**
path node spacing 0.5 m; wave amp 3 m, wavelength 30 m (tightest curve ~7.6 m radius);
circle radius 15 m; max_decel 6 m/s^2, max_accel 20; steering rate 1 rad/s; off-track
limit 2 m; stop is full marks within 5 m of the finish; time limit 60 s.

**Controller (`my_driver/src/driver_node.cpp`):**
1. *Where am I:* cumulative arc length `s` of the path; project the car onto the nearest
   segment, searching only forward from the last progress (80-node window). This is why the
   circle (start == finish) cannot jump to its finish.
2. *Steering:* pure pursuit, `delta = atan(2 L sin(alpha) / ld)`, L = 2.5 m, target point `ld`
   metres further along the path, `ld = 2.5 + 0.4 * v_actual` (longer lookahead when faster),
   clamped to +/-0.6 rad. Uses `/veh_actual` for the real speed.
3. *Speed profile:* at every node ahead the allowed speed is `v <= sqrt(lat_accel / kappa)` in
   curves and `v <= sqrt(2 * brake * distance)` for braking; command the smallest.
   Curvature `kappa` comes from heading change over +/-2 nodes.
4. *Stopping:* plan to stop `stop_aim` = 1.5 m past the finish (free zone is 5 m, and time stops
   counting when the car is at rest), command 0 once `remaining <= 0`.
5. Empty/invalid path -> zero command; `/reset` clears pose/speed/progress but keeps the path.

**Tunable without rebuilding** (`--ros-args -p name:=value`):
`cruise_speed` 12, `lat_accel` 3.0, `brake_decel` 3.5, `stop_aim` 1.5,
`lookahead_base` 2.5, `lookahead_gain` 0.4.

**Build:** `colcon build --symlink-install --packages-select my_driver` with
`-Wall -Wextra -Wpedantic` -> finished, no warnings.
Not yet run in the simulator (Claude's session cannot use the ROS network).

**Why these defaults are conservative:** a run that goes off-track/overruns/times out loses
all time and stop points, so first get all four paths `stopped`, then raise speed.

### 2026-11-18 — Step 6: Slide report

**Goal:** 5-minute team report for my team lead and team, answering four questions:
(1) what score, (2) what method, (3) what issues, (4) how to improve — plus a beginning
that teaches the background and parameters.

**Deck:** https://claude.ai/artifact/QaaeQabr3SQxCSCnxPsSZw (11 slides, private until shared).
Order: cover; the task; scoring; simulator numbers; steering method; speed method;
the six parameters; score (Q1); issues (Q3); improvements (Q4); what I learned.
Speaker notes on every slide.

**Still to fill before the meeting (marked `[__]` in the deck):** my scores per path
(slide "score"), my average speed and parameter settings, the 4th issue card (tuning), my name/date on the cover.

## What I have learned so far (running list)

**ROS 2 / environment**
- A node subscribes to and publishes on topics; simulator and driver never share code.
- QoS must match between publisher and subscriber: `/path` is RELIABLE + TRANSIENT_LOCAL so a late driver still gets it
  (check with `ros2 topic info /path --verbose`).
- Publish at a steady 20 Hz from a timer: the sim zeroes the car after 0.5 s of silence.
- Every new terminal needs `source /opt/ros/humble/setup.bash` and `source install/setup.bash`.
- Conda `(base)` on PATH breaks ROS builds (`No module named 'em'`): check `which python3` first.
- A linker error "undefined reference to main" can just mean the source file is empty/unsaved.
- C++ needs a rebuild after every change (`--symlink-install` only helps Python).

**Control**
- Pure pursuit: `delta = atan(2 L sin(alpha) / ld)`; longer lookahead at higher speed is steadier but cuts corners.
- Speed profile: `v <= sqrt(lat_accel / kappa)` in curves, `v <= sqrt(2 a d)` for braking; use the smallest ahead.
- Progress must only move forward, otherwise the circle (start == finish) confuses the controller.
- The stop has slack (5 m free zone) which can be traded for speed.

**Scoring / method**
- Demo = tracking ~38/40, stop 20/20, time only ~4/40, so speed is the main opportunity.
- One failed run (off-track/overrun/timeout) loses the time AND stop points: robustness beats peak speed.
- Noise makes single runs vary by ~0.3 points: compare with `./evaluate.bash -n 3`, change one parameter at a time.

### 2026-11-18 — Step 7: First evaluation of my C++ driver (`./evaluate.bash -n 3`)

**Settings (defaults):** cruise_speed 12, lat_accel 3.0, brake_decel 3.5, stop_aim 1.5,
lookahead_base 2.5, lookahead_gain 0.4.

**Result: overall 66.6/100** (demo baseline 62.3). All 12 runs `stopped`, none off-track.
Report: `eval_results/eval_20261118_195322.json` (+ .png).

| Path | Score | Track /40 | Time /40 | Stop /20 | v_eq (m/s) | Stop err (m) |
|---|---:|---:|---:|---:|---:|---:|
| straight | 68.2 | 38.4 | 9.7 | 20.0 | 7.31 | 0.61 |
| wave | 64.3 | 36.1 | 8.2 | 20.0 | 6.13 | 0.71 |
| lane_change | 67.1 | 38.0 | 9.1 | 20.0 | 6.83 | 0.58 |
| circle | 66.7 | 38.9 | 7.8 | 20.0 | 5.81 | 0.81 |
| **Overall** | **66.6** | 37.9 | 8.7 | 20.0 | 6.5 mean | |

**Observations:**
- The driver worked first time: no tuning crashes, all four paths finished and stopped.
- Tracking is excellent (RMS CTE 0.05-0.21 m, limit 2 m), so there is a lot of error margin to spend on speed.
- Time points doubled (4 -> 8.7) because average speed went 3 -> 6.5 m/s.
- v_eq (6-7 m/s) is well below cruise_speed 12: v_eq is path length / total time, so the
  acceleration phase and the planned braking (3.5 m/s^2) eat much of a 60 m path. Raising
  cruise_speed alone gives diminishing returns; brake_decel and stop_aim matter too.
- Wave is the weakest path (error 0.21 m from tight curves); stop errors are +0.6-0.85 m (limit for full marks is 5 m).

**Next:** raise cruise_speed, lat_accel, brake_decel and stop_aim together, one step at a time, and re-run `-n 3`.

### 2026-11-18 — Step 8: Automated parameter sweep (planned)

**Goal:** tune speed as far as possible while keeping every run `stopped`.

**Method:** `scripts/sweep.bash` starts the driver with each parameter set, runs
`./evaluate.bash --headless -n 2`, stops the driver, and writes a one-line summary per set to
`eval_results/sweep/summary.txt` (plus one JSON per set). Baseline reference: defaults = 66.6.
Run it with `./scripts/sweep.bash` (no other driver running, workspace built).

**Planned sets** (defaults: cruise 12, lat 3.0, brake 3.5, aim 1.5):

| Set | cruise | lat_accel | brake_decel | stop_aim | other |
|---|---:|---:|---:|---:|---|
| B | 16 | 4.0 | 4.5 | 2.5 | |
| C | 20 | 5.0 | 5.0 | 3.0 | |
| D | 25 | 6.0 | 5.5 | 3.5 | |
| E | 30 | 7.0 | 5.5 | 3.5 | |
| F | 20 | 8.0 | 5.0 | 3.0 | isolates the cornering limit |
| G | 25 | 6.0 | 5.5 | 3.5 | lookahead_gain 0.25 |

**Why:** each step raises speed and brake/stop aggressiveness together; the car can brake at
most 6 m/s^2 and a stop within 5 m of the finish is free, so `brake_decel` stays under 6 and
`stop_aim` under ~4. Results to be recorded below as each set finishes.

## Study notes in plain language (slides 2-7)

**The loop (slide 2).** The simulator is the world; my node is the driver. Every 50 ms I read the car pose
(x, y, heading) and the path, decide two numbers (speed, steering angle) and publish them. If I stay silent
0.5 s the car stops (dead-man switch), so I publish even when idle. `/path` is sent once, so I subscribe with
transient-local QoS (the topic remembers its last message). `/reset` = new run: forget progress, keep the path.
Empty path = no task: command zero speed.

**Scoring (slide 3).** Tracking 40 = `40 x completion x (1 - RMS_error/2 m)`: 0.1 m error -> 38/40.
Time 40 = `40 x min(v_eq,30)/30`: 3 m/s -> 4, 6.5 m/s -> 8.7, 30 m/s -> 40. Stop 20 = full inside 5 m.
Any failed run (off-track, overrun, timeout) gets 0 for time and stop.

**Simulator numbers (slide 4).** Car limits (L 2.5 m, steer +/-0.6 rad at 1 rad/s, brake 6 m/s^2) bound what is
possible; scoring numbers (2 m, 5 m, 30 m/s) say what is worth it; path numbers (0.5 m spacing, wave 3 m x 30 m,
circle R 15 m) shape the curves; safety numbers (0.5 s, 60 s) limit mistakes.
Worked examples: braking from 12 m/s at 3.5 m/s^2 needs `v^2/(2a)` = 20.6 m. Wave curvature max ~0.13 1/m, so
with lat_accel 3 the corner speed limit is `sqrt(3/0.13)` = 4.8 m/s.

**Pure pursuit (slide 5).** Aim at a "carrot" `ld` metres ahead on the path. `alpha` = angle between where the car
points and the carrot. Steering `delta = atan(2 L sin(alpha)/ld)`. Bigger alpha -> turn more; longer ld -> gentler.
Short ld tracks tightly but wiggles; long ld is smooth but cuts corners; so `ld = 2.5 + 0.4 v`.

**Speed profile (slide 6).** Three limits, take the smallest: curves `v <= sqrt(lat_accel/kappa)`, braking
`v <= sqrt(2 a d)` (also looks ahead so I slow before a curve), stop at the finish (aim `stop_aim` past the line).

**Parameters (slide 7).** Speed: cruise_speed, lat_accel. Braking/stop: brake_decel, stop_aim.
Steering: lookahead_base, lookahead_gain. All tunable with `--ros-args -p name:=value`.

**Sweep script bug (2026-11-18 ~20:05):** first run of `scripts/sweep.bash` stopped with
`/opt/ros/humble/setup.bash: line 8: AMENT_TRACE_SETUP_FILES: unbound variable`.
Cause: the script used `set -u` (error on unset variables) and ROS's setup files read variables that may be unset.
Fix: `set +u` while sourcing the ROS and workspace setup files, then `set -u` again.
Lesson: do not use `set -u` around `source /opt/ros/.../setup.bash`.

### 2026-11-18 — Extra requirement from team lead (received ~20:08)

Team lead also wants: **speed higher than 12 m/s** and to **develop a new control**.
Open question to confirm with the lead: is "12 m/s" the peak/cruise speed or the average `v_eq` (path length / run time)?

**My feasibility estimate (path 60 m, max brake 6 m/s^2, stop within the 5 m free zone):**
- Peak speed above 12 m/s: feasible on straights (sets B-E in the sweep use cruise 16-30).
- Average `v_eq` above 12 m/s: not physically possible on a 60 m path. Accelerate to v then brake at <= 6 m/s^2:
  with 8 m/s^2 accel the best case is ~21 m/s peak, ~6.1 s, `v_eq` ~ 9.8; with 15 m/s^2 accel ~ 5.5 s, `v_eq` ~ 10.9.
  (Hard limit comes from braking: ~65 m available including the 5 m free zone.)
- So realistic target: `v_eq` ~ 9-10 on straight, lower on wave/circle (curve limits).

## Code walkthrough: `my_driver/src/driver_node.cpp`

Structure (top to bottom): helpers (`wrap`, `Pt`, `Location`) -> `Driver` class:
constructor (parameters + 4 connections + 20 Hz timer) -> `on_path` (store path, arc length `s_`, curvature `kappa_`)
-> `on_reset` -> `locate` (forward-only projection) -> `point_at` (carrot) -> `control` (steering + speed + publish) -> `main`.

- **Data stored once per path** (`on_path`): points `pts_`, cumulative distance `s_`, curvature `kappa_` (heading change over +/-2 nodes divided by arc length).
  Doing this once avoids recomputing 20 times a second.
- **`locate`**: search nearest node only in `[progress_, progress_+80]` (forward-only) so the circle cannot jump from start to finish;
  then project the car onto the two nearby segments for a smooth distance `s` along the path.
- **`control` steering**: `ld = clamp(2.5 + 0.4*v_actual)`, carrot = `point_at(s+ld)`, `alpha = wrap(atan2(dy,dx) - yaw)`,
  `steer = clamp(atan2(2 L sin(alpha), ld))`.
- **`control` speed**: start from cruise; for each node ahead up to the braking horizon, `v = min(v, sqrt(vc^2 + 2 a dist))`
  where `vc = sqrt(lat_accel/kappa)`; then `v = min(v, sqrt(2 a (remaining + stop_aim)))`; 0 once `remaining <= 0`.
- **Always publish** at the end, even with no task (zeros), because the sim stops the car after 0.5 s of silence.

### 2026-11-18 — Step 8 results: parameter sweep (2 runs per path, 8 runs per set)

Baseline (defaults, 3 runs/path): **66.6** (cruise 12, lat 3.0, brake 3.5, aim 1.5; mean v_eq 6.5).
Full summary: `eval_results/sweep/summary.txt`; per-set JSON/PNG/logs in `eval_results/sweep/`.

| Set | cruise | lat | brake | aim | Overall | Track | Time | Stop | Max CTE (m) | Failures | v_eq straight / wave / lane / circle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| base | 12 | 3.0 | 3.5 | 1.5 | 66.6 | 37.9 | 8.7 | 20.0 | 0.4 | none | 7.3 / 6.1 / 6.8 / 5.8 |
| B | 16 | 4.0 | 4.5 | 2.5 | 66.7 | 37.1 | 9.5 | 20.0 | 0.51 | none | 8.1 / 6.8 / 7.3 / 6.5 |
| C | 20 | 5.0 | 5.0 | 3.0 | 67.0 | 36.8 | 10.3 | 20.0 | 0.72 | none | 8.5 / 7.5 / 7.8 / 7.1 |
| **D** | 25 | 6.0 | 5.5 | 3.5 | **68.5** | 37.1 | 11.4 | 20.0 | 0.65 | none | 8.9 / 9.0 / 8.6 / 7.6 |
| E | 30 | 7.0 | 5.5 | 3.5 | 67.7 | 35.9 | 11.8 | 20.0 | 0.92 | none | 8.9 / 9.5 / 8.9 / 8.0 |
| F | 20 | 8.0 | 5.0 | 3.0 | 68.0 | 37.1 | 10.9 | 20.0 | 0.83 | none | 8.4 / 7.9 / 8.2 / 8.3 |

**Findings:**
- No failures in any set: every run `stopped`, max cross-track error stayed under 1 m (limit 2 m).
- Best so far: **D = 68.5** (+1.9 over baseline). Time points rose from 8.7 to 11.4 while tracking fell only ~0.8.
- Diminishing returns: E (cruise 30, lat 7) has the highest time points (11.8) but tracking drops to 35.9, so it ends below D.
- Average speed v_eq tops out around 9-9.5 m/s even with cruise 30: confirms the physical ceiling
  (~10 m/s: limited by 6 m/s^2 braking over a 60 m path and the speed-loop lag), so the time score can only reach ~12/40 here.
- F vs C (lat_accel 5 -> 8, same cruise): +1.0 overall, mostly circle and lane_change: cornering limit was holding those back.
- Tuning story for the deck: raising speed costs tracking and, past D, the extra time points no longer pay for it.

| **G** | 25 | 6.0 | 5.5 | 3.5 (+lookahead_gain 0.25) | **68.8** | 37.4 | 11.4 | 20.0 | 0.61 | none | 8.9 / 9.0 / 8.7 / 7.6 |

**G (D with lookahead_gain 0.4 -> 0.25) is the best set: 68.8**, +2.2 over the baseline 66.6 and +0.3 over D.
Tracking improved (37.1 -> 37.4) with a shorter lookahead, mostly on wave (66.2 -> 68.8). Differences under ~0.5 are within noise (2 runs/path).

### 2026-11-18 — Step 9: Sweep round 2 (planned, ~20:18)

**Goal:** (a) confirm the best set G with a safer stop margin (G's largest stop error was 4.6 m, close to the 5 m free zone),
(b) tune a little further around G, (c) measure run-to-run noise by repeating one set.
Script: `./scripts/sweep2.bash` -> `eval_results/sweep2/summary.txt`. All sets: cruise 25, brake 5.5 unless stated.

| Set | lat_accel | brake_decel | stop_aim | lookahead_gain | lookahead_base | Purpose |
|---|---:|---:|---:|---:|---:|---|
| H | 6.0 | 5.5 | 3.0 | 0.25 | 2.5 | G with a safer stop (confirmation) |
| I | 6.0 | 5.5 | 3.0 | 0.15 | 2.5 | shorter lookahead at speed |
| J | 7.0 | 5.5 | 3.0 | 0.25 | 2.5 | faster cornering |
| K | 6.0 | 5.8 | 3.0 | 0.25 | 2.5 | brake closer to the 6 m/s^2 limit |
| L | 6.0 | 5.5 | 3.0 | 0.25 | 2.0 | shorter base lookahead |
| H2 | 6.0 | 5.5 | 3.0 | 0.25 | 2.5 | exact repeat of H: measures noise |

**Schedule (updated ~20:19):** meeting is at 21:00 Taiwan time; leave at 20:50. Tuning stops at 20:30; 20:30-20:50 = final slide numbers + rehearsal.

### 2026-11-18 — Step 10: Simplified the deck, split results in three

Cover now: "Nahathai · 18 November 2026 · Team meeting".
Deck is now 13 slides: cover; task; scoring; six simulator limits; steering; speed; parameters;
**result 1 (first run, defaults 66.6)**; **result 2 (sweep 1, up to 68.8)**; **result 3 (sweep 2, placeholders until it finishes)**;
issues; improvements; five takeaways. Removed the old single score slide.
Simplification: shorter on-slide text, formulas and examples moved into the speaker notes, tables trimmed (simulator limits 9 -> 6 rows).
Note: the deck page tool blocked one publish because the page had re-saved `deck.json` (key reformat only);
I re-read it and re-applied my change. Avoid editing the deck page while Claude is publishing.

### 2026-11-18 — Step 9 results so far: sweep round 2 (2 runs per path; `eval_results/sweep2/`)

| Set | Change from G (cruise 25, lat 6, brake 5.5, aim 3.5, gain 0.25) | Overall | Time /40 | Max CTE | Result |
|---|---|---:|---:|---:|---|
| H | stop_aim 3.0 | 68.9 | 11.5 | 0.76 m | no failures; same score as G with a safer stop |
| I | lookahead_gain 0.15 (+ aim 3.0) | **47.0** | 6.7 | 2.06 m | **FAILED: 3 runs off_track (straight, wave x2)** |
| J | lat_accel 7 (+ aim 3.0) | 68.7 | 11.4 | 0.75 m | no failures; no gain over H |
| K | brake_decel 5.8 (+ aim 3.0) | **69.8** | 12.3 | 0.64 m | no failures; best so far; straight v_eq 10.2 |

**Findings:**
- **I is the key failure:** lookahead_gain 0.15 makes the lookahead too short at 25 m/s (lookahead = 2.5 + gain x v = 6.25 m at 25 m/s instead of 8.75 m),
  steering becomes unstable and the car leaves the 2 m corridor. One failed run costs all time and stop points (47.0 vs 68.9).
  Lesson: the lookahead must grow enough with speed; this is the "speed against staying on track" issue for slide 11.
- Lower stop_aim (3.5 -> 3.0) cost nothing: H = 68.9 vs G = 68.8 (within noise) and the stop is safer.
- Braking closer to the limit (5.5 -> 5.8 of 6.0 m/s^2) gave +0.9 overall and raised straight/lane_change speed above 10 m/s:
  braking was the real bottleneck for average speed.
- Raising lat_accel 6 -> 7 gave nothing (J ~ H): cornering limit is no longer the constraint.
- **Caution on K:** its largest stop error was **4.97 m**, only 0.03 m inside the 5 m free zone (H: 4.04, J: 3.91). Beyond 5 m each metre costs 5 points.
  Round 3 (`./scripts/sweep3.bash`, after round 2 ends): M = K with stop_aim 2.5 (safer stop), K2 = exact repeat of K (noise check).

| L | lookahead_base 2.0 (+ aim 3.0) | 67.7 | 11.2 | 1.06 m | no failures, but worse tracking: confirms a too-short lookahead hurts |

## Study notes: what the tuning results mean (understanding, 20:28)

1. **Time is where the points were.** Tracking (~38/40) and stop (20/20) were already near full; the demo's 62.3 -> 69.8 came from the time column
   (each extra m/s of average speed = 40/30 = 1.33 points).
2. **Speed stops paying (set E).** Cruise 30 had the most time points but tracking fell (35.9): swinging wider in curves loses tracking faster than speed earns time.
3. **Braking was the real bottleneck (set K).** The car brakes at 6 m/s^2 at most, so from 20 m/s it needs ~33 m of a 60 m path. Planning with
   brake_decel 5.8 instead of 5.5 starts braking later, keeps speed longer: +0.9 points and straight v_eq > 10 m/s. lat_accel 6 -> 7 (J) did nothing.
4. **Short lookahead is unstable at speed.** ld = 2.5 + gain*v. At 25 m/s: gain 0.25 -> 8.75 m (fine), gain 0.15 -> 6.25 m (off-track, score 47),
   base 2.0 -> worse error (L). Steering rate is limited to 1 rad/s, so over-reacting overshoots the 2 m corridor. One failed run loses all time + stop points.
5. **Stop margin.** Later braking and a larger stop_aim both push the stop point further past the line; K reached 4.97 m of the 5 m free zone.
6. **Noise.** Same settings differ run to run (simulated actuator noise); H vs H2 measures it. Treat smaller gaps as ties.

| H2 | exact repeat of H | 69.4 | 11.5 | 0.44 m | no failures; H (68.9) vs H2 (69.4) = **noise is about 0.5 points** |

**Round 2 complete (20:27).** Final table (2 runs per path, 8 runs per set; max stop error in brackets):
H 68.9 (4.04 m), I 47.0 (3.46 m, 3 off-track runs), J 68.7 (3.91 m), K 69.8 (4.97 m), L 67.7 (4.00 m), H2 69.4 (3.94 m).
Best score K = 69.8, but K vs H/H2 (68.9/69.4) is only ~0.4-0.9 above noise and K's stop margin is 0.03 m.
Round 3 (M = K with stop_aim 2.5, K2 = repeat of K) is ready: `./scripts/sweep3.bash`.

**Deck update blocked (20:28):** my publish of the "Sweep 2" slide (real numbers) and the updated issues card to the artifact
was denied by a permission check. The local files are edited (scratchpad deck folder) but the online deck still shows the
placeholder `[__]` version of slide 10 and the older text on the issues card. Waiting for the user's decision.

**Deck update published (20:29):** after the user approved a retry, the "Sweep 2" slide (real numbers: best 69.8, one failure) and the
updated issues card (set I: 3 runs left the track) are now online (deck version 10).

## Code snippets for the explanation (`my_driver/src/driver_node.cpp`, line numbers as of 20:31)

1. Angle wrap (l.29): `double wrap(double a) {return std::atan2(std::sin(a), std::cos(a));}`
2. Path distance `s_` (l.91): `s_[i] = s_[i - 1] + std::hypot(pts_[i].x - pts_[i - 1].x, pts_[i].y - pts_[i - 1].y);`
3. Curvature (l.100): `kappa_[i] = ds > 1e-6 ? std::fabs(wrap(h2 - h1)) / ds : 0.0;`
4. Forward-only search (l.122, l.168): `const size_t hi = std::min(n - 1, progress_ + 80);` and `progress_ = std::max(progress_, loc.index);`
5. Lookahead (l.172): `const double ld = std::clamp(ld_base_ + ld_gain_ * std::fabs(v_actual_), ld_base_, 15.0);`
6. Carrot + angle (l.173-174): `point_at(loc.s + ld, loc.index)` and `alpha = wrap(atan2(target.y - y, target.x - x) - yaw)`
7. Steering (l.175): `steer = clamp(atan2(2.0 * wheelbase_ * sin(alpha), ld), -max_steer_, max_steer_);`
8. Curve limit + look-ahead braking (l.187-189): `vc = sqrt(a_lat_/kappa_[j])`; `v = min(v, sqrt(vc*vc + 2*brake_*dist))`
9. Finish braking (l.192): `v = min(v, sqrt(2.0 * brake_ * (remaining + stop_aim_)))`
10. Always publish (l.207): `publisher_->publish(msg);` is outside the `if`, so zero commands go out when there is no task.

### Round 3 (sweep3) first result, 20:31
M (K with stop_aim 2.5): overall 69.4 = track 37.1 + time 12.3 + stop 20.0, max CTE 0.76 m, no failures (v_eq: straight 10.1, wave 9.1, lane_change 10.0, circle 7.8).
Same time points as K (12.3) with a smaller stop_aim. K2 (repeat of K) is still running.

### 2026-11-18 — Step 9 results: sweep round 3 (`eval_results/sweep3/`, 2 runs per path)

| Set | Change | Overall | Time /40 | Max CTE | Max stop err | Failures |
|---|---|---:|---:|---:|---:|---|
| M | K with stop_aim 2.5 | 69.4 | 12.3 | 0.76 m | 4.51 m | none |
| K2 | exact repeat of K (stop_aim 3.0) | 69.5 | 12.4 | 0.59 m | 4.93 m | none |

**Findings:** K scored 69.8 and its repeat K2 69.5 (noise ~0.3). M (smaller stop_aim) scores the same within noise (69.4)
with 0.4 m more stop margin, so **M is the safer final choice**: cruise 25, lat_accel 6, brake_decel 5.8, stop_aim 2.5, lookahead_gain 0.25 (base 2.5).

### 2026-11-18 — Step 11: sweep round 4 (small, requested by user, ~20:35)

Base = M (cruise 25, lat 6, brake 5.8, aim 2.5, gain 0.25). Script: `./scripts/sweep4.bash` -> `eval_results/sweep4/summary.txt`.
| Set | Change from M | Question |
|---|---|---|
| N | brake_decel 5.9, stop_aim 2.0 | brake even closer to the 6 m/s^2 limit; smaller aim to keep the stop inside 5 m |
| O | lookahead_gain 0.30 | a longer lookahead at speed: steadier tracking? |
| P | cruise_speed 30 | higher ceiling now that braking is later |

**Deck:** added three code slides after the speed method slide (steering, speed profile, safety), numbered rows with code and explanation.

### 2026-11-18 — Step 12: Committed and pushed to GitHub (~20:35)

Commits on `main` (pushed to `origin` = github.com/nahathaiw/NTHU-Racing_THRSimSimple):
- `1ae422f` feat: add my_driver C++ pure-pursuit driver with speed profile and planned stop
- `a7493ae` docs: add personal log and parameter sweep scripts
Not committed on purpose: `build/`, `install/`, `log/`, `eval_results/` (ignored by `.gitignore`); results are recorded in this log instead.
Note: `package.xml` still has the default `TODO` description and license; fill them before submitting.

## Presentation outline for the experiments (what changed, what it showed)

1. **Demo (62.3):** fixed 3 m/s. Tracking and stop full, time ~4/40.
2. **First run, defaults (66.6):** my pure pursuit + speed profile, cruise 12. Time 8.7/40. Proof the method works: all 12 runs stopped.
3. **Sweep 1 (B-G, up to 68.8):** raise cruise, lat_accel, brake_decel, stop_aim together. Gains until D; E (cruise 30) lost tracking. G (shorter gain 0.25) best.
4. **Sweep 2 (H-L, best 69.8):** change one thing at a time. H = safer stop (no cost); I = gain 0.15 FAILED (3 off-track runs, 47.0);
   J = lat_accel 7 (no gain); K = brake 5.8 (best, +0.9, but stop error 4.97 m); L = base 2.0 (worse tracking); H2 = noise 0.5.
5. **Round 3 (M, K2):** M = K with stop_aim 2.5: 69.4 with 4.51 m stop error (safer); K2 = repeat of K: 69.5 (noise ~0.3). Chosen final: M.
6. **Round 4 (N, O, P):** brake 5.9, gain 0.30, cruise 30 (results pending).
Story: speed gives time points -> tracking cost -> braking is the bottleneck -> lookahead must grow with speed -> stop margin vs score -> noise limits what we can claim.

| N (round 4) | brake 5.9, aim 2.0 | 70.3 | time 12.8 | max CTE 0.58 m | straight v_eq 11.6 | new best so far (stop err: see summary) |

### 2026-11-18 — Step 13: Sweep 3 added to the deck (~20:40)

New slide "Sweep 3: a safer stop at the same score" (result 4 of 5): K 69.8 (stop err 4.97 m), K2 69.5 (4.93 m), M 69.4 (4.51 m).
Result slides renumbered "n of 5" (first run, sweep 1, sweep 2, sweep 3, sweep 4). Deck is now 17 slides; sweep 4 slide to be added when P finishes.
Round 4 so far (base M): N (brake 5.9, aim 2.0) 70.3, max stop err 4.75 m; O (gain 0.30) 70.1, max stop err 4.75 m; P (cruise 30) running.

### 2026-11-18 — Step 11 results: sweep round 4 (`eval_results/sweep4/`, 2 runs per path, base = M)

| Set | Change from M | Overall | Track | Time | Max CTE | Max stop err | Failures |
|---|---|---:|---:|---:|---:|---:|---|
| **N** | brake 5.9, stop_aim 2.0 | **70.3** | 37.5 | 12.8 | 0.58 m | 4.75 m | none |
| O | lookahead_gain 0.30 | 70.1 | 37.3 | 12.8 | 0.59 m | 4.75 m | none |
| P | cruise_speed 30 | 70.1 | 37.6 | 12.5 | 0.56 m | 4.57 m | none |

N, O, P all beat M (69.4) by ~0.7-0.9 but tie each other within noise (~0.5). N: straight v_eq 11.6 m/s (the highest of all tests).

## FINAL SETTINGS (chosen 20:41): N
`cruise_speed 25, lat_accel 6.0, brake_decel 5.9, stop_aim 2.0, lookahead_base 2.5, lookahead_gain 0.25`
Score journey: demo 62.3 -> first run 66.6 -> sweep 1 68.8 -> sweep 2 69.8 -> sweep 3 69.4 (safer) -> sweep 4 70.3.
Deck now 18 slides: added "Sweep 4" (result 5 of 5); parameters slide shows default -> final values.
Run command: `ros2 run my_driver driver --ros-args -p cruise_speed:=25.0 -p lat_accel:=6.0 -p brake_decel:=5.9 -p stop_aim:=2.0 -p lookahead_gain:=0.25`

### 2026-11-18 — Step 14: Why N won + live demo script (~20:43)

**Why set N scored best (70.3 vs M 69.4):** `brake_decel` 5.9 is just under the car's 6 m/s^2 limit, so the plan starts braking later and keeps speed longer
(straight average speed 10.1 -> 11.6 m/s); `stop_aim` 2.0 offsets the later braking so the stop stays inside the 5 m zone (worst 4.75 m).
Gain +0.9 = +0.5 time points (12.3 -> 12.8) + 0.4 tracking points (37.1 -> 37.5). Honest caveat: noise is ~0.5 and O/P score 70.1, so N, O, P are effectively tied.
Added slide "Why set N scored 70.3" (deck now 19 slides).

**Live demo:** `./scripts/demo_best.bash` (GUI, choose a path, click Start); `./scripts/demo_best.bash eval` (GUI evaluation, 1 run x 4 paths, ~1 minute);
`./scripts/demo_best.bash wave` (GUI preset to a path). It starts my_driver with the final parameters and stops it when the window closes.

### 2026-11-18 — Step 15: All parameters on every test slide + comparison slides (~20:46)

Every result slide now shows all six parameters (cruise, lat_accel, brake_decel, stop_aim, lookahead_gain, lookahead_base):
first run (line under table), sweep 1 (table has all six), sweep 2 / sweep 3 / sweep 4 (shared base line, each set changes only the item shown), why-best (final settings).
New slides "Every test and its parameters" 1 of 2 (Start, B-I) and 2 of 2 (J-P) list all 18 tests with all six parameters and the score. Deck is now 21 slides.

Full parameter table (cruise / lat / brake / aim / gain / base -> score):
Start 12/3.0/3.5/1.5/0.40/2.5 -> 66.6; B 16/4.0/4.5/2.5/0.40/2.5 -> 66.7; C 20/5.0/5.0/3.0/0.40/2.5 -> 67.0; D 25/6.0/5.5/3.5/0.40/2.5 -> 68.5;
E 30/7.0/5.5/3.5/0.40/2.5 -> 67.7; F 20/8.0/5.0/3.0/0.40/2.5 -> 68.0; G 25/6.0/5.5/3.5/0.25/2.5 -> 68.8; H 25/6.0/5.5/3.0/0.25/2.5 -> 68.9;
I 25/6.0/5.5/3.0/0.15/2.5 -> 47.0 (failed); J 25/7.0/5.5/3.0/0.25/2.5 -> 68.7; K 25/6.0/5.8/3.0/0.25/2.5 -> 69.8; L 25/6.0/5.5/3.0/0.25/2.0 -> 67.7;
H2 = H -> 69.4; K2 = K -> 69.5; M 25/6.0/5.8/2.5/0.25/2.5 -> 69.4; N 25/6.0/5.9/2.0/0.25/2.5 -> 70.3; O 25/6.0/5.8/2.5/0.30/2.5 -> 70.1; P 30/6.0/5.8/2.5/0.25/2.5 -> 70.1.
