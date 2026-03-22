#!/usr/bin/env python3
"""
build_translation.py — SCMDB Community Translation Builder

Builds a translation JSON from an SCMDB Language Template
and a foreign-language Star Citizen global.ini.

Usage:
    python build_translation.py --template lang-template-4.7.0-ptu.11475995.json --ini german_global.ini --lang de

Output:
    lang-de-4.7.0-ptu.11475995.json

Requirements:
    - Python 3.10+ (stdlib only, no external dependencies)
    - lang-template-*.json (provided by SCMDB)
    - Foreign-language global.ini (community translation or CIG original)
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# ~mission() token normalization
# Replaces runtime placeholders with readable tags
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"~mission\(([^)]+)\)")
_TOKEN_DISPLAY_MAP = {
    "Location": "[LOCATION]", "Location|Address": "[LOCATION]",
    "location": "[LOCATION]", "Hint_Location": "[LOCATION]",
    "DefendLocationWrapperLocation": "[LOCATION]",
    "DefendLocationWrapperLocation|Address": "[LOCATION]",
    "Destination": "[DESTINATION]", "Destination|Address": "[DESTINATION]",
    "Destination|Address|ListAll": "[DESTINATIONS]",
    "destination|ListAll": "[DESTINATIONS]",
    "TargetName": "[TARGET]", "TargetName|First": "[TARGET]",
    "TargetName|Last": "[TARGET]", "AmbushTarget": "[TARGET]",
    "System": "[SYSTEM]", "Ship": "[SHIP]",
    "MissionMaxSCUSize": "[MAX_SCU]", "Hint_Tool": "[MULTITOOL]",
    "ApprovalCode": "[APPROVAL_CODE]", "RaceType": "[RACE_TYPE]",
    "Contractor|SignOff": "[SIGN_OFF]", "ClaimNumber": "[CLAIM]",
    "NearbyLocation": "[LOCATION]",
    "Contractor|DestroyProbeInformant": "[INFORMANT]",
    "Contractor|DestroyProbeAmount": "[MONITOR_COUNT]",
    "Contractor|DestroyProbeTimed": "", "Contractor|DestroyProbeDanger": "",
    "ReputationRank": "[RANK]",
    "CargoGradeToken": "[CARGO_GRADE]",
}


def normalize_runtime_tokens(text: str) -> str:
    """Replaces ~mission(...) tokens with readable [PLACEHOLDER] tags."""
    if not text:
        return text

    def replace(m):
        key = m.group(1)
        return _TOKEN_DISPLAY_MAP.get(key, f"[{key.split('|')[0].upper()}]")

    text = _TOKEN_RE.sub(replace, text)
    text = re.sub(r'~(\[[A-Z_]+\])', r'\1', text)
    return text


# ---------------------------------------------------------------------------
# Load global.ini
# ---------------------------------------------------------------------------

def load_ini(path: str) -> dict:
    """Loads a global.ini (key=value format).
    Tries multiple encodings (utf-8-sig, cp1252, utf-8)."""
    content = None
    for enc in ("utf-8-sig", "cp1252", "utf-8"):
        try:
            with open(path, encoding=enc, errors="strict") as f:
                content = f.readlines()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.readlines()

    loc = {}
    for line in content:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            while val.endswith("\\n"):
                val = val[:-2].rstrip()
            loc[key] = val
            # ,P suffix fallback (CIG plural/pending marker)
            for suffix in (",P", ",p"):
                if key.endswith(suffix):
                    bare_key = key[:-len(suffix)]
                    if bare_key not in loc:
                        loc[bare_key] = val

    return loc


def _lookup_ini(ini: dict, ini_lower: dict, key: str) -> str | None:
    """Look up a key in the INI dict with multiple fallbacks."""
    clean = key.lstrip("@")
    return (ini.get(clean) or ini.get(f"@{clean}")
            or ini_lower.get(clean.lower()) or ini_lower.get(f"@{clean}".lower()))


# ---------------------------------------------------------------------------
# Build translation
# ---------------------------------------------------------------------------

def build_translation(template: dict, ini: dict, lang_code: str) -> tuple:
    """Builds translation JSON from template + INI.
    Returns (output_dict, stats).

    Token substitution: the template may include tokenSubstitutions
    (e.g. ReputationRank -> @rank_master). After normalizing ~mission()
    tokens to placeholders like [RANK], these are replaced by looking up
    the loc-key in the foreign INI (e.g. [RANK] -> "Мастер")."""

    # Also keep lowercase keys for fallback
    ini_lower = {k.lower(): v for k, v in ini.items()}

    # Token substitutions from template (loc-key per token per key)
    token_subs = template.get("tokenSubstitutions", {})

    translated = {}
    missing = []
    noloc = []
    placeholder_only = 0
    substituted = 0
    mismatched = []
    bracket_re = re.compile(r"^\s*(\[[A-Z_]+\]\s*)+$")

    # rawKeys for mismatch detection
    raw_keys = template.get("rawKeys", {})

    for key, english_text in template.get("keys", {}).items():
        if key.startswith("_noloc_"):
            translated[key] = {"en": english_text, "tr": english_text}
            noloc.append(key)
            continue

        # Look up key in INI (with and without @, case-insensitive)
        val = _lookup_ini(ini, ini_lower, key)

        if val:
            while val.endswith("\\n"):
                val = val[:-2].rstrip()
            val = normalize_runtime_tokens(val)

            # Apply token substitutions: replace placeholders with
            # foreign language values (e.g. [RANK] -> "Мастер")
            subs = token_subs.get(key, {})
            if subs:
                for token_name, loc_key in subs.items():
                    placeholder = _TOKEN_DISPLAY_MAP.get(
                        token_name,
                        f"[{token_name.split('|')[0].upper()}]"
                    )
                    if not placeholder or placeholder not in val:
                        continue
                    foreign_value = _lookup_ini(ini, ini_lower, loc_key)
                    if foreign_value:
                        while foreign_value.endswith("\\n"):
                            foreign_value = foreign_value[:-2].rstrip()
                        val = val.replace(placeholder, foreign_value)
                        substituted += 1

            # Mismatch detection: foreign text still has token placeholders
            # that were resolved in the EN text
            raw_en = raw_keys.get(key)
            if raw_en and "~mission(" in raw_en:
                for token_placeholder in set(_TOKEN_DISPLAY_MAP.values()):
                    if (token_placeholder
                            and token_placeholder in val
                            and token_placeholder not in english_text):
                        mismatched.append(key)
                        break

            # Placeholder-only check (e.g. just "[CONTRACTOR]")
            if bracket_re.match(val):
                translated[key] = {"en": english_text, "tr": english_text}
                placeholder_only += 1
            else:
                translated[key] = {"en": english_text, "tr": val}
        else:
            translated[key] = {"en": english_text, "tr": english_text}
            missing.append(key)

    total = len(template.get("keys", {}))
    translated_count = total - len(missing) - len(noloc) - placeholder_only

    stats = {
        "total": total,
        "translated": translated_count,
        "missing": len(missing),
        "placeholderOnly": placeholder_only,
        "noLocKey": len(noloc),
        "mismatch": len(mismatched),
        "tokenSubstitutions": substituted,
        "missingKeys": sorted(missing),
        "mismatchKeys": sorted(mismatched),
    }

    output = {
        "version": template.get("version", "unknown"),
        "sourceLanguage": "en",
        "targetLanguage": lang_code,
        "keyCount": len(translated),
        "stats": {k: v for k, v in stats.items() if k != "missingKeys"},
        "keys": translated,
    }

    return output, stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SCMDB Community Translation Builder",
        epilog="Example: python build_translation.py --template lang-template-4.7.0-ptu.json --ini german_global.ini --lang de"
    )
    parser.add_argument("--template", required=True,
                        help="Path to lang-template-*.json (from SCMDB)")
    parser.add_argument("--ini", required=True,
                        help="Path to foreign-language global.ini")
    parser.add_argument("--lang", required=True,
                        help="Language code (e.g. de, fr, ja, ko, zh-cn)")
    args = parser.parse_args()

    # Load template
    if not os.path.exists(args.template):
        print(f"ERROR: Template not found: {args.template}")
        sys.exit(1)

    print(f"Loading template: {args.template}")
    with open(args.template, encoding="utf-8") as f:
        template = json.load(f)

    version = template.get("version", "unknown")
    key_count = template.get("keyCount", len(template.get("keys", {})))
    has_subs = bool(template.get("tokenSubstitutions"))
    print(f"  Version: {version}")
    print(f"  Keys: {key_count}")
    if has_subs:
        print(f"  Token substitutions: {len(template['tokenSubstitutions'])} keys")

    # Load INI
    if not os.path.exists(args.ini):
        print(f"ERROR: INI not found: {args.ini}")
        sys.exit(1)

    print(f"Loading INI: {args.ini}")
    ini = load_ini(args.ini)
    print(f"  {len(ini)} entries loaded")

    # Build translation
    print(f"\nBuilding translation ({args.lang})...")
    output, stats = build_translation(template, ini, args.lang)

    # Output
    out_name = f"lang-{args.lang}-{version}.json"
    out_path = os.path.join(os.path.dirname(args.template) or ".", out_name)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Report
    pct = stats["translated"] / stats["total"] * 100 if stats["total"] else 0
    print(f"\n{'=' * 50}")
    print(f"  File:             {out_name}")
    print(f"  Total Keys:       {stats['total']}")
    print(f"  Translated:       {stats['translated']} ({pct:.1f}%)")
    print(f"  Missing:          {stats['missing']} (fallback: English)")
    print(f"  Placeholder-Only: {stats['placeholderOnly']} (fallback: English)")
    print(f"  No Loc-Key:       {stats['noLocKey']} (kept as-is)")
    if stats.get("tokenSubstitutions"):
        print(f"  Substituted:      {stats['tokenSubstitutions']} (token placeholders resolved)")
    if stats.get("mismatch"):
        print(f"  Mismatches:       {stats['mismatch']} (unresolvable token placeholders)")
    print(f"{'=' * 50}")

    if stats["missing"] > 0:
        print(f"\nMissing Keys ({stats['missing']}):")
        for k in stats["missingKeys"][:30]:
            en_text = template["keys"].get(k, "")
            short = en_text[:60] + "..." if len(en_text) > 60 else en_text
            print(f"  {k}")
            try:
                print(f"    EN: {short}")
            except UnicodeEncodeError:
                print(f"    EN: {short.encode('ascii', 'replace').decode()}")
        if stats["missing"] > 30:
            print(f"  ... and {stats['missing'] - 30} more")
        print(f"\nThese keys are missing from the INI. English text is used as fallback.")

    if stats.get("mismatch", 0) > 0:
        print(f"\nToken Mismatches ({stats['mismatch']}):")
        print(f"These keys have token placeholders that could not be resolved.")
        for k in stats["mismatchKeys"][:20]:
            en_text = output["keys"].get(k, {}).get("en", "?")
            tr_text = output["keys"].get(k, {}).get("tr", "?")
            en_short = (en_text[:60] + "...") if len(en_text) > 63 else en_text
            tr_short = (tr_text[:60] + "...") if len(tr_text) > 63 else tr_text
            print(f"  {k}")
            for label, text in [("EN", en_short), ("TR", tr_short)]:
                try:
                    print(f"    {label}: {text}")
                except UnicodeEncodeError:
                    print(f"    {label}: {text.encode('ascii', 'replace').decode()}")
        if stats["mismatch"] > 20:
            print(f"  ... and {stats['mismatch'] - 20} more")

    print(f"\nDone! Host the file and share the link: scmdb.dev?lang=<FILE_URL>")


if __name__ == "__main__":
    main()
