# New methods (2025-2026) we can learn from and implement

**How these were found (2026-11-19):** OpenAlex listed every 2025-2026 paper that cites our classic reading list
(`../README.md`): **1,603 papers**. `classify_citing_papers.py` kept the **501** about vehicle path tracking or racing control
(241 from 2025, 260 from 2026) and grouped them by method. Full lists: `../citing_2025_2026/relevant.json` (with abstracts).
Scripts: `_SCRIPT/2026-11-19_script/find_citing_papers.py`, `classify_citing_papers.py`. PDFs here are local only (git-ignored).

| Method group | Papers (2025-26) |
|---|---:|
| Learning-based control (RL, Gaussian process, neural net, residual) | 213 |
| MPC / optimisation-based tracking | 164 |
| Improved pure pursuit / geometric | 133 |
| Delay / latency compensation | 46 |
| Speed profile / minimum time / racing line | 43 |
| Other (systems, platforms, surveys) | 102 |
(a paper can be in several groups)

## Important filter: what fits OUR simulator
THRSimSimple is a **kinematic bicycle model** (no tyres, no slip, no friction limit) with **actuator lag + 1 rad/s steering
rate + noise**, 4 fixed paths. So methods about **tyre models / friction changes** (MAP2's tyre part, LLA-MPC, on-track tyre
identification) solve a problem our simulator does not have. Methods about **prediction with actuator lag**, **kinematic MPC**
and **learning the lookahead** fit directly.

## Shortlist (PDF in this folder)

| Fit | File | Paper | Core idea | Fits us? |
|---|---|---|---|---|
| ★★★ | `2026_DLR_Predictive_Stanley_Feedforward.pdf` | *Implementation and Evaluation of Stanley Based Path-Following Controllers...* (DLR, 2026, thesis) | Stanley vs **predictive Stanley** (prediction horizon) vs Stanley + **feed-forward from a kinematic reference model**; tested with added **latency**. Predictive Stanley had the lowest lateral RMSE in simulation | Very close to our setup (kinematic, latency); easy to implement in C++ next to pure pursuit |
| ★★★ | `2026_MAP2_Kinematic_MPC_GP_Residual_Pursuit.pdf` | *MAP2: Model- and Acceleration-Based Pursuit with MPC and Gaussian Process Residual Learning* (arXiv 2610.12196, 2026) | **Curvature-based kinematic MPC** over a horizon, then a learned (Gaussian process) correction of what the model gets wrong | The kinematic-MPC half fits us exactly (it is "prediction" done properly over many steps); GP residual could learn the steering lag/overshoot |
| ★★★ | `2026_LPV_MPC_Lateral_Control_Full_Scale_Racing.pdf` | *LPV-MPC for Lateral Control in Full-Scale Autonomous Racing* (ICRA 2026, arXiv 2603.13732) | Linear parameter-varying MPC for steering, stable above 71 m/s on a real IAC car; **Python code published (acados)** | Good template for a lateral MPC with the steering lag in the model |
| ★★☆ | `2026_RL_Tuned_Pure_Pursuit_PPO_Lookahead_Gain.pdf` | *Learning to Tune Pure Pursuit in Autonomous Racing: Joint Lookahead and Steering-Gain Control With PPO* (IEEE RA-L 2026, arXiv 2602.18386) | RL policy (PPO) picks lookahead **and** steering gain every step from speed + upcoming curvature; trained in F1TENTH Gym, run in ROS 2 | Keeps our pure pursuit; replaces hand-tuned lookahead. Needs a training setup (our sim's Python model could be the gym) |
| ★★☆ | `2026_FS_Driverless_Prediction_Model_MPC.pdf` | *Vehicle Prediction Model for Enhanced MPC Path Tracking in Formula Student Driverless* (IEEE IV 2026, arXiv 2606.10732) | Kinematic bicycle model + offline regression + online sparse GP, learns from **past runs** | Formula Student context (like NTHU Racing); the "learn from previous runs" idea fits our repeated evaluation |
| ★☆☆ | `2025_Residual_Koopman_MPC.pdf` | *Residual Koopman MPC...* (ITSC 2025, arXiv 2507.18396) | Linear MPC + a learned linear (Koopman) correction | Interesting, more advanced |
| ☆ | `2025_LLA_MPC_Fast_Adaptive_Racing.pdf` | *LLA-MPC: Fast Adaptive Control for Autonomous Racing* (IROS 2025) | Bank of models, adapts to friction changes fast | Friction/tyres: not in our sim |
| ☆ | `2025_OnTrack_System_Identification_Racing.pdf` | *Learning-Based On-Track System Identification...* (RA-L 2025, cited 31) | Learn tyre parameters in under a minute | Tyres: not in our sim |

Not downloaded (no open PDF): *Dynamic Lookahead Distance via RL-Based Pure Pursuit* (IV Workshops 2026);
*Adapting to unknown environment conditions ... using Iterative Learning Control* (Robotics and Autonomous Systems 2026);
*Smooth and Robust Path-Tracking Control ... From Theory to Real-World* (Electronics 2025, open access but the site blocked the download:
https://www.mdpi.com/2079-9292/14/18/3588).

## Suggested order to implement
1. **Predictive Stanley / feed-forward** (DLR 2026): small change, directly about our latency problem. Compare to R2G10 (74.2).
2. **Kinematic MPC with the steering lag in the model** (MAP2 / LPV-MPC / FS 2026): the "real" modern method; our
   `predict()` is already one step of it. Biggest learning value.
3. **RL-tuned lookahead** (RA-L 2026): if we want to learn reinforcement learning; needs a training loop.
