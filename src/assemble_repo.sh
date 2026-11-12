#!/bin/bash
# Lay out the print files in the GitHub repo for a person, not a script.
# Each step folder leads with ready-to-print plate files (3MF, parts already placed and
# oriented); the single-part STLs sit in an individual-parts folder as a fallback.
set -e
S=$(cd "$(dirname "$0")" && pwd)
D=/local/home/ryanvan/workplace/monitor-sun-shield
P="$D/print-files"
rm -rf "$D/stl" "$P"
T="$P/step-1_test-prints"
mkdir -p "$T/individual-parts"
cp "$S/out/plates/test-plate.3mf" "$T/"
cp "$S"/out/coupons/*.stl "$T/individual-parts/"
for s in "$S"/out/sets/*; do
  n=$(basename "$s")                 # e.g. 1-notch_0.10mm
  tag=${n%%_*}; mm=${n##*_}
  F="$P/step-2_full-shield/${mm}_${tag}"
  mkdir -p "$F/individual-parts/left-monitor" "$F/individual-parts/right-monitor"
  cp "$S/out/plates/$n"/*.3mf "$F/"
  cp "$s"/left_*.stl "$F/individual-parts/left-monitor/"
  cp "$s"/right_*.stl "$F/individual-parts/right-monitor/"
done
cp "$S/READ-ME-FIRST.txt" "$P/"
