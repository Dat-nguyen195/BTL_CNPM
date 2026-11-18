"""Durable local telemetry feed shared by producers and Streamlit observers."""
import copy
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.scheduler import apply_hub_snapshot


def feed_path():
    return Path(os.environ.get("EMOBILITY_IOT_DB", "tmp/telemetry.sqlite3"))


def connect_feed(path=None):
    path = Path(path or feed_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.execute("CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE, payload TEXT)")
    return connection


def publish_event(event, path=None):
    """Persist a JSON event once. Validation against operational hubs happens on consumption."""
    required = ("event_id", "hub_id", "port_id", "event_type", "occurred_at")
    if any(not isinstance(event.get(key), str) or not event[key] for key in required):
        raise ValueError("Thiếu trường bản tin")
    if event["event_type"] not in ("OFFLINE", "ONLINE"):
        raise ValueError("Loại sự kiện không hợp lệ")
    timestamp = datetime.fromisoformat(event["occurred_at"])
    if timestamp.tzinfo is None:
        raise ValueError("occurred_at cần múi giờ")
    payload = dict(event, received_at=datetime.now(timezone.utc).isoformat())
    with connect_feed(path) as connection:
        cursor = connection.execute("INSERT OR IGNORE INTO events(event_id,payload) VALUES (?,?)",
                                    (event["event_id"], json.dumps(payload)))
        return bool(cursor.rowcount)


def consume_events(state, path=None):
    """Replay in receipt order, ignoring stale readings per physical port."""
    with connect_feed(path) as connection:
        rows = connection.execute("SELECT seq,payload FROM events WHERE seq>? ORDER BY seq",
                                  (state.get("telemetry_cursor", 0),)).fetchall()
    changed = 0
    for seq, raw in rows:
        event = json.loads(raw)
        state["telemetry_cursor"] = seq
        hub = next((h for h in state["hubs"] if h["hub_id"] == event["hub_id"]), None)
        try:
            port = int(event["port_id"])
        except ValueError:
            port = 0
        status = "REJECTED"
        key = f'{event["hub_id"]}/{port}'
        seen = state.setdefault("telemetry_ports", {})
        if hub and 1 <= port <= hub["charging_ports"]["total"]:
            previous = seen.get(key)
            stamp = datetime.fromisoformat(event["occurred_at"])
            if previous and stamp <= datetime.fromisoformat(previous["occurred_at"]):
                status = "STALE"
            else:
                before = copy.deepcopy(hub["charging_ports"])
                # Reading represents one indexed port. Unknown ports begin ONLINE.
                delta = int(event["event_type"] == "OFFLINE") - int(
                    previous is not None and previous["event_type"] == "OFFLINE")
                hubs = copy.deepcopy(state["hubs"])
                target = next(h for h in hubs if h["hub_id"] == hub["hub_id"])
                ports = target["charging_ports"]
                offline = min(ports["total"], max(0, ports.get("offline", 0) + delta))
                actual_delta = offline - ports.get("offline", 0)
                busy = ports["total"] - ports.get("offline", 0) - ports["available"]
                ports["offline"] = offline
                if actual_delta > 0:
                    ports["available"] -= max(0, actual_delta - busy)
                elif actual_delta < 0:
                    ports["available"] += -actual_delta
                apply_hub_snapshot(state, hubs)
                seen[key] = event
                event["before"] = before
                event["after"] = dict(ports)
                event["displayed_at"] = datetime.now(timezone.utc).isoformat()
                status = "APPLIED"
                changed += 1
        event["result"] = status
        state.setdefault("telemetry_log", []).append(event)
        state["telemetry_log"] = state["telemetry_log"][-100:]
    return changed
