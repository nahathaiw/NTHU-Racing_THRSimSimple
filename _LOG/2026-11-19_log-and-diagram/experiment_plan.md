# Experiment plan: new steering methods from 2025-2026 papers

Goal: beat **R2G10 = 74.2** (ceiling about 76). Time (16/40) and stop (20/20) are already maxed, so every experiment is about
**tracking** (38.2/40, RMS path error). Speed profile, prediction, stop_damp stay as in R2G10 unless the row says otherwise.
Each experiment: 2 runs per path (8 runs), same sweep script, results in `_RESULTS/2026-11-19_eval-result/`.
Status: TODO -> RUNNING -> DONE (or FAILED / SKIPPED). Filled in step by step; details of each step in `personal_log.md`.

## The list

| ID | Method | From paper | What changes in the driver | Why it might help |
|---|---|---|---|---|
| E0 | **Baseline R2G10** (pure pursuit + prediction) | our work today | nothing | reference to beat |
| E1 | Stanley | Hoffmann et al. 2007; DLR 2026 (base Stanley) | steering = heading error + atan(k * cross-track error / v), front axle | different steering law; often tracks tighter than pure pursuit |
| E2 | Predictive Stanley | DLR 2026 (best RMSE in their sim) | E1, but computed from the **predicted** pose | Stanley + our latency fix |
| E3 | Predictive Stanley + feed-forward | DLR 2026 (enhanced Stanley); Kapania & Gerdes 2015 | E2 + steering the path curvature needs, atan(L * kappa) | feedback only corrects small errors, less weaving |
| E4 | Pure pursuit + curvature feed-forward | Kapania & Gerdes 2015 | R2G10 + feed-forward term, blended | same idea on our current controller |
| E5 | Kinematic MPC with steering lag (LQR form) | MAP2 2026; LPV-MPC 2026; FS Driverless 2026 | new steering mode: linear model of path error + steering lag, optimal gains over a horizon (finite-horizon Riccati, no solver library) | the "full" version of prediction: plans many steps, knows the wheel lags |
| E6 | E5 with tuned weights | same | sweep error vs steering-effort weights, horizon | find the best MPC setting |
| E7 | Best of E1-E6 + confirmation | | 3 runs per path (12 runs), official style | a reliable final number |
| E8 | (optional) RL-tuned lookahead | RL pure pursuit, RA-L 2026 | policy picks lookahead and gain from speed + curvature | learning project; needs a training loop |

## Rule added 2026-11-19 ~02:45 (user): optimise promising methods, try combinations
After each experiment: if a method is **within noise of the best (about 0.6)** or **better on some paths**, it gets an
optimisation round (C-rows). If two methods are good at different things (e.g. one tracks the wave better, another the circle),
we try them **combined** (C-rows). Candidate C-rows are added below as results come in.

| ID | Idea | Why (evidence) | Status | Score | Result folder |
|---|---|---|---|---:|---|
| C2 | Blend pure pursuit + LQR (`blend_lqr`) | E6: LQR best on the wave, pure pursuit best on straight/circle | DONE 14:00 | **74.3** (30 % LQR r3; same-session E0 74.0, +0.3 = within noise) | `2026-11-19_1400_c1c2_combine/` |
| C1 | Stanley K6 + tuning (K 6-10, soft, with E4 feed-forward) | E1/E2: higher K kept improving (K1 71.5 -> K6 73.2), straight 74.6 = best straight so far | DONE 14:00 | 73.7 (K12; max err 0.35 m = smallest; best wave/lane, weak circle 74.0) | `2026-11-19_1400_c1c2_combine/` |
| C3 | Time round: much higher curve speed (lat_accel 40-100, cruise 30) on R2G10 and C2B3R3 | corrected ceiling 77.5: circle time 18.0 vs perfect 20.1, wave 15.3 vs 16.9 | DONE 14:09 | **74.5** (T40C2 = C2 blend + lat 40 + cruise 30; E0 74.0); circle v_eq 13.4 -> 14.4 = at realistic ceiling | `2026-11-19_1409_c3_time/` |
| C4 | Time-optimal braking (`bang_brake`: -30 command, then 0) on T40C2 | realistic perfect straight 12.07 m/s vs ours 11.6; offline 11.86 | RUNNING | | |

## Results (filled in as we go)

| ID | Status | Date-time | Score | Track /40 | Time /40 | Stop /20 | Max err (m) | Failures | Result folder | Note |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| E0 | DONE | 2026-11-19 01:4x / 01:52 | 74.2 | 38.2 | 16.0 | 20.0 | 0.56 / 0.51 | none | `..._p6_tracking/..._R2G10`, `..._p7_short_lookahead/..._S0` | scored 74.2 twice |
| E1 | DONE | 2026-11-19 02:21 | 73.0 (best: K4) | 36.9 | 16.1 | 20.0 | 0.51 | none (paper version without prediction: 3 off-track) | `2026-11-19_0221_e1_stanley/` | same-session E0 = 73.6. Stanley is ~0.6 below pure pursuit; needs prediction; higher K better (K1 71.5, K2 72.6, K4 73.0); yaw damping no help (72.4) |
| E2 | DONE | 2026-11-19 02:28 | 72.8 (best: K6 N3) | 36.7 | 16.0 | 20.0 | 0.60 | none | `2026-11-19_0228_e2_predictive_stanley/` | same-session E0 = 74.0. Predictive Stanley is WORSE than plain Stanley (K4: 73.0 -> 72.2 N3 -> 71.8 N6); plain K6 73.2 is the best Stanley, still 0.8 below pure pursuit |
| E3 | DONE | 2026-11-19 02:36 | 73.5 (best: K4 ff 0.10) | 37.5 | 16.0 | 20.0 | 0.75 | none | `2026-11-19_0236_e3e4_feedforward/` | same-session E0 = 73.9. Best Stanley variant so far (plain 73.0-73.2), within noise of pure pursuit but not above; ff 0.20 and K2 worse |
| E4 | DONE | 2026-11-19 02:36 | 73.5 (best: blend 0.3) | 37.4 | 16.1 | 20.0 | 0.69 | none | `2026-11-19_0236_e3e4_feedforward/` | same-session E0 = 73.9. Feed-forward blend does not help pure pursuit: 0.3 -> 73.5, 0.5 -> 72.1 (wave worse) |
| E5 | DONE | 2026-11-19 02:45 + 02:48 | 73.2 (best: r=30) | 37.1 | 16.1 | 20.0 | 0.57 | none | `2026-11-19_0245_e5_lqr/`, `2026-11-19_0248_e5_lqr_part2/` | same-session E0 = 74.4. Lower r (stronger steering) is better: r30 73.2, r100 71.5, r300 69.3; ff 0.2 worse (70.2); q_psi 4 slightly better (71.8 vs 71.5). Trend not finished: try r 3-10 in E6 |
| E6 | DONE | 2026-11-19 13:52 | 73.7 (best: r=20) | 37.6 | 16.0 | 20.0 | 0.53 | none | `2026-11-19_1352_e6_lqr_tuning/` | same-session E0 = 73.9: LQR r20 within noise of pure pursuit (best r 20-30; r10 72.2, r3 73.0). LQR r3/r10 have the BEST WAVE of any method (72.6/72.1 vs 71.4) but worse straight/circle. steer_tau 0.15 in the model hurts (70.8) |
| E7 | TODO | | | | | | | | | |
| E8 | optional | | | | | | | | | |
