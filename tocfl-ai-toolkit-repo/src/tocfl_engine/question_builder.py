from __future__ import annotations

from .models import Question


class QuestionBuilder:
    def build(
        self,
        *,
        index: int,
        qtype: str,
        subtype: str,
        level: str,
        topic: dict,
        subtopic: dict,
        grammar: list[dict],
        content: str,
        question_text: str,
        correct: str,
        distractors: list[str],
    ) -> Question:
        options = [correct] + distractors[:3]
        answer = 0
        explanation = f"根據內容可知正確答案是「{correct}」。"
        qid = f"{level}-{qtype[:1].upper()}-{topic['id']}-{subtopic['id']}-{index:04d}"
        tts_script = {"normal": content, "slow": " ".join(list(content))}
        return Question(
            id=qid,
            type=qtype,
            subtype=subtype,
            level=level,
            topic_id=topic["id"],
            topic_name=topic["name"],
            subtopic_id=subtopic["id"],
            subtopic_name=subtopic["name"],
            situation=subtopic["scenarios"][0],
            grammar=[g["pattern"] for g in grammar],
            content=content,
            question=question_text,
            options=options,
            answer=answer,
            explanation=explanation,
            tts_script=tts_script,
            metadata={"source": "scaffold_sample"},
        )
