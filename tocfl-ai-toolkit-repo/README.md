# TOCFL 遊戲化自動出題引擎

這個專案是依據《TOCFL 遊戲化自動出題引擎：完整 JSON 結構與系統規格書整合版》整理成可直接放上 GitHub 的 Python 專案，並補上「抓新聞 → 改寫 → 自動生成 TOCFL 題目」的完整閱讀題流程。

## 目前支援

- 級別：A1、A2、B1、B2
- 題型：聽力、閱讀
- 一般模板出題
- 新聞抓取後改寫成 TOCFL 風格短文
- 依新聞短文自動生成閱讀題
- JSON 輸出給前端、資料庫或遊戲系統

## 專案結構

```text
project/
├─ data/
│  ├─ tocfl_topics.json
│  ├─ question_generation_config.json
│  ├─ question_schema_example.json
│  ├─ game_mode_config.json
│  ├─ news_sources.json
│  ├─ vocab.json
│  ├─ grammar.json
│  └─ templates.json
├─ src/
│  └─ tocfl_engine/
│     ├─ article_rewriter.py
│     ├─ news_fetcher.py
│     ├─ news_question_generator.py
│     ├─ utils.py
│     └─ ...
├─ tests/
├─ output/
└─ docs/
```

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## 用法

### 1. 一般模板出題

```bash
tocfl-generate generate   --type reading   --subtype cloze   --level A2   --topic-id 02   --subtopic-id 02-02   --question-count 3   --grammar "因為……所以……"
```

### 2. 抓新聞、改寫、生成 TOCFL 閱讀題

```bash
tocfl-generate generate-news   --query 校園   --level A2   --topic-id 11   --subtopic-id 11-01   --question-count 4
```

輸出會寫到：

- `output/sample_questions.json`
- `output/news_questions.json`

## 新聞出題流程

1. 從 `data/news_sources.json` 內設定的 RSS 來源抓取新聞列表
2. 依查詢詞篩選標題與摘要
3. 下載文章頁面並抽取本文
4. 依級別做簡化改寫
5. 生成閱讀題，包括：
   - 標題題
   - 主旨題
   - 細節題
   - 詞彙題
6. 輸出固定 JSON

## 模組說明

- `news_fetcher.py`：抓 RSS、抓新聞本文
- `article_rewriter.py`：把新聞改寫成 A1–B2 可控長度短文
- `news_question_generator.py`：依改寫短文出題
- `main.py`：CLI 入口，含 `generate` 與 `generate-news`

## 注意

- 這版已補齊完整流程與程式骨架，但新聞網站的 HTML 結構常會變動，所以 `news_fetcher.py` 的 selector 可能需要依實際來源調整。
- 本環境內沒有對外網路，所以專案中的新聞抓取功能是以可部署程式碼方式補齊，並用本地測試驗證改寫與出題邏輯。
- 若你要升級成真正的 AI 改寫版本，可以再接大型語言模型 API，讓 `article_rewriter.py` 從規則式簡化升級成提示詞改寫。

## 建議下一步

- 補完整 `vocab.json` 與 `grammar.json`
- 加入真正的 LLM 改寫器
- 加入 FastAPI API 層
- 加入前端題庫管理頁
- 增加評分與錯題追蹤
