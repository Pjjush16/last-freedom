#!/bin/bash
while true; do
    echo "[$(date)] Starting proxy..."
    python3 /root/userdata/workspace/chase-game-tauri/tile_proxy.py
    EXIT_CODE=$?
    echo "[$(date)] Proxy exited with code $EXIT_CODE, restarting in 1s..."
    sleep 1
done
