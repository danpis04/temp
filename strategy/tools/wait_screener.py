"""Block until every batch in a screener work dir has its out file.

Usage: python3 strategy/tools/wait_screener.py <work_dir> [timeout_s]
Prints the missing batch numbers on timeout. Exists because the operator
runner's shell rejects compound polling loops.
"""
import os
import sys
import time


def missing(work_dir):
    names = os.listdir(work_dir)
    batches = sorted(n[6:8] for n in names if n.startswith("batch-") and n.endswith(".json"))
    return [nn for nn in batches if f"out-{nn}.json" not in names]


def main():
    work_dir = sys.argv[1]
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 300
    deadline = time.time() + timeout
    while True:
        left = missing(work_dir)
        if not left:
            print("all out files present")
            return 0
        if time.time() >= deadline:
            print("timeout; missing:", " ".join(left))
            return 1
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
