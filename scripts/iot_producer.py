"""Send alternating port readings. Stop with Ctrl+C."""
import argparse
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.telemetry import publish_event

parser = argparse.ArgumentParser()
parser.add_argument("--hub", default="HUB-001")
parser.add_argument("--port", type=int, default=1)
parser.add_argument("--interval", type=float, default=5)
parser.add_argument("--count", type=int, default=0, help="0 chạy liên tục")
args = parser.parse_args()
if args.interval <= 0 or args.count < 0 or args.port < 1:
    parser.error("interval/port phải dương, count không âm")
index = 0
try:
    while args.count == 0 or index < args.count:
        event = dict(event_id=uuid.uuid4().hex, hub_id=args.hub, port_id=str(args.port),
                     event_type="OFFLINE" if index % 2 == 0 else "ONLINE",
                     occurred_at=datetime.now(timezone.utc).isoformat())
        publish_event(event)
        print(event, flush=True)
        index += 1
        if args.count == 0 or index < args.count:
            time.sleep(args.interval)
except KeyboardInterrupt:
    pass
