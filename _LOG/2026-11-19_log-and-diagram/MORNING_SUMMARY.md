# Morning summary (updated after every experiment)

**Best scores and how to run them again: [BEST_SCORES.md](BEST_SCORES.md)** (frozen script `_SCRIPT/2026-11-19_script/run_best_B6_74.9.bash`, git tag `best-B6-74.9`).

**Last update:** 2026-11-19 14:55, after C6. **FINAL BEST: B6 = 74.9** (3 runs per path, robust: every stop 1.1-2.9 m past the line). Realistic ceiling about 77.
later same-session checks; noise between sweeps about 0.6).** Ceiling with official settings about 76.

| ID | Method (paper) | Best score | vs same-session R2G10 | Verdict |
|---|---|---:|---:|---|
| E1 | Stanley (Hoffmann 2007, DLR 2026) | 73.0 | 73.6 | needs prediction; ~0.6 below |
| E2 | Predictive Stanley (DLR 2026) | 72.8 | 74.0 | worse than plain Stanley here |
| E3 | Rear-axle Stanley + feed-forward (DLR 2026) | 73.5 | 73.9 | best Stanley, within noise, not better |
| E4 | Pure pursuit + feed-forward (Kapania & Gerdes 2015) | 73.5 | 73.9 | no gain; more ff = worse wave |
| E5 | Kinematic MPC / LQR with steering lag (MAP2, LPV-MPC, FS 2026) | 73.2 | 74.4 | lower r better (r30 > r100 > r300): tune further (E6, r 3-10) |

Details: `personal_log.md` (one step per experiment), `experiment_plan.md` (table), results in `_RESULTS/2026-11-19_eval-result/`.
| E6 | LQR tuning | 73.7 (r20) | 73.9 | best r 20-30; strong LQR (r3) best wave |
| C1 | Stanley K8/K12 | 73.7 (K12) | 74.0 | smallest max error 0.35 m, weak on circle |
| C2 | Pure pursuit + 30 % LQR (r3) | **74.3** | 74.0 | best so far in-session (+0.3, within noise) |
| C3 | Time round: lat_accel 40-100, cruise 30 | running | | |
| C3 | Faster curves (lat_accel 40, cruise 30) on C2 | 74.5 | 74.0 | circle at its ceiling (14.4 m/s) |
| C4 | Time-optimal braking (bang_brake) + stop_damp 5 | 74.9 | 74.6 | faster AND safer stop (~2 m past the line) |
| E7 | 3-run confirmation | **74.9 (B5)** | 74.0 | **B5 confirmed** |

**B5 settings:** cruise 30, lat_accel 40, brake 5.9 (ramp, used before the bang point), stop_aim 1.5, lookahead_base 2.5,
lookahead_gain 0.10, predict_time 0.10, steer_tau 0.10, blend_lqr 0.3 (lqr_r 3, ff_time 0.10), stop_damp 5, bang_brake true.
Demo: `./_SCRIPT/2026-11-19_script/demo_best.bash eval`
| C5 | Tracking round around B5 | 74.9 (blend 0.4) | 73.0 | found 2 risks: rare stop overshoot (7.2 m), gain 0.12 off-track at wave start |
| C6 | Control rate 100 Hz (precise brake point) + gain 0.09, 3 runs per path | **74.9 (B6)** | 74.4 | **B6 = final: robust** |

**B6 = B5 + control_hz 100 + lookahead_gain 0.09** (demo_best.bash runs B6).
