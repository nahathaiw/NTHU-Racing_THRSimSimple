# Data flow

How data moves between the simulator, my driver and the evaluation scripts. For how the driver decides, see
[ARCHITECTURE.md](ARCHITECTURE.md).

## 1. The big picture

```mermaid
flowchart LR
    GUI["GUI / evaluate.bash<br/>(user clicks Start)"] --> SC
    subgraph SIM["Simulator"]
        SC["sim_ctrl<br/>path, reset, scoring"]
        VS["vehicle_sim<br/>physics + actuators"]
    end
    SC -- "/path (once, latched)" --> D
    SC -- "/reset" --> D
    SC -- "/reset" --> VS
    VS -- "/veh_state 50 Hz" --> D
    VS -- "/veh_actual 50 Hz" --> D
    D["my_driver"] -- "/veh_ctrl 20 Hz" --> VS
    VS -- "/veh_state" --> SC
    SC -- "/score, /sim_status" --> OUT["results: GUI + JSON + PNG"]
```

## 2. Topics

| Topic | Type | From -> to | Rate | QoS | Content |
|---|---|---|---|---|---|
| `/path` | `RefPath` | sim_ctrl -> driver | once per run (and empty when idle) | reliable, **transient-local**, depth 1 | ordered nodes (x, y) + `finish_index` |
| `/reset` | `std_msgs/Empty` | sim_ctrl -> vehicle_sim and driver | once per run | reliable, volatile, depth 10 | "start a new run" |
| `/veh_state` | `VehState` | vehicle_sim -> driver, sim_ctrl | 50 Hz | reliable, volatile | rear-axle `x`, `y`, `yaw` (map frame) |
| `/veh_actual` | `VehCtrl` | vehicle_sim -> driver | 50 Hz | reliable, volatile | **actual** speed and steering after the actuator loops |
| `/veh_ctrl` | `VehCtrl` | driver -> vehicle_sim | 20 Hz | reliable, volatile | **commanded** `velocity` [m/s], `steer` [rad] |
| `/score` | `Float64` | sim_ctrl -> consumers | once per run | reliable | total score 0 to 100 |
| `/sim_status` | `String` (JSON) | sim_ctrl -> consumers | once per run | reliable | tracking, time, stop, errors, result |

Why `/path` is transient-local: it is sent once, so the topic keeps the last message and a driver that starts late
still receives it. My subscription must use the same QoS or it never gets the path.

## 3. One run, in time order

```mermaid
sequenceDiagram
    participant U as User (GUI)
    participant S as sim_ctrl
    participant V as vehicle_sim
    participant D as my_driver
    Note over D: idle: publishes zero speed at 20 Hz
    U->>S: Start
    S->>V: /reset
    S->>D: /reset
    S->>D: /path (nodes + finish_index)
    loop 50 Hz
        V->>D: /veh_state, /veh_actual
    end
    loop 20 Hz
        D->>V: /veh_ctrl (velocity, steer)
    end
    V->>S: /veh_state (cross-track error, progress, rest check)
    Note over S: car at rest for 1 s, or off-track / overrun / timeout
    S->>U: /score + /sim_status
    S->>D: /path (empty = no task)
    Note over D: back to publishing zero speed
```

`/reset` and `/path` can arrive in **either order**, so the driver never wipes the path on reset: `on_reset()`
clears only the pose, the actual speed and the progress.

## 4. Inside the driver, per message

```mermaid
flowchart TD
    P["/path"] --> OP["on_path(): store points,<br/>compute s_ (arc length), kappa_ (curvature),<br/>progress_ = 0"]
    R["/reset"] --> OR["on_reset(): clear pose,<br/>actual speed, progress_"]
    X["/veh_state"] --> ST["state_ = latest pose"]
    A["/veh_actual"] --> VA["v_actual_ = real speed"]
    T["20 Hz timer"] --> C["control(): uses pts_, s_, kappa_,<br/>state_, v_actual_, parameters"]
    OP -.-> C
    OR -.-> C
    ST -.-> C
    VA -.-> C
    C --> O["publish /veh_ctrl"]
```

Callbacks only **store** data. All decisions happen in the timer, so the command rate is steady whatever the
message rates are.

## 5. Inside the simulator: command to motion

```mermaid
flowchart LR
    C["/veh_ctrl<br/>command"] --> TO{"command in the<br/>last 0.5 s?"}
    TO -- "no" --> Z["speed target = 0"]
    TO -- "yes" --> PV["speed PI loop<br/>accel max 20, decel max 6 m/s^2"]
    Z --> PV
    C --> PS["steering PI loop<br/>rate max 1 rad/s, angle max 0.6 rad"]
    PV --> N["+ coloured noise"]
    PS --> N
    N --> B["bicycle model, RK4, 100 Hz<br/>x' = v cos(yaw)<br/>y' = v sin(yaw)<br/>yaw' = v tan(steer) / L"]
    B --> O1["/veh_state (x, y, yaw)"]
    B --> O2["/veh_actual (v, steer)"]
```

This is why the car does not obey commands instantly: the actual speed and steering **lag** the command. At the
finish, the driver commands 0 but the car was still moving at 3.7 m/s one second later. The driver plans its braking
early for exactly this reason.

## 6. How a run is scored

```mermaid
flowchart LR
    S["/veh_state samples"] --> CTE["cross-track error<br/>vs the path"]
    S --> PR["progress to the finish"]
    S --> RE["rest detection<br/>moved under 0.05 m for 1 s"]
    CTE --> TR["tracking (40)<br/>40 x completion x (1 - RMS/2 m)"]
    PR --> TR
    RE --> TI["time (40)<br/>40 x min(v_eq, 30) / 30"]
    RE --> SP["stop (20)<br/>full within 5 m, -5 per extra metre"]
    TR --> SUM["score = tracking + time + stop"]
    TI --> SUM
    SP --> SUM
    SUM --> OUT["/score, /sim_status, JSON report"]
```

Any result other than `stopped` (`off_track`, `overrun`, `timeout`) gives **0** for time and stop.

## 7. The tuning pipeline

```mermaid
flowchart LR
    SW["_SCRIPT/11.18.26 script/sweepN.bash<br/>list of parameter sets"] --> LOOP["for each set"]
    LOOP --> DR["start my_driver<br/>with --ros-args -p ..."]
    DR --> EV["evaluate.bash --headless -n 2<br/>4 paths x 2 runs"]
    EV --> JS["eval_results/sweepN/SET.json"]
    JS --> SUM["summary.txt<br/>score, track, time, stop,<br/>max error, failures"]
    SUM --> LOG["_LOG/11.18.26 log and diagram/"]
    LOOP --> KILL["stop the driver"]
```

Used for the four rounds: 6 + 6 + 2 + 3 parameter sets, 2 runs per path each.

## 8. Timing

| Item | Rate or delay |
|---|---|
| Physics integration | 100 Hz |
| `/veh_state`, `/veh_actual` | 50 Hz (20 ms) |
| Driver control loop and `/veh_ctrl` | 20 Hz (50 ms) |
| Command timeout | 0.5 s without `/veh_ctrl` -> speed target 0 |
| Speed loop lag | about 1 to 2 s to settle (PI loop, natural frequency 3 rad/s, damping 0.8) |
| Steering rate limit | 1 rad/s |
| Run time limit | 60 s |

The pose the driver reads can be up to 20 ms old, and the next command only changes the car through the actuator loops.
At 25 m/s the car travels 0.5 m in 20 ms, so the driver always acts on slightly old information. This is one reason a
longer lookahead helps at speed.

## 9. Ordering pitfalls

- **`/path` and `/reset` order is not guaranteed.** Keep the path on reset.
- **A late-started driver** only gets the path if it uses transient-local QoS.
- **Empty `/path` means "no task":** publish zero speed; do not keep following the last path.
- **Stop publishing and the car stops:** the 0.5 s timeout is a safety feature, not a bug.
- **Only one driver at a time** may publish `/veh_ctrl`, otherwise the two commands compete.
