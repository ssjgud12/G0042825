#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p exam_audit

nohup bash -c 'python3 scripts/monitor_exam_settings.py >> exam_audit/monitor_errors.log 2>&1 &' >/dev/null 2>&1 </dev/null
