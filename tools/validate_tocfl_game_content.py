from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "packs" / "generated" / "manifest.generated.json"
EXPECTED = {
    "topic_mode": {"tutorial": 10, "core": 500},
    "story_mode": {"tutorial": 10, "core": 500},
    "review_mode": {"tutorial": 10, "core": 500},
    "mock_exam_mode": {"tutorial": 10, "core": 500},
    "listening_mode": {"tutorial": 10, "core": 500},
    "news_mode": {"tutorial": 10, "core": 500},
}
REQUIRED_ITEM_FIELDS = {
    "itemCode",
    "itemType",
    "itemSubtype",
    "tocflLevel",
    "tbclLevel",
    "tocflBand",
    "indicator",
    "stem",
    "questionText",
    "options",
    "answerOptionKey",
    "explanationText",
    "quality",
}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seen = {}
    total = 0

    for pack_meta in manifest["packs"]:
      mode = pack_meta["mode"]
      experience = pack_meta["experience"]
      path = ROOT / pack_meta["file"]
      payload = json.loads(path.read_text(encoding="utf-8"))
      items = payload.get("items", [])
      expected_count = EXPECTED[mode][experience]
      if len(items) != expected_count:
          raise SystemExit(f"{mode}/{experience} expected {expected_count}, got {len(items)}")

      for item in items:
          missing = REQUIRED_ITEM_FIELDS - item.keys()
          if missing:
              raise SystemExit(f"{item.get('itemCode', 'unknown')} missing fields: {sorted(missing)}")
          if len(item.get("options", [])) != 4:
              raise SystemExit(f"{item['itemCode']} does not have 4 options")
          if item["itemType"] == "listening" and "audio" not in item:
              raise SystemExit(f"{item['itemCode']} is listening but lacks audio")

      seen[(mode, experience)] = len(items)
      total += len(items)

    print("validated_modes", seen)
    print("total_items", total)


if __name__ == "__main__":
    main()
