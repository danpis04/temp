#!/usr/bin/env python3
"""Live bid/ask per outcome for one or more gamma market ids.

Usage: python3 strategy/tools/book.py <market_id> [<market_id> ...]

Added 2026-09-27 15:1xZ: on the operator runner, inline `python3 -c` and raw
curl to gamma both need approval, and quote.py wants CLOB token ids that the
screener batch files do not carry. This goes market id -> tokens -> book in
one allowed call, via core/pmapi (read-only). Prints endDate and the first
600 chars of the rules too, so the clause read happens before the estimate.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))
import pmapi  # noqa: E402


def main(ids):
    for mid in ids:
        try:
            m = pmapi.gamma_market(mid)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"market_id": mid, "error": str(e)}))
            continue
        book = {}
        for name, tid in pmapi.market_tokens(m).items():
            try:
                bid, ask = pmapi.best_prices(tid)
            except Exception as e:  # noqa: BLE001
                bid, ask = None, f"error: {e}"
            book[name] = {"bid": bid, "ask": ask}
        print(json.dumps({
            "market_id": mid,
            "question": m.get("question"),
            "end": m.get("endDate"),
            "liquidity": m.get("liquidityNum"),
            "volume": m.get("volumeNum"),
            "book": book,
            "rules": (m.get("description") or "")[:600],
        }, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
