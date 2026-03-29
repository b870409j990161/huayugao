from pathlib import Path

from tocfl_engine.article_rewriter import ArticleRewriter
from tocfl_engine.news_question_generator import NewsQuestionGenerator
from tocfl_engine.topic_selector import TopicSelector


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'


def test_article_rewriter_respects_level_limit() -> None:
    rewriter = ArticleRewriter()
    article = rewriter.rewrite(
        '台南校園活動',
        '台南一所大學今天舉辦文化活動。很多學生參加，也有老師一起介紹台灣文化。活動結束後，大家說很高興。',
        'A2',
    )
    assert len(article.rewritten_text) <= 120
    assert '活動' in article.rewritten_text


def test_news_question_generator_builds_four_choice_questions() -> None:
    rewriter = ArticleRewriter()
    topic, subtopic = TopicSelector(DATA_DIR).get_subtopic('11', '11-01')
    article = rewriter.rewrite(
        '學校舉辦比賽',
        '學校今天舉辦中文比賽，很多學生參加。老師說這個活動可以讓大家更喜歡學中文。',
        'A2',
    )
    questions = NewsQuestionGenerator().build_questions(article=article, level='A2', topic=topic, subtopic=subtopic, count=4)
    assert len(questions) == 4
    assert all(len(q.options) == 4 for q in questions)
