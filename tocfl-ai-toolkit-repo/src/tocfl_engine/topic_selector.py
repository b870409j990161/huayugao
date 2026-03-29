from __future__ import annotations

import json
from pathlib import Path


class TopicSelector:
    def __init__(self, data_dir: Path) -> None:
        self.data = json.loads((data_dir / "tocfl_topics.json").read_text(encoding="utf-8"))

    def get_topic(self, topic_id: str) -> dict:
        for topic in self.data["topics"]:
            if topic["id"] == topic_id:
                return topic
        raise ValueError(f"Unknown topic_id: {topic_id}")

    def get_subtopic(self, topic_id: str, subtopic_id: str) -> tuple[dict, dict]:
        topic = self.get_topic(topic_id)
        for subtopic in topic["subtopics"]:
            if subtopic["id"] == subtopic_id:
                return topic, subtopic
        raise ValueError(f"Unknown subtopic_id: {subtopic_id}")
