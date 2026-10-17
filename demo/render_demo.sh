#!/bin/bash
# renders demo segments sequentially; resumable (skips finished parts)
cd "$(dirname "$0")"; mkdir -p parts logs
for sc in "$@"; do
  [ -f parts/$sc.mp4 ] && continue
  ${MANIMGX:-manimgx} render demo_scenes.py $sc -r 1920x1080 --fps 30 --preset veryfast --crf 20 -o raw_$sc.mp4 > logs/$sc.log 2>&1 \
    && mv raw_$sc.mp4 parts/$sc.mp4 && { [ -f raw_$sc.srt ] && mv raw_$sc.srt parts/$sc.srt; echo "- $(date +%H:%M) demo part $sc rendered" >> ../PROGRESS.md; } \
    || echo "- $(date +%H:%M) demo part $sc FAILED (see demo/logs/$sc.log)" >> ../PROGRESS.md
done
