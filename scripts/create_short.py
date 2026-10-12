#!/usr/bin/env python3
"""Safe default short-video candidate generation.

This generator is intentionally conservative: it can discover and rank candidates,
but it refuses to create or process media without explicit authorization.
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


def generate_plan(data_path: Path, count: int = 3, authorized: bool = False) -> Dict[str, Any]:
    items = load_highlights(data_path)
    default_batch = select_default_batch(items, count=count)

    if not authorized:
        return {
            "status": "discover",
            "authorized": False,
            "message": "No media generation is allowed without explicit authorization.",
            "batch_count": len(default_batch),
            "batch": default_batch,
            "source": str(data_path),
        }

    return {
        "status": "create",
        "authorized": True,
        "message": "Authorization confirmed; default batch is ready for creation.",
        "batch_count": len(default_batch),
        "batch": default_batch,
        "source": str(data_path),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a safe short-video generation plan.")
    parser.add_argument("--data", type=Path, default=Path("data/highlights.json"), help="Path to highlight JSON file.")
    parser.add_argument("--count", type=int, default=3, help="Default number of highlight clips in the batch.")
    parser.add_argument("--authorize", action="store_true", help="Authorize creation of clips.")
    args = parser.parse_args()

    result = generate_plan(args.data, count=args.count, authorized=args.authorize)
    print(json.dumps(result, ensure_ascii=False, indent=2))
