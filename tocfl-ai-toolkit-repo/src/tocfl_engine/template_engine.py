from __future__ import annotations

import json
from pathlib import Path


class TemplateEngine:
    def __init__(self, data_dir: Path) -> None:
        self.templates = json.loads((data_dir / "templates.json").read_text(encoding="utf-8"))

    def render(self, qtype: str, subtype: str, vocab_words: list[str]) -> tuple[str, str]:
        template = self.templates[qtype][subtype][0]
        mapping = {
            "word1": vocab_words[0] if len(vocab_words) > 0 else "東西",
            "word2": vocab_words[1] if len(vocab_words) > 1 else "水果",
            "word3": vocab_words[2] if len(vocab_words) > 2 else "筷子",
            "action1": "洗手",
            "action2": "吃飯",
        }
        content = template["content_template"].format(**mapping)
        question = template["question_template"].format(**mapping)
        return content, question
