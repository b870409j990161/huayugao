from __future__ import annotations


class Validator:
    def validate(self, question: dict) -> None:
        if len(question["options"]) != 4:
            raise ValueError("Each question must have exactly 4 options.")
        if not 0 <= question["answer"] < 4:
            raise ValueError("Answer index out of range.")
        if len(set(question["options"])) != 4:
            raise ValueError("Options must be unique.")
