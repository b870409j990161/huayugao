from __future__ import annotations

import argparse
from pathlib import Path

from .article_rewriter import ArticleRewriter
from .distractor_generator import DistractorGenerator
from .exporter import Exporter
from .grammar_selector import GrammarSelector
from .news_fetcher import NewsFetcher
from .news_question_generator import NewsQuestionGenerator
from .question_builder import QuestionBuilder
from .template_engine import TemplateEngine
from .topic_selector import TopicSelector
from .validator import Validator
from .vocab_selector import VocabSelector


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / 'data'
OUTPUT_PATH = BASE_DIR / 'output' / 'sample_questions.json'
NEWS_OUTPUT_PATH = BASE_DIR / 'output' / 'news_questions.json'


def generate_questions(params: dict) -> list[dict]:
    topic_selector = TopicSelector(DATA_DIR)
    vocab_selector = VocabSelector(DATA_DIR)
    grammar_selector = GrammarSelector(DATA_DIR)
    template_engine = TemplateEngine(DATA_DIR)
    distractor_generator = DistractorGenerator()
    question_builder = QuestionBuilder()
    validator = Validator()

    topic, subtopic = topic_selector.get_subtopic(params['topic_id'], params['subtopic_id'])
    vocab = vocab_selector.select(params['level'], subtopic['scenarios'][0], limit=3)
    grammar = grammar_selector.select(params['level'], params.get('grammar'), limit=1)

    vocab_words = [item['word'] for item in vocab]
    questions: list[dict] = []
    for i in range(1, params.get('question_count', 1) + 1):
        content, question_text = template_engine.render(params['type'], params['subtype'], vocab_words)
        correct = vocab_words[0] if vocab_words else '水果'
        distractors = distractor_generator.generate(correct, vocab_words)
        question = question_builder.build(
            index=i,
            qtype=params['type'],
            subtype=params['subtype'],
            level=params['level'],
            topic=topic,
            subtopic=subtopic,
            grammar=grammar,
            content=content,
            question_text=question_text,
            correct=correct,
            distractors=distractors,
        ).to_dict()
        validator.validate(question)
        questions.append(question)
    return questions


def generate_news_questions(params: dict) -> list[dict]:
    topic_selector = TopicSelector(DATA_DIR)
    fetcher = NewsFetcher(DATA_DIR)
    rewriter = ArticleRewriter()
    generator = NewsQuestionGenerator()
    validator = Validator()

    topic, subtopic = topic_selector.get_subtopic(params['topic_id'], params['subtopic_id'])
    articles = fetcher.fetch_articles(params['query'], limit=params.get('article_limit', 3))
    if not articles:
        raise RuntimeError('No matching news articles were found from configured RSS sources.')
    article = articles[0]
    rewritten = rewriter.rewrite(
        article.title,
        article.content or article.summary,
        params['level'],
        forced_keywords=params.get('keywords') or [],
    )
    questions = [q.to_dict() for q in generator.build_questions(
        article=rewritten,
        level=params['level'],
        topic=topic,
        subtopic=subtopic,
        count=params.get('question_count', 4),
    )]
    for question in questions:
        question['metadata'] = question.get('metadata', {}) | {
            'source_url': article.url,
            'source_name': article.source,
            'published': article.published,
        }
        validator.validate(question)
    return questions


def cli() -> None:
    parser = argparse.ArgumentParser(description='Generate TOCFL questions')
    subparsers = parser.add_subparsers(dest='command', required=True)

    static_parser = subparsers.add_parser('generate', help='Generate scaffold questions from templates')
    static_parser.add_argument('--type', required=True, choices=['listening', 'reading'])
    static_parser.add_argument('--subtype', required=True)
    static_parser.add_argument('--level', required=True, choices=['A1', 'A2', 'B1', 'B2'])
    static_parser.add_argument('--topic-id', required=True)
    static_parser.add_argument('--subtopic-id', required=True)
    static_parser.add_argument('--question-count', type=int, default=1)
    static_parser.add_argument('--grammar', action='append')

    news_parser = subparsers.add_parser('generate-news', help='Fetch news, rewrite, and generate TOCFL reading questions')
    news_parser.add_argument('--query', required=True)
    news_parser.add_argument('--level', required=True, choices=['A1', 'A2', 'B1', 'B2'])
    news_parser.add_argument('--topic-id', required=True)
    news_parser.add_argument('--subtopic-id', required=True)
    news_parser.add_argument('--question-count', type=int, default=4)
    news_parser.add_argument('--article-limit', type=int, default=3)
    news_parser.add_argument('--keyword', action='append', dest='keywords')

    args = parser.parse_args()

    if args.command == 'generate':
        params = {
            'type': args.type,
            'subtype': args.subtype,
            'level': args.level,
            'topic_id': args.topic_id,
            'subtopic_id': args.subtopic_id,
            'question_count': args.question_count,
            'grammar': args.grammar,
        }
        questions = generate_questions(params)
        Exporter().export_json(questions, OUTPUT_PATH)
        print(f'Generated {len(questions)} questions -> {OUTPUT_PATH}')
        return

    params = {
        'query': args.query,
        'level': args.level,
        'topic_id': args.topic_id,
        'subtopic_id': args.subtopic_id,
        'question_count': args.question_count,
        'article_limit': args.article_limit,
        'keywords': args.keywords,
    }
    questions = generate_news_questions(params)
    Exporter().export_json(questions, NEWS_OUTPUT_PATH)
    print(f'Generated {len(questions)} news-based questions -> {NEWS_OUTPUT_PATH}')


if __name__ == '__main__':
    cli()
