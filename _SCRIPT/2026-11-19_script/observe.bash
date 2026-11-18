#!/usr/bin/env bash
# Hint 1, "draw the data and observe it": run my driver (final set N) on every path once, headless,
# while record_run.py saves command vs actual data and plots for each run.
#
# Usage:  ./_SCRIPT/2026-11-19_script/observe.bash [NAME] [extra driver params...]
#   e.g.  ./_SCRIPT/2026-11-19_script/observe.bash setN
# Output: _RESULTS/2026-11-19_eval-result/<YYYY-MM-DD_HHMM>_observe_<NAME>/
#         01_straight.png/.csv ... 04_circle.png/.csv, delays.txt, eval.json
set -u
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="${1:-setN}"; shift || true
pkill -f "lib/my_driver/driver" 2>/dev/null

export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u
source /opt/ros/humble/setup.bash
source "$WS/install/setup.bash"
set -u

OUT="$WS/_RESULTS/2026-11-19_eval-result/$(date +%Y-%m-%d_%H%M)_observe_$NAME"
mkdir -p "$OUT"
PARAMS=(-p cruise_speed:=25.0 -p lat_accel:=6.0 -p brake_decel:=5.9 -p stop_aim:=2.0 -p lookahead_gain:=0.25)
for p in "$@"; do PARAMS+=(-p "$p"); done
echo "driver params: ${PARAMS[*]}" | tee "$OUT/params.txt"

ros2 run my_driver driver --ros-args "${PARAMS[@]}" > "$OUT/driver.log" 2>&1 &
/usr/bin/python3 "$HERE/record_run.py" "$OUT" > "$OUT/recorder.log" 2>&1 &
REC=$!
sleep 2
"$WS/evaluate.bash" --headless -n 1 -o "$OUT/eval.json" > "$OUT/sim.log" 2>&1
sleep 1
kill -INT $REC 2>/dev/null
pkill -INT -f "lib/my_driver/driver" 2>/dev/null
sleep 1
echo "results in $OUT"
cat "$OUT/delays.txt" 2>/dev/null || echo "no delays.txt: see $OUT/recorder.log"
