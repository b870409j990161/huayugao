from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Question:
    id: str
    type: str
    subtype: str
    level: str
    topic_id: str
    topic_name: str
    subtopic_id: str
    subtopic_name: str
    situation: str
    grammar: list[str]
    content: str
    question: str
    options: list[str]
    answer: int
    explanation: str
    audio_script: dict[str, Any] | None = None
    tts_script: dict[str, str] | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
