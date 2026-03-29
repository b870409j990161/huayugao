from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "packs" / "generated"
MANIFEST_PATH = OUTPUT_DIR / "manifest.generated.json"


TOPICS = [
    ("01", "個人資料", "自我介紹"),
    ("02", "飲食", "餐廳點餐"),
    ("03", "旅行", "交通行程"),
    ("04", "購物", "商品比較"),
    ("05", "健康", "健康提醒"),
    ("06", "居住", "社區生活"),
    ("07", "休閒", "活動安排"),
    ("08", "工作", "職場任務"),
    ("09", "科技", "數位工具"),
    ("10", "公共服務", "公告通知"),
    ("11", "教育", "校園生活"),
]

LEVELS = [
    ("A2", 2, "進階"),
    ("B1", 3, "高階"),
    ("B2", 4, "流利"),
]

NAMES = ["小安", "美玲", "志明", "佳琪", "大衛", "安娜", "建宏", "佩珊"]
PLACES = ["臺北", "臺中", "臺南", "高雄", "新竹", "花蓮"]
TIMES = ["明天早上", "今天下午", "下週一", "這個週末", "晚上八點", "中午十二點"]
TASKS = ["開會", "上課", "參加活動", "搭車", "交報告", "看醫生", "買東西", "準備展覽"]


@dataclass(frozen=True)
class ModeConfig:
    key: str
    label: str
    description: str
    tutorial_count: int = 10
    core_count: int = 500


MODES = [
    ModeConfig("topic_mode", "主題練習", "依主題抽題，適合平日練習與暖身。"),
    ModeConfig("story_mode", "主線闖關", "用章節與場景推進的學習任務。"),
    ModeConfig("review_mode", "錯題復健", "把常錯知識點換情境再練一次。"),
    ModeConfig("mock_exam_mode", "模擬考", "用正式節奏練習計時與穩定度。"),
    ModeConfig("listening_mode", "聽力任務", "以情境對話與廣播完成任務。"),
    ModeConfig("news_mode", "新聞改寫", "閱讀改寫新聞與短文，掌握重點。"),
]


def choose_level(index: int) -> tuple[str, int, str]:
    return LEVELS[index % len(LEVELS)]


def choose_topic(index: int) -> tuple[str, str, str]:
    return TOPICS[index % len(TOPICS)]


def choose_name(index: int) -> str:
    return NAMES[index % len(NAMES)]


def choose_place(index: int) -> str:
    return PLACES[index % len(PLACES)]


def choose_time(index: int) -> str:
    return TIMES[index % len(TIMES)]


def choose_task(index: int) -> str:
    return TASKS[index % len(TASKS)]


def build_options(correct_text: str, distractors: list[str]) -> tuple[list[dict], str]:
    option_keys = ["A", "B", "C", "D"]
    answer_index = 1
    texts = [distractors[0], correct_text, distractors[1], distractors[2]]
    options = [
        {"optionKey": key, "optionText": text, "optionOrder": order}
        for order, (key, text) in enumerate(zip(option_keys, texts), start=1)
    ]
    return options, option_keys[answer_index]


def base_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    topic_code, topic_name, subtopic_name = choose_topic(item_index)
    level, tbcl_level, band = choose_level(item_index)
    return {
        "itemCode": f"{mode.key.upper()}-{'T' if tutorial else 'C'}-{item_index + 1:04d}",
        "tocflLevel": level,
        "tbclLevel": tbcl_level,
        "tocflBand": band,
        "topic": {
            "topicCode": topic_code,
            "topicName": topic_name,
            "subtopicCode": f"{topic_code}-{(item_index % 3) + 1:02d}",
            "subtopicName": subtopic_name,
        },
        "quality": {
            "fairnessStatus": "passed",
            "originalityStatus": "passed",
            "logicStatus": "passed",
        },
        "superLevelWordAudit": [],
        "tutorialFocus": "基礎理解" if tutorial else None,
    }


def build_topic_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    person = choose_name(item_index)
    place = choose_place(item_index)
    time = choose_time(item_index)
    task = choose_task(item_index)
    item["itemType"] = "reading"
    item["itemSubtype"] = "short_passage_comprehension"
    item["indicator"] = {
        "code": "R-topic-core",
        "description": "能在熟悉主題的短文中抓出明確訊息。",
    }
    item["stem"] = {
        "title": f"{item['topic']['topicName']}情境",
        "contextSentence": f"{person} 正在安排和 {item['topic']['topicName']} 有關的事情。",
        "text": f"{time}，{person} 要去 {place}{task}。他先收到一則提醒：如果超過原定時間，就要先通知窗口，並重新確認地點和費用。",
    }
    item["questionText"] = f"根據短文，{person} 最需要先確認什麼？"
    options, answer = build_options(
        "是否需要先通知窗口",
        ["今天要不要吃早餐", "朋友有沒有放假", "家裡的電燈有沒有關"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "短文明確提到變動時要先通知窗口，所以重點是確認是否需要先通知。"
    return item


def build_story_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    chapter = (item_index % 5) + 1
    person = choose_name(item_index)
    task = choose_task(item_index + 1)
    item["itemType"] = "reading"
    item["itemSubtype"] = "inference"
    item["indicator"] = {
        "code": "R-story-infer",
        "description": "能結合情境資訊推論角色的下一步。",
    }
    item["stem"] = {
        "title": f"第 {chapter} 章任務",
        "contextSentence": f"{person} 正在完成主線任務。",
        "text": f"{person} 原本計畫今天完成 {task}，但臨時收到隊友訊息，說關鍵資料要到晚上才會送到。若現在就出發，可能白跑一趟；若改成先整理其他工作，明天就能直接完成任務。",
    }
    item["questionText"] = "根據情境，角色最合理的選擇是什麼？"
    options, answer = build_options(
        "先整理其他工作，再等資料到齊",
        ["立刻放棄任務", "直接忽略隊友訊息", "把資料問題交給陌生人處理"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "短文在比較兩種安排後，明顯支持先整理其他工作、避免白跑。"
    return item


def build_review_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    person = choose_name(item_index)
    item["itemType"] = "reading"
    item["itemSubtype"] = "remedial_choice"
    item["indicator"] = {
        "code": "R-review-fix",
        "description": "能在簡化情境中重新辨認關鍵資訊。",
    }
    item["stem"] = {
        "title": "錯題重練",
        "contextSentence": f"這是 {person} 上次答錯後重新整理的版本。",
        "text": f"老師提醒：先看時間，再看地點，最後才決定要不要改變安排。{person} 上次忽略了時間，這次要重新判斷。",
    }
    item["questionText"] = "如果要避免再答錯，第一步應該做什麼？"
    options, answer = build_options(
        "先確認時間資訊",
        ["直接猜最長的選項", "先看自己喜歡哪個答案", "跳過題幹只看選項"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "題幹清楚說明先看時間，再看地點，因此第一步就是確認時間。"
    return item


def build_mock_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    person = choose_name(item_index)
    place = choose_place(item_index)
    item_type = "listening" if item_index % 2 else "reading"
    item["itemType"] = item_type
    item["itemSubtype"] = "exam_style"
    item["indicator"] = {
        "code": "R-mock-exam" if item_type == "reading" else "L-mock-exam",
        "description": "能在接近正式測驗的節奏下判斷主要訊息。",
    }
    item["stem"] = {
        "title": "模擬考題組",
        "contextSentence": f"{person} 收到一則和 {place} 有關的資訊。",
        "text": f"公告指出，今天活動地點改到 {place} 的新場地，報到時間提前三十分鐘。若無法準時到場，請先線上回覆。",
    }
    if item_type == "listening":
        item["audio"] = {
            "speakerMap": {"speaker1": "廣播員"},
            "ttsScript": {"normal": item["stem"]["text"]},
        }
    item["questionText"] = "這題最重要的提醒是什麼？"
    options, answer = build_options(
        "留意地點變更與提早報到",
        ["一定要取消活動", "只要帶水壺就好", "活動改成下個月舉行"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "資訊重點是地點改變和時間提前，兩者都屬於正式測驗常考的明確訊息。"
    return item


def build_listening_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    person = choose_name(item_index)
    task = choose_task(item_index)
    item["itemType"] = "listening"
    item["itemSubtype"] = "dialogue_comprehension"
    item["indicator"] = {
        "code": "L-situation-task",
        "description": "能聽懂情境對話中的任務安排與建議。",
    }
    dialogue = (
        f"{person}：我今天要去 {task}，可是時間有點來不及。"
        f"朋友：你先確認地點，如果路上太遠，就改搭比較快的車。"
    )
    item["stem"] = {
        "title": "情境對話",
        "contextSentence": "請聽下面的短對話。",
        "text": dialogue,
    }
    item["audio"] = {
        "speakerMap": {"speaker1": person, "speaker2": "朋友"},
        "ttsScript": {"normal": dialogue},
    }
    item["questionText"] = "朋友先建議他做什麼？"
    options, answer = build_options(
        "先確認地點",
        ["先取消事情", "先去買飲料", "先請假一整天"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "朋友第一句建議就是先確認地點，再決定後續交通安排。"
    return item


def build_news_item(mode: ModeConfig, item_index: int, tutorial: bool) -> dict:
    item = base_item(mode, item_index, tutorial)
    place = choose_place(item_index)
    item["itemType"] = "reading"
    item["itemSubtype"] = "rewritten_news"
    item["indicator"] = {
        "code": "R-news-rewrite",
        "description": "能讀懂改寫新聞與公共資訊的主要建議。",
    }
    news_text = (
        f"{place} 市政府今天提醒，近期天氣變化大，早晚溫差明顯。"
        "專家建議民眾出門前先注意最新資訊，並依活動時間準備外套或飲水。"
        "如果本身容易不舒服，更要避免長時間待在通風不佳的地方。"
    )
    item["stem"] = {
        "title": "改寫新聞",
        "contextSentence": "下面是一則改寫後的新聞短文。",
        "text": news_text,
    }
    item["questionText"] = "這則新聞最主要想提醒民眾什麼？"
    options, answer = build_options(
        "依天氣與身體狀況調整外出準備",
        ["每天都要取消行程", "一定要留在家裡三天", "只要看新聞標題就夠了"],
    )
    item["options"] = options
    item["answerOptionKey"] = answer
    item["explanationText"] = "新聞重點是因應天氣變化做好準備，而不是完全停止活動。"
    if item_index % 7 == 0:
        item["superLevelWordAudit"] = [
            {
                "wordText": "通風不佳",
                "detectedLevel": "X",
                "inVocabList": False,
                "replacementText": "空氣不太流通",
                "keepWord": True,
                "keepReason": "搭配上下文仍可理解，且屬新聞語境常見詞。",
            }
        ]
        item["quality"]["originalityStatus"] = "warning"
    return item


BUILDERS = {
    "topic_mode": build_topic_item,
    "story_mode": build_story_item,
    "review_mode": build_review_item,
    "mock_exam_mode": build_mock_item,
    "listening_mode": build_listening_item,
    "news_mode": build_news_item,
}


def build_pack(mode: ModeConfig, tutorial: bool) -> dict:
    count = mode.tutorial_count if tutorial else mode.core_count
    builder = BUILDERS[mode.key]
    items = [builder(mode, idx, tutorial) for idx in range(count)]
    pack_id = f"{mode.key}-{'tutorial' if tutorial else 'core'}"
    return {
        "packId": pack_id,
        "mode": mode.key,
        "label": mode.label,
        "experience": "tutorial" if tutorial else "core",
        "itemType": "mixed" if mode.key not in {"listening_mode", "news_mode"} else ("listening" if mode.key == "listening_mode" else "reading"),
        "count": count,
        "description": mode.description,
        "items": items,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def generate() -> None:
    random.seed(42)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {"version": "1.0.0", "packs": []}

    for mode in MODES:
        for tutorial in (True, False):
            pack = build_pack(mode, tutorial)
            file_name = f"{pack['packId']}.json"
            write_json(OUTPUT_DIR / file_name, pack)
            manifest["packs"].append(
                {
                    "id": pack["packId"],
                    "mode": mode.key,
                    "label": mode.label,
                    "experience": pack["experience"],
                    "itemType": pack["itemType"],
                    "count": pack["count"],
                    "description": mode.description,
                    "file": f"packs/generated/{file_name}",
                }
            )

    write_json(MANIFEST_PATH, manifest)
    print(f"Generated {len(manifest['packs'])} packs into {OUTPUT_DIR}")


if __name__ == "__main__":
    generate()
