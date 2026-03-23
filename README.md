# SCMDB Community Translations

Community-maintained translations for [SCMDB](https://scmdb.dev) — the Star Citizen Mission & Data Browser.

SCMDB displays all data in English by default. This repo provides the tools for community translation teams to create their own language files that users can load in the browser.

## For Translation Teams

### What you need

1. **Python 3.10+** (no external dependencies)
2. **`build_lang_template.py`** (this repo)
3. **`lang-template-*.json`** (this repo, updated each patch by SCMDB)
4. **Your community `global.ini`** (the Star Citizen translation file your team maintains)

### How to build a translation

```bash
# PTU (default)
python build_lang_template.py --translate path/to/your_global.ini

# LIVE (when a live template is available)
python build_lang_template.py -p live --translate path/to/your_global.ini
```

The `-p` flag selects which template to use when multiple are present (e.g. `lang-template-*-ptu.*.json` vs `lang-template-*-live.*.json`). Default is `ptu`.

This produces a `lang-your_global-4.7.0-ptu.11494258.json` file with a coverage report:

```
=== Result ===
  File:          lang-your_global-4.7.0-ptu.11494258.json
  Total:         3340
  Translated:    3250
  Missing:       3
  Mismatch:      26 (token placeholders in foreign text)
  Substituted:   165 (placeholders replaced with foreign values)
  No loc key:    80 (kept as-is)
```

Missing keys automatically fall back to English text.

#### Token substitution

The tool automatically resolves token placeholders in translated text. For example, if a mission title contains `[RANK]`, the tool looks up the translated rank name (e.g. "Master" -> "Мастер") in your `global.ini` and inserts it. This reduces manual post-processing significantly.

#### Output filename

The output filename is derived from your `global.ini` filename. To control the language code in the output, name your INI file accordingly:

```bash
# Input: global_ru.ini -> Output: lang-global_ru-4.7.0-ptu.11494258.json
# Input: german_global.ini -> Output: lang-german_global-4.7.0-ptu.11494258.json
```

### How to publish your translation

1. Host the generated `lang-*.json` file somewhere publicly accessible:
   - **GitHub** (recommended): Push to your own repo, use the Raw URL
   - **Any web server** with CORS enabled (`Access-Control-Allow-Origin: *`)
   - **GitHub Gist**: Upload and use the Raw URL

2. Share the direct URL with your community:
   ```
   https://raw.githubusercontent.com/your-team/scmdb-translations/main/lang-de-4.7.0-ptu.11494258.json
   ```

3. When a new patch drops:
   - Pull the updated `lang-template-*.json` and `build_lang_template.py` from this repo
   - Re-run `python build_lang_template.py --translate path/to/your_global.ini`
   - Update your hosted file

### File format

The output JSON contains English + translated text for each key:

```json
{
  "version": "4.7.0-ptu.11494258",
  "sourceLanguage": "en",
  "targetLanguage": "global_ru",
  "keyCount": 3340,
  "keys": {
    "Adagio_BasicSalvage_Title_01": {
      "en": "Claim #[CLAIM]: [SHIP] Salvage Rights",
      "tr": "ПРАВО НА УТИЛИЗАЦИЮ #[CLAIM]: [SHIP]"
    },
    "items_commodities_gold_ore": {
      "en": "Gold (Ore)",
      "tr": "Золото (Руда)"
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

## Key Statistics (~3,300 keys per version)

| Category | Count | Notes |
|----------|-------|-------|
| Mission Titles | ~685 | Contract/mission names |
| Descriptions | ~724 | Mission briefing texts |
| Locations | ~626 | Planets, moons, stations |
| Ships | ~144 | Ship names |
| Items | ~1,033 | Weapons, armor, equipment |
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

**Q: What are "Mismatch" entries?**
A: CIG sometimes has different English text in foreign language `global.ini` files compared to the English version. These mismatches are reported but the translated text is still included.

**Q: What are "Substituted" entries?**
A: Mission tokens like `[RANK]` or `[CARGO_GRADE]` are automatically replaced with the translated value from your `global.ini`. For example, `[RANK]` becomes "Мастер" in Russian.

**Q: Can I manually edit the output JSON?**
A: Yes. You can fix or improve any translation directly in the JSON file after generation.

**Q: How often does the template update?**
A: With every Star Citizen patch that changes mission data. Check this repo for new `lang-template-*.json` files.

## License

The translation tooling is provided as-is. Star Citizen game data belongs to Cloud Imperium Games.
