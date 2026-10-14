"""nmcu build [--offline] [--through YYYY-MM]"""

from __future__ import annotations

import argparse
import json
import sys

from .build import build
from .checks import BuildError


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nmcu")
    ap.add_argument("command", choices=["build"])
    ap.add_argument("--offline", action="store_true", help="use cached zips; don't ask NCUA's page")
    ap.add_argument("--through", help="last quarter to build, e.g. 2026-06")
    a = ap.parse_args(argv)
    try:
        manifest = build(offline=a.offline, through=a.through)
    except BuildError as e:
        print(f"build stopped: {e}", file=sys.stderr)
        return 1
    print(json.dumps({k: manifest[k] for k in ("latest", "credit_unions_latest", "flags")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
