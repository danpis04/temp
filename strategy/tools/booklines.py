#!/usr/bin/env python3
"""Compact per-book line table from `core/odds.py odds ...` JSON.

Usage: python3 core/odds.py odds baseball_mlb --markets h2h,totals | \
         python3 strategy/tools/booklines.py [team-substring]

Added 2026-10-01 19:1xZ: odds.py prints ~700 lines of nested JSON per MLB
slate, and on the operator runner inline python to flatten it needs
approval. One line per (event, book, market) with decimal prices, then a
proportional no-vig consensus per (market, point) across books, ready for
devig.py's power method.
"""
import json
import sys
from collections import defaultdict


def main():
    flt = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    events = json.load(sys.stdin)
    for ev in events:
        name = f"{ev['away_team']} @ {ev['home_team']}"
        if flt and flt not in name.lower():
            continue
        print(f"== {name}  {ev['commence_time']}")
        agg = defaultdict(list)
        for bk in ev.get("bookmakers", []):
            for mk in bk.get("markets", []):
                outs = mk["outcomes"]
                cells = " | ".join(
                    f"{o['name']}{'' if o.get('point') is None else ' ' + str(o['point'])} {o['price']}"
                    for o in outs)
                print(f"  {bk['key']:<14} {mk['key']:<8} {cells}")
                if len(outs) == 2:
                    raw = [1 / o["price"] for o in outs]
                    s = sum(raw)
                    pt = outs[0].get("point")
                    key = (mk["key"], outs[0]["name"], pt)
                    agg[key].append(raw[0] / s)
        for (mk, nm, pt), ps in sorted(agg.items(), key=lambda kv: str(kv[0])):
            avg = sum(ps) / len(ps)
            print(f"  consensus {mk:<8} {nm}{'' if pt is None else ' ' + str(pt)}: "
                  f"{avg:.3f} (n={len(ps)}, min {min(ps):.3f} max {max(ps):.3f})")


if __name__ == "__main__":
    main()
