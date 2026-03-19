# SCMDB Community Translations

Community-maintained translations for [SCMDB](https://scmdb.dev) — the Star Citizen Mission & Data Browser.

SCMDB displays all data in English by default. This repo provides the tools for community translation teams to create their own language files that users can load in the browser.

## For Translation Teams

### What you need

1. **Python 3.10+** (no external dependencies)
2. **`build_translation.py`** (this repo)
3. **`lang-template-*.json`** (this repo, updated each patch by SCMDB)
4. **Your community `global.ini`** (the Star Citizen translation file your team maintains)

### How to build a translation

```bash
python build_translation.py \
  --template lang-template-4.7.0-ptu.11475995.json \
  --ini path/to/your_global.ini \
  --lang de
```

This produces a `lang-de-4.7.0-ptu.11475995.json` file with a coverage report:

```
==================================================
  Total Keys:       3186
  Translated:       2819 (88.5%)
  Missing:          235 (Fallback: English)
  Placeholder-Only: 50 (Fallback: English)
==================================================
```

Missing keys automatically fall back to English text.

### How to publish your translation

1. Host the generated `lang-*.json` file somewhere publicly accessible:
   - **GitHub** (recommended): Push to your own repo, use the Raw URL
   - **Any web server** with CORS enabled (`Access-Control-Allow-Origin: *`)
   - **GitHub Gist**: Upload and use the Raw URL

2. Share the direct URL with your community:
   ```
   https://raw.githubusercontent.com/your-team/scmdb-translations/main/lang-de-4.7.0-ptu.11475995.json
   ```

3. When a new patch drops:
   - Pull the updated `lang-template-*.json` from this repo
   - Re-run `build_translation.py` with your latest `global.ini`
   - Update your hosted file

### File format

The output JSON contains English + translated text for each key:

```json
{
  "version": "4.7.0-ptu.11475995",
  "sourceLanguage": "en",
  "targetLanguage": "de",
  "keyCount": 3186,
  "keys": {
    "recovery_title": {
      "en": "Getting Our Gear Back",
      "tr": "Unsere Ausruestung zurueckholen"
    },
    "items_commodities_gold_ore": {
      "en": "Gold (Ore)",
      "tr": "Gold (Erz)"
    }
  }
}
```

## For Users

### Quick start (no account needed)

Add `?lang=URL` to any SCMDB page:

```
https://scmdb.dev?lang=https://raw.githubusercontent.com/team-de/scmdb-lang/main/lang-de.json
```

The language preference is saved in your browser. You only need to do this once.

### With an SCMDB account

Go to Settings and paste the language file URL. The setting syncs across devices.

### How to remove

- **Without account**: Clear browser data, or visit `scmdb.dev?lang=clear`
- **With account**: Remove the URL from Settings

## Available Languages

Translation teams can be listed here once they publish their files:

| Language | Team | URL | Coverage |
|----------|------|-----|----------|
| *Your language here* | — | — | — |

If your team has published a translation, open an issue to get listed.

## Key Statistics (~3,200 keys per version)

| Category | Count | Notes |
|----------|-------|-------|
| Mission Titles | ~620 | Contract/mission names |
| Descriptions | ~640 | Mission briefing texts |
| Locations | ~630 | Planets, moons, stations |
| Ships | ~144 | Ship names |
| Items | ~1,030 | Weapons, armor, equipment |
| Factions | ~35 | In-game organizations |
| Reputation | ~55 | Rank and scope names |
| Mining | ~38 | Mineable elements |

## What is translated?

Translations cover **in-game data only** — mission titles, descriptions, location names, ship names, item names, faction names, and other strings sourced from Star Citizen's `global.ini`.

Website UI elements (buttons, labels, column headers, tooltips, filters, etc.) always remain in English. This is intentional — UI localization would require layout adjustments, pluralization rules, and formatting changes that go far beyond simple string replacement.

## FAQ

**Q: Do I need a Star Citizen account?**
A: No. You just need Python and a `global.ini` file (your translation team provides this).

**Q: Why are some keys missing from my translation?**
A: CIG adds new mission texts each patch. If your `global.ini` doesn't have them yet, English is used as fallback.

**Q: What are "Placeholder-Only" entries?**
A: Some CIG translations contain only `~mission()` tokens instead of actual text (e.g. `~mission(Contractor|Title)`). These are automatically replaced with English text.

**Q: Can I manually edit the output JSON?**
A: Yes. You can fix or improve any translation directly in the JSON file after generation.

**Q: How often does the template update?**
A: With every Star Citizen patch that changes mission data. Check this repo for new `lang-template-*.json` files.

## License

The translation tooling is provided as-is. Star Citizen game data belongs to Cloud Imperium Games.
