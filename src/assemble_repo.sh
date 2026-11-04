#!/bin/bash
# Lay out the print files in the GitHub repo as plain step folders for a person,
# not a script: step 1 is test prints, step 2 is one full set per clearance.
set -e
S=$(cd "$(dirname "$0")" && pwd)
D=/local/home/ryanvan/workplace/monitor-sun-shield
P="$D/print-files"
rm -rf "$D/stl" "$P"
T="$P/step-1_test-prints"
mkdir -p "$T"
cp "$S/out/sets/2-notch_0.15mm/0_fit-test-clip_print-first.stl" "$T/fit-test-clip.stl"
cp "$S"/out/coupons/*.stl "$T/"
for s in "$S"/out/sets/*; do
  n=$(basename "$s")                 # e.g. 1-notch_0.10mm
  tag=${n%%_*}; mm=${n##*_}
  F="$P/step-2_full-shield/${mm}_${tag}"
  mkdir -p "$F/left-monitor" "$F/right-monitor"
  cp "$s"/left_*.stl "$F/left-monitor/"
  cp "$s"/right_*.stl "$F/right-monitor/"
done
cp "$S/READ-ME-FIRST.txt" "$P/"
