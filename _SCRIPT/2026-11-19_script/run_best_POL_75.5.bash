#!/usr/bin/env bash
# FROZEN COPY of the POL demo (2026-11-19 19:20). Needs the driver code of git tag best-POL-75.5 (or later).
# Live demo of today's best settings (set POL, 75.5/100 with 3 runs per path) with the simulator GUI.
# POL = B6 + adaptive lookahead policy (C9, tuned by CEM policy search): ld = (2.9 + 0.06 v) / (1 + 11.6 |kappa|) - 1.5 |e|.
#       Same score as F15 (learned table) but needs no practice runs, so it also works on a new track.
#       Add "-p ilc_apply:=true -p ilc_file:=.../best_F15_ilc_table.txt" for POLF15 (75.6, same within noise).
# B6 = B5 + control_hz 100 (precise brake point) + lookahead_gain 0.09.
# B5 = pure pursuit + pose prediction + 30 % LQR blend, fast curves, time-optimal braking. (Previous best R2G10 = 74.0 same session.)
#
# Usage (from the repo folder):
#   ./_SCRIPT/2026-11-19_script/demo_best.bash            # GUI: pick a path in the window and click Start
#   ./_SCRIPT/2026-11-19_script/demo_best.bash eval       # GUI evaluation, 3 runs x 4 paths: click "Start evaluation"
#   ./_SCRIPT/2026-11-19_script/demo_best.bash eval 1     # same, 1 run per path (about 1 minute)
#   ./_SCRIPT/2026-11-19_script/demo_best.bash circle     # GUI already set to that path (straight|wave|lane_change|circle)
#
# Starts my_driver with the best parameters, opens the simulator, stops the driver when you close the window.
# Do not run it while a sweep is running (two drivers would fight over the car).
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"   # Anaconda's python breaks ROS
set +u
source /opt/ros/humble/setup.bash
source "$WS/install/setup.bash"

pkill -f "lib/my_driver/driver" 2>/dev/null
trap 'pkill -INT -f "lib/my_driver/driver" 2>/dev/null' EXIT

echo ">>> starting my_driver with set POL (B6 + curve-adaptive lookahead)"
ros2 run my_driver driver --ros-args \
  -p cruise_speed:=30.0 -p lat_accel:=40.0 -p brake_decel:=5.9 -p stop_aim:=1.5 \
  -p lookahead_base:=2.9 -p lookahead_gain:=0.06 -p ld_kappa:=11.6 -p ld_err:=1.5 -p control_hz:=100.0 \
  -p predict_time:=0.10 -p steer_tau:=0.10 -p steer_rate:=1.0 -p stop_damp:=5.0 \
  -p blend_lqr:=0.3 -p lqr_r:=3.0 -p ff_time:=0.10 -p bang_brake:=true \\
  -p ilc_apply:=true -p ilc_file:="$WS/_SCRIPT/2026-11-19_script/best_F15_ilc_table.txt" > /tmp/demo_driver.log 2>&1 &
sleep 2

case "${1:-}" in
  eval)
    echo ">>> opening the evaluation window: click 'Start evaluation'"
    "$WS/evaluate.bash" -n "${2:-3}"
    ;;
  straight|wave|lane_change|circle)
    echo ">>> opening the simulator on '$1': click Start"
    "$WS/run_sim.bash" path_shape:="$1"
    ;;
  *)
    echo ">>> opening the simulator: choose a path and click Start"
    "$WS/run_sim.bash"
    ;;
esac
