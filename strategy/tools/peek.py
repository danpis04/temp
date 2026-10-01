"""List scan rows (work/scan.json, JSONL from core/scan.py) by liquidity.

Usage: python3 strategy/tools/peek.py MAX_HOURS [KEYWORD] [N] [--file PATH] [--nosports]

Unscreened FULL cycles (screener reserve spent) need a way to read the pool;
ad-hoc python/awk needs approval on the operator runner, tools here do not.
"""
import json
import re
import sys
from datetime import datetime, timezone

SPORTS_SLUG = re.compile(r"^[a-z0-9]+-[a-z0-9]+-[a-z0-9]+-\d{4}-\d{2}-\d{2}")


def main(argv):
    path = "work/scan.json"
    nosports = "--nosports" in argv
    argv = [a for a in argv if a != "--nosports"]
    if "--file" in argv:
        i = argv.index("--file")
        path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    hmax = float(argv[0])
    kw = argv[1].lower() if len(argv) > 1 else ""
    n = int(argv[2]) if len(argv) > 2 else 80
    now = datetime.now(timezone.utc)
    rows = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        try:
            ed = datetime.fromisoformat(r["end_date"].replace("Z", "+00:00"))
        except Exception:
            continue
        h = (ed - now).total_seconds() / 3600
        if h < 0 or h > hmax:
            continue
        if kw and kw not in (r["question"] + r.get("event_slug", "")).lower():
            continue
        # game slugs look like 'nfl-pit-cle-2026-10-02' (league-team-team-date)
        if nosports and SPORTS_SLUG.match(r.get("event_slug", "")):
            continue
        rows.append((h, r))
    rows.sort(key=lambda x: -(x[1].get("liquidity") or 0))
    for h, r in rows[:n]:
        print(f'{h:5.1f}h {r["market_id"]} liq={r.get("liquidity", 0) or 0:9.0f} '
              f'{r.get("outcome_prices")} {r["question"][:90]} [{r.get("event_slug", "")[:40]}]')
    print(f"-- {len(rows)} rows within {hmax}h", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
