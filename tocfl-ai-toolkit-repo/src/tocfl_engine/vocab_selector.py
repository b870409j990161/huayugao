from __future__ import annotations

import json
from pathlib import Path


LEVEL_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4}


class VocabSelector:
    def __init__(self, data_dir: Path) -> None:
        self.items = json.loads((data_dir / "vocab.json").read_text(encoding="utf-8"))

    def select(self, level: str, scenario: str, limit: int = 3) -> list[dict]:
        target = LEVEL_ORDER[level]
        candidates = [
            item for item in self.items
            if LEVEL_ORDER[item["level"]] <= target and scenario in item.get("situation", [])
        ]
        if len(candidates) < limit:
            candidates = [item for item in self.items if LEVEL_ORDER[item["level"]] <= target]
        candidates = sorted(candidates, key=lambda x: x.get("frequency", 0), reverse=True)
        return candidates[:limit]
