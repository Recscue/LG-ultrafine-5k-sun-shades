#!/bin/bash
# Build one complete print set per test-coupon clearance, each with named files,
# and run the seam and assembly checks on every set.
cd "$(dirname "$0")"
PY=.venv/bin/python
for pair in "1-notch:0.10" "2-notch:0.15" "3-notch:0.20"; do
  tag=${pair%%:*}; fit=${pair##*:}
  dir="out/sets/${tag}_${fit}mm"
  rm -rf "$dir"; mkdir -p "$dir/raw"
  echo "== $tag ($fit mm per side)"
  export MJF=0 FIT=$fit OUT_DIR="$PWD/$dir/raw"
  $PY build.py 2>&1 | grep -i "TOO\|Error\|assert"
  $PY check_seams.py 2>&1 | grep see-through
  $PY check_assembly.py 2>&1 | grep -iv backend | tail -1
  $PY -c "
import build as B
print('joint clearance per side:', B.JOINT_CLEAR)
bad=[(s,n) for s,par in (('left',0),('right',1)) for n,m in B.pieces(par).items() if len(m.decompose())!=1]
print('multi-body parts:', bad or 'none')" 2>&1 | grep -E 'clearance|multi'
  $PY - "$dir" <<'EOF' 2>&1 | grep -iv backend
import sys, trimesh
d = sys.argv[1]
names = {
 "fit_test_clip": "0_fit-test-clip_print-first",
 "left_extension": "left_1a_side-extension-top", "left_extension-lower": "left_1b_side-extension-bottom",
 "left_outer": "left_2_outer",
 "left_middle-camera": "left_3_middle_monitor-camera-notch",
 "left_inner": "left_4_inner_webcam-shelf_spine",
 "right_extension": "right_1a_side-extension-top", "right_extension-lower": "right_1b_side-extension-bottom",
 "right_outer": "right_2_outer",
 "right_middle-camera": "right_3_middle_monitor-camera-notch",
 "right_inner": "right_4_inner_spine",
}
for old, new in names.items():
    m = trimesh.load(f"{d}/raw/{old}.stl")
    open(f"{d}/{new}.stl", "w").write(trimesh.exchange.stl.export_stl_ascii(m))
print("named files:", len(names))
EOF
  rm -rf "$dir/raw"
done
unset FIT OUT_DIR
