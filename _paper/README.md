# _paper: reading list for the driverless controller

**New (2025-2026) methods to implement: see [2025-2026/README.md](2025-2026/README.md).** Below: the classics.

Downloaded 2026-11-19. Files are named `YEAR_Author_Topic.pdf`. **The PDFs stay on this computer only** (they are
git-ignored: about 40 MB, and publishers' copyright does not allow re-posting them in a public repo). This README is in git,
so anyone can download the same papers from the links below.

## Read first
1. **2009 Snider**: *Automatic Steering Methods for Autonomous Automobile Path Tracking* (CMU-RI-TR-09-08).
   Compares pure pursuit, Stanley and model-based steering in simulation. Explains our sweep results: a short lookahead is
   unstable at speed, a long one cuts corners. [CMU RI](https://www.ri.cmu.edu/pub_files/2009/2/Automatic_Steering_Methods_for_Autonomous_Automobile_Path_Tracking.pdf)
2. **2015 Kapania & Gerdes**: *Design of a feedback-feedforward steering controller for accurate path tracking and
   stability at the limits of handling*, Vehicle System Dynamics 53(12). Steer from the path's curvature (feed-forward),
   feedback fixes only the small error: our candidate for the last tracking points. [Stanford DDL](https://ddl.stanford.edu/publications/journal/design-feedback-feedforward-steering-controller-accurate-path-tracking-and)

## By topic
| File | Paper | Why it matters for my_driver |
|---|---|---|
| `1992_Coulter_Pure_Pursuit_Implementation.pdf` | Coulter, *Implementation of the Pure Pursuit Path Tracking Algorithm*, CMU-RI-TR-92-01 | The original pure pursuit write-up (our steering law) |
| `2009_Snider_Automatic_Steering_Methods_Path_Tracking.pdf` | Snider 2009 (above) | Lookahead trade-off, steering methods compared |
| `2014_Lipp_Boyd_Minimum_Time_Speed_Optimisation.pdf` | Lipp & Boyd, *Minimum-time speed optimisation over a fixed path*, Int. J. Control 2014 | The theory behind our speed profile (curve + braking limits) |
| `2015_Kapania_Gerdes_Feedback_Feedforward_Steering.pdf` | Kapania & Gerdes 2015 (above) | Feed-forward steering, the next code change |
| `2016_Paden_Survey_Motion_Planning_Control.pdf` | Paden et al., *A Survey of Motion Planning and Control Techniques for Self-driving Urban Vehicles*, IEEE T-IV 2016 ([arXiv 1604.07446](https://arxiv.org/abs/1604.07446)) | Big-picture overview, path-tracking controllers compared |
| `2020_Kabzan_AMZ_Driverless_Racing_System.pdf` | Kabzan et al., *AMZ Driverless: The Full Autonomous Racing System*, J. Field Robotics 2020 ([arXiv 1905.05150](https://arxiv.org/abs/1905.05150)) | Formula Student Driverless (ETH): MPC with actuator delay in the model |
| `2020_OKelly_F1TENTH_Evaluation_Environment.pdf` | O'Kelly et al., *F1TENTH: An Open-source Evaluation Environment for Continuous Control and Reinforcement Learning*, PMLR 123, 2020 ([PMLR](https://proceedings.mlr.press/v123/o-kelly20a/o-kelly20a.pdf)) | A simulator benchmark much like THRSimSimple |
| `2022_Betz_Survey_Autonomous_Racing.pdf` | Betz et al., *Autonomous Vehicles on the Edge: A Survey on Autonomous Vehicle Racing*, IEEE OJ-ITS 2022 ([arXiv 2202.07008](https://arxiv.org/abs/2202.07008)) | Who does what in autonomous racing |
| `2023_Becker_MAP_Pursuit_Controller.pdf` | Becker et al., *Model- and Acceleration-based Pursuit Controller for High-Performance Autonomous Racing*, ICRA 2023 ([arXiv 2209.04346](https://arxiv.org/abs/2209.04346)) | Pure pursuit improved with a vehicle model: closest to what we did today |

## Not downloaded (no free official copy found)
- Hoffmann, Tomlin, Montemerlo, Thrun, *Autonomous Automobile Trajectory Tracking for Off-Road Driving: Controller Design,
  Experimental Validation and Racing*, ACC 2007 (Stanley controller). [IEEE Xplore 4282788](https://ieeexplore.ieee.org/document/4282788). Try through the NTHU library.
- Kong, Pfeiffer, Schildbach, Borrelli, *Kinematic and Dynamic Vehicle Models for Autonomous Driving Control Design*, IEEE IV 2015
  (the bicycle model). The authors' lab link was down; try IEEE Xplore through the NTHU library.
- Rajamani, *Vehicle Dynamics and Control* (Springer textbook): library.
