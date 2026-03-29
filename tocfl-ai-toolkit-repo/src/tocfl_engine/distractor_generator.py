from __future__ import annotations


class DistractorGenerator:
    def generate(self, correct: str, vocab_words: list[str]) -> list[str]:
        pool = [word for word in vocab_words if word != correct]
        fallbacks = ["杯子", "叉子", "盤子", "水果"]
        options = []
        for item in pool + fallbacks:
            if item != correct and item not in options:
                options.append(item)
            if len(options) == 3:
                break
        return options
