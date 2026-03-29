from __future__ import annotations

import random

from .article_rewriter import RewrittenArticle
from .distractor_generator import DistractorGenerator
from .models import Question


QUESTION_TEXTS = {
    'main_idea': '這篇短文主要在說什麼？',
    'detail': '根據短文，下列哪一個是對的？',
    'title': '下列哪一個最適合做這篇短文的標題？',
    'vocab': '短文中的「{word}」最接近下面哪一個意思？',
}


class NewsQuestionGenerator:
    def __init__(self) -> None:
        self.distractor_generator = DistractorGenerator()

    def build_questions(self, *, article: RewrittenArticle, level: str, topic: dict, subtopic: dict, count: int = 5) -> list[Question]:
        questions: list[Question] = []
        title_options = self._build_title_options(article)
        questions.append(self._make_question(
            qid=f'{level}-R-{topic["id"]}-{subtopic["id"]}-9001',
            level=level,
            topic=topic,
            subtopic=subtopic,
            article=article,
            question_text=QUESTION_TEXTS['title'],
            options=title_options,
            answer=0,
            explanation='短文內容圍繞這個標題展開。',
            metadata={'source': 'news_rewrite', 'question_kind': 'title'}
        ))

        main_idea = self._guess_main_idea(article)
        main_options = [main_idea] + self.distractor_generator.generate(main_idea, article.keywords or ['活動', '新聞', '生活'])[:3]
        questions.append(self._make_question(
            qid=f'{level}-R-{topic["id"]}-{subtopic["id"]}-9002',
            level=level,
            topic=topic,
            subtopic=subtopic,
            article=article,
            question_text=QUESTION_TEXTS['main_idea'],
            options=main_options,
            answer=0,
            explanation='正確答案概括了全文重點。',
            metadata={'source': 'news_rewrite', 'question_kind': 'main_idea'}
        ))

        detail_answer = article.keywords[0] if article.keywords else article.rewritten_title
        detail_options = [detail_answer] + self.distractor_generator.generate(detail_answer, article.keywords or ['交通', '學校', '活動'])[:3]
        questions.append(self._make_question(
            qid=f'{level}-R-{topic["id"]}-{subtopic["id"]}-9003',
            level=level,
            topic=topic,
            subtopic=subtopic,
            article=article,
            question_text=QUESTION_TEXTS['detail'],
            options=detail_options,
            answer=0,
            explanation='正確答案和短文出現的重點名詞一致。',
            metadata={'source': 'news_rewrite', 'question_kind': 'detail'}
        ))

        vocab_word = (article.keywords[0] if article.keywords else '活動')
        vocab_options = [self._simple_gloss(vocab_word)] + self._vocab_distractors(vocab_word)
        questions.append(self._make_question(
            qid=f'{level}-R-{topic["id"]}-{subtopic["id"]}-9004',
            level=level,
            topic=topic,
            subtopic=subtopic,
            article=article,
            question_text=QUESTION_TEXTS['vocab'].format(word=vocab_word),
            options=vocab_options,
            answer=0,
            explanation=f'「{vocab_word}」在本文中對應這個意思。',
            metadata={'source': 'news_rewrite', 'question_kind': 'vocab'}
        ))

        return questions[:count]

    def _make_question(self, *, qid: str, level: str, topic: dict, subtopic: dict, article: RewrittenArticle, question_text: str, options: list[str], answer: int, explanation: str, metadata: dict) -> Question:
        options = options[:4]
        if len(options) < 4:
            filler = ['學校新聞', '生活消息', '交通問題', '文化活動']
            for item in filler:
                if item not in options:
                    options.append(item)
                if len(options) == 4:
                    break
        return Question(
            id=qid,
            type='reading',
            subtype='short_passage_comprehension',
            level=level,
            topic_id=topic['id'],
            topic_name=topic['name'],
            subtopic_id=subtopic['id'],
            subtopic_name=subtopic['name'],
            situation=subtopic['scenarios'][0],
            grammar=[],
            content=article.rewritten_text,
            question=question_text,
            options=options,
            answer=answer,
            explanation=explanation,
            tts_script={'normal': article.rewritten_text, 'slow': ' '.join(list(article.rewritten_text))},
            metadata=metadata | {'original_title': article.original_title, 'rewritten_title': article.rewritten_title},
        )

    def _build_title_options(self, article: RewrittenArticle) -> list[str]:
        correct = article.rewritten_title
        distractors = [
            f'關於{kw}的通知' for kw in article.keywords[:3]
        ]
        if len(distractors) < 3:
            distractors.extend(['今天的校園生活', '一次特別的活動', '大家的日常習慣'])
        return [correct] + distractors[:3]

    def _guess_main_idea(self, article: RewrittenArticle) -> str:
        if article.keywords:
            return f'介紹{article.keywords[0]}相關的最新情況'
        return '介紹一則和生活有關的新聞'

    def _simple_gloss(self, word: str) -> str:
        gloss = {
            '台灣': '一個地方名稱',
            '學生': '在學校學習的人',
            '活動': '大家一起參加的事情',
            '交通': '人和車移動的方式',
            '學校': '上課學習的地方',
            '文化': '一個地方的生活特色',
            '旅遊': '到別的地方玩',
            '夜市': '晚上可以吃東西和買東西的地方',
            '比賽': '大家一起比較表現的活動',
            '餐廳': '吃飯的地方',
            '天氣': '每天冷熱下雨的情況',
            '捷運': '城市裡的軌道交通工具',
            '公車': '在路上載客的大車',
        }
        return gloss.get(word, '和生活有關的詞')

    def _vocab_distractors(self, word: str) -> list[str]:
        pool = [
            '一種水果', '一種顏色', '一種衣服', '一種動物', '一個人的名字'
        ]
        random.seed(word)
        random.shuffle(pool)
        return pool[:3]
