#!/bin/sh
# 🧹 LF File Manager Preview Cleaner
# Removes preview images when navigating away

if [ -n "$FIFO_UEBERZUG" ]; then
  printf '{"action": "remove", "identifier": "preview"}\n' >"$FIFO_UEBERZUG"
fi
