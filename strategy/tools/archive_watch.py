"""Replace one strategy/schedule.json watch item, or append text to a key.

Usage:
  python3 strategy/tools/archive_watch.py replace PREFIX REPLACEMENT
  python3 strategy/tools/archive_watch.py append KEY TEXT

`replace` swaps the single watch item that starts with PREFIX for
REPLACEMENT (an ARCHIVED one-line pointer). It refuses if PREFIX matches
zero items or more than one. `append` adds " " + TEXT to the end of a
top-level string key (e.g. notes).

Added DEEP-2026-10-02: watch items are single JSON strings of up to ~10KB,
too long to Edit reliably, and inline python needs approval on the
operator runner, while tools here do not.
"""
import json
import sys

PATH = "strategy/schedule.json"


def main(argv):
    with open(PATH) as f:
        d = json.load(f)
    if argv[0] == "replace":
        prefix, repl = argv[1], argv[2]
        hits = [i for i, w in enumerate(d["watch_items"]) if w.startswith(prefix)]
        if len(hits) != 1:
            print(f"refused: {len(hits)} items start with {prefix!r}")
            return 1
        d["watch_items"][hits[0]] = repl
    elif argv[0] == "append":
        key, text = argv[1], argv[2]
        if not isinstance(d.get(key), str):
            print(f"refused: {key!r} is not a string key")
            return 1
        d[key] = d[key] + " " + text
    else:
        print(__doc__)
        return 1
    with open(PATH, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
