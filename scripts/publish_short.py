#!/usr/bin/env python3
"""Publishing layer for short-video outputs.

By default it only prepares a publish plan and refuses to finalise without explicit authorization.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_short import generate_plan


def publish_plan(data_path: Path, count: int = 3, authorized: bool = False, output_path: Path | None = None) -> Dict[str, Any]:
    plan = generate_plan(data_path, count=count, authorized=authorized)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(plan, handle, ensure_ascii=False, indent=2)
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish a short-video batch plan safely.")
    parser.add_argument("--data", type=Path, default=Path("data/highlights.json"), help="Path to highlight JSON file.")
    parser.add_argument("--count", type=int, default=3, help="Number of clips in the batch.")
    parser.add_argument("--authorize", action="store_true", help="Explicitly authorize publication.")
    parser.add_argument("--output", type=Path, default=Path("data/generated/default_batch.json"), help="Where to persist the generated plan.")
    args = parser.parse_args()

    result = publish_plan(args.data, count=args.count, authorized=args.authorize, output_path=args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
