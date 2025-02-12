#!/bin/sh
# 🧭 Tere Terminal Navigation Function

# 📂 Change directory using tere command
tere() {
    local result=$(command tere "$@")
    [ -n "$result" ] && cd -- "$result"
}
