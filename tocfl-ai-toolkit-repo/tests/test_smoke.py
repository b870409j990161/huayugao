from tocfl_engine.main import generate_questions


def test_generate_questions_smoke() -> None:
    questions = generate_questions(
        {
            "type": "reading",
            "subtype": "cloze",
            "level": "A2",
            "topic_id": "02",
            "subtopic_id": "02-02",
            "question_count": 2,
            "grammar": ["因為……所以……"],
        }
    )
    assert len(questions) == 2
    assert all(len(q["options"]) == 4 for q in questions)
