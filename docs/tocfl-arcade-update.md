# TOCFL Arcade Update Flow

## What is included

- `tocfl-arcade.html`
  - the playable multi-mode game page
- `packs/generated/manifest.generated.json`
  - base pack index
- `tools/generate_tocfl_game_content.py`
  - regenerates all tutorial and core banks
- `tools/validate_tocfl_game_content.py`
  - checks counts and basic item structure

## Base rebuild

Run:

```powershell
python tools\generate_tocfl_game_content.py
python tools\validate_tocfl_game_content.py
```

This recreates:

- 6 modes
- 10 tutorial items per mode
- 500 core items per mode

## Upload update bundles in the game page

Open:

- `tocfl-arcade.html`

Use the `Import Update Bundle` file input.

Accepted shape:

```json
{
  "version": "1.0.0",
  "packs": [
    {
      "packId": "custom-topic-pack",
      "mode": "topic_mode",
      "label": "Topic Practice",
      "experience": "core",
      "itemType": "mixed",
      "description": "Imported update",
      "items": []
    }
  ]
}
```

The imported packs are saved in browser local storage and merged into the game library immediately.

## Repo-side update strategy

Use one of these approaches:

1. Edit `tools/generate_tocfl_game_content.py` to change templates or scale.
2. Replace generated pack JSON files in `packs/generated/`.
3. Build a custom bundle JSON and upload it through the page for local testing.
4. After review, move approved custom packs into `packs/generated/` and add them to `manifest.generated.json`.

## Recommended release checklist

1. Run the generator.
2. Run the validator.
3. Open the game page through a local static server.
4. Test one tutorial and one practice run in each mode.
5. Upload one custom bundle and confirm it appears in the mode list.
