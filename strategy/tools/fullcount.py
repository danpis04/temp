"""Trailing-24h FULL-cycle count for the pacing gate — AGENT-EDITABLE (strategy/tools/).

Added by DEEP-2026-09-30 after four deep retros in a row found the LIGHT
tick's hand count wrong: in the 09-29/30 window 9 of 14 pacing-evaluated
LIGHT ticks wrote a wrong number (06:09Z '18', 10:09Z '22', 14:09Z '29+',
17:10Z '22' against a true 6-7) and only 1 wrote the required
'v5=N [hh:mm, ...]' token. The awk command in schedule.json notes needs
approval on the operator runner, so ticks counted from memory. Same
escalation shape as reconcile.py: a mechanical check instead of more prose.

Rule (schedule.json notes, COUNT COMMAND v5): a cycles.log line counts
when it starts '<ts>Z cycle done' and the FIRST of the markers '(FULL',
'(LIGHT', '(TRIGGERED' is '(FULL'. The window is strictly later than
now minus 24h. Lines with a non-numeric timestamp (e.g. '08:0xZ') are
skipped and reported, fail-safe undercount.

Usage: python3 strategy/tools/fullcount.py [--now 2026-09-30T04:07]
Prints one line to paste verbatim: v5=N [hh:mm, ...]
"""
import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "journal" / "cycles.log"
LINE = re.compile(r"^(\S+?)Z cycle done.*?\((FULL|LIGHT|TRIGGERED)")


def parse_ts(raw):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--now", help="UTC time, YYYY-MM-DDTHH:MM (default: now)")
    args = ap.parse_args()
    now = parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    hits, skipped = [], []
    for line in LOG.read_text().splitlines():
        m = LINE.match(line)
        if not m:
            continue
        ts = parse_ts(m.group(1))
        if ts is None:
            if m.group(1)[:10] >= cutoff.strftime("%Y-%m-%d"):
                skipped.append(m.group(1))
            continue
        if cutoff < ts <= now and m.group(2) == "FULL":
            hits.append(ts)
    print(f"v5={len(hits)} [{', '.join(t.strftime('%H:%M') for t in hits)}]")
    if skipped:
        print(f"unparsed timestamps skipped: {', '.join(skipped)}", file=sys.stderr)


if __name__ == "__main__":
    main()
