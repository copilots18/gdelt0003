#!/usr/bin/env python3
"""Default-ready short-video batch generation.

The default batch should be pre-generated and visible immediately on the Pages site.
The preview-only mode is still available for testing and custom tailoring.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_highlights(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, list) else []


def select_default_batch(items: Iterable[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
    ranked = sorted(items, key=lambda item: item.get("score", 0), reverse=True)
    return ranked[:count]


def generate_plan(data_path: Path, count: int = 3, authorized: bool = True) -> Dict[str, Any]:
    items = load_highlights(data_path)
    default_batch = select_default_batch(items, count=count)

    if not authorized:
        return {
            "status": "discover",
            "authorized": False,
            "message": "Preview mode only; default batch is visible, but generation stays offline until the default plan is explicitly approved.",
            "batch_count": len(default_batch),
            "batch": default_batch,
            "source": str(data_path),
        }

    return {
        "status": "create",
        "authorized": True,
        "message": "Default batch is ready and can be published directly on the Pages site.",
        "batch_count": len(default_batch),
        "batch": default_batch,
        "source": str(data_path),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the default short-video batch plan.")
    parser.add_argument("--data", type=Path, default=Path("data/highlights.json"), help="Path to highlight JSON file.")
    parser.add_argument("--count", type=int, default=3, help="Default number of highlight clips in the batch.")
    parser.add_argument("--discover-only", action="store_true", help="Preview the default batch without publishing it.")
    args = parser.parse_args()

    authorized = not args.discover_only
    result = generate_plan(args.data, count=args.count, authorized=authorized)
    print(json.dumps(result, ensure_ascii=False, indent=2))
