from __future__ import annotations

from dataclasses import dataclass

from .utils import split_zh_sentences, trim_text_by_chars


LEVEL_CHAR_LIMITS = {
    'A1': 70,
    'A2': 120,
    'B1': 180,
    'B2': 260,
}


@dataclass
class RewrittenArticle:
    original_title: str
    rewritten_title: str
    rewritten_text: str
    keywords: list[str]


class ArticleRewriter:
    def rewrite(self, title: str, content: str, level: str, forced_keywords: list[str] | None = None) -> RewrittenArticle:
        sentences = split_zh_sentences(content)
        if not sentences:
            sentences = [content.strip()] if content.strip() else [title.strip()]
        max_chars = LEVEL_CHAR_LIMITS.get(level, 180)
        selected: list[str] = []
        current = ''
        for sentence in sentences:
            candidate = (current + sentence).strip()
            if len(candidate) > max_chars and selected:
                break
            selected.append(sentence)
            current = ''.join(selected)
            if len(current) >= max_chars * 0.85:
                break
        rewritten_text = ''.join(selected)
        rewritten_text = self._simplify(rewritten_text, level)
        keywords = self.extract_keywords(title + '。' + rewritten_text)
        if forced_keywords:
            for keyword in forced_keywords:
                if keyword not in keywords:
                    keywords.append(keyword)
        rewritten_title = trim_text_by_chars(title, 20)
        return RewrittenArticle(
            original_title=title,
            rewritten_title=rewritten_title,
            rewritten_text=trim_text_by_chars(rewritten_text, max_chars),
            keywords=keywords[:8],
        )

    def extract_keywords(self, text: str) -> list[str]:
        candidates = []
        for token in ['台灣', '學生', '活動', '交通', '學校', '文化', '旅遊', '夜市', '比賽', '餐廳', '天氣', '捷運', '公車']:
            if token in text and token not in candidates:
                candidates.append(token)
        return candidates

    def _simplify(self, text: str, level: str) -> str:
        replacements = {
            '由於': '因為',
            '然而': '但是',
            '此外': '另外',
            '民眾': '大家',
            '表示': '說',
        }
        if level in {'A1', 'A2'}:
            for src, dst in replacements.items():
                text = text.replace(src, dst)
        return text
