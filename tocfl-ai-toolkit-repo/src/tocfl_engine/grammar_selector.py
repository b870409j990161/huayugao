from __future__ import annotations

import json
from pathlib import Path


LEVEL_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4}


class GrammarSelector:
    def __init__(self, data_dir: Path) -> None:
        self.items = json.loads((data_dir / "grammar.json").read_text(encoding="utf-8"))

    def select(self, level: str, requested: list[str] | None = None, limit: int = 1) -> list[dict]:
        if requested:
            selected = [item for item in self.items if item["pattern"] in requested]
            if selected:
                return selected[:limit]
        target = LEVEL_ORDER[level]
        candidates = [item for item in self.items if LEVEL_ORDER[item["level"]] <= target]
        return candidates[:limit]
