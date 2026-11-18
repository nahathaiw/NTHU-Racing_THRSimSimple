#!/usr/bin/env bash
# Live demo of the best settings (set N) with the simulator GUI.
#
# Usage:
#   ./scripts/demo_best.bash            # GUI: pick a path in the window and click Start
#   ./scripts/demo_best.bash eval       # GUI evaluation: click "Start evaluation" (1 run x 4 paths, about 1 minute)
#   ./scripts/demo_best.bash wave       # GUI already set to that path (straight|wave|lane_change|circle)
#
# It starts my_driver with the final parameters, opens the simulator, and stops the driver when you close the window.
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# system tools first: Anaconda's python breaks ROS
export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u
source /opt/ros/humble/setup.bash
source "$WS/install/setup.bash"

# stop any leftover driver, and stop ours when this script ends
pkill -f "lib/my_driver/driver" 2>/dev/null
trap 'pkill -INT -f "lib/my_driver/driver" 2>/dev/null' EXIT

echo ">>> starting my_driver with the best settings (set N)"
ros2 run my_driver driver --ros-args \
  -p cruise_speed:=25.0 -p lat_accel:=6.0 -p brake_decel:=5.9 \
  -p stop_aim:=2.0 -p lookahead_base:=2.5 -p lookahead_gain:=0.25 > /tmp/demo_driver.log 2>&1 &
sleep 2

case "${1:-}" in
  eval)
    echo ">>> opening the evaluation window: click 'Start evaluation'"
    "$WS/evaluate.bash" -n 1
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
