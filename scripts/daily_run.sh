#!/bin/bash
# Obsidian Todo AI - 每日自动运行脚本
# 由 launchd 在每天 09:05 触发

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/daily_run.log"

mkdir -p "$PROJECT_DIR/logs"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"

source "$PROJECT_DIR/.venv/bin/activate"
todo daily-run >> "$LOG_FILE" 2>&1

echo "Exit code: $?" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
