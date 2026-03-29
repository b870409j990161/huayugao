# TOCFL 遊戲化自動出題引擎規格整理

本檔案是依據原始 Word 規格書轉寫成適合 GitHub 閱讀的 Markdown 版本。

## 文件用途

提供工程師、教學設計者與後續維護者作為統一開發藍本。

## 適用級別

- A1
- A2
- B1
- B2

## 核心資料檔

- `data/tocfl_topics.json`
- `data/question_generation_config.json`
- `data/question_schema_example.json`
- `data/game_mode_config.json`
- `data/vocab.json`
- `data/grammar.json`
- `data/templates.json`

## 系統核心公式

主題 × 子情境 × 詞彙 × 語法 × 題型 × 難度 → 題目

## 第一版系統範圍

支援：

- 聽力題生成
- 閱讀題生成
- 主題式出題
- 分級式出題
- 選項與干擾項生成
- 解析生成
- 音檔腳本與 TTS 腳本輸出

暫不支援：

- 寫作題
- 口說題
- 真人錄音
- 自動口說評分
- 圖像辨識題

## 模組化架構

- `topic_selector.py`
- `vocab_selector.py`
- `grammar_selector.py`
- `template_engine.py`
- `question_builder.py`
- `distractor_generator.py`
- `validator.py`
- `exporter.py`
- `main.py`

## 驗收標準

- 至少可依 `topic_id` 生成題目
- 至少可依 `level` 控制難度
- 可生成 `listening` 與 `reading` 題
- 每題皆為 4 選 1
- 輸出為固定 JSON
- 支援 `explanation` 與 `tts_script`
- 干擾項合理，不是隨機填入

## 建議後續工作

1. 把完整 TOCFL 詞彙表整理進 `vocab.json`
2. 把完整語法點整理進 `grammar.json`
3. 新增更多模板到 `templates.json`
4. 接入新聞抓取與改寫模組
5. 接入前端遊戲或 API 服務
