#!/usr/bin/env python3

import fcntl
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".vscode" / "settings.json"
AUDIT = ROOT / "exam_audit"
LOG = AUDIT / "config_events.jsonl"
LOCK = AUDIT / ".monitor.lock"
POLL_SECONDS = 1.0
HEARTBEAT_SECONDS = 120.0


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def snapshot():
    try:
        content = SETTINGS.read_bytes()
    except FileNotFoundError:
        return "file_missing", None
    except OSError:
        return "file_unreadable", None

    digest = hashlib.sha256(content).hexdigest()
    try:
        settings = json.loads(content)
        if not isinstance(settings, dict):
            return "invalid_json_object", digest
    except (UnicodeError, json.JSONDecodeError):
        return "invalid_json", digest
    feature = settings.get("chat.disableAIFeatures")
    if feature is True:
        return "ai_features_disabled", digest
    if feature is False:
        return "ai_features_enabled", digest
    return "ai_setting_missing_or_invalid", digest


def log_event(event, **attributes):
    # Do not log file contents, credentials, code, or keyboard activity.
    line = {
        "time_utc": now_utc(),
        "repo": ROOT.name,
        "event": event,
        **attributes,
    }
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(line, sort_keys=True) + "\n")


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    # Only one active watcher per Codespace, even if startup hooks repeat.
    with LOCK.open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0

        previous_state, previous_digest = snapshot()
        log_event("watcher_started", state=previous_state)
        if previous_state != "ai_features_disabled":
            log_event("setting_not_compliant_at_start", state=previous_state)
        last_heartbeat = time.monotonic()

        while True:
            time.sleep(POLL_SECONDS)
            state, digest = snapshot()
            if (state, digest) != (previous_state, previous_digest):
                log_event(
                    "settings_changed",
                    previous_state=previous_state,
                    new_state=state,
                )
                previous_state, previous_digest = state, digest
            if time.monotonic() - last_heartbeat >= HEARTBEAT_SECONDS:
                log_event("watcher_heartbeat", state=state)
                last_heartbeat = time.monotonic()


if __name__ == "__main__":
    raise SystemExit(main())
