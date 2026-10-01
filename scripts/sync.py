#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Checks whether googlefonts/noto-emoji's main-branch build of NotoColorEmoji.ttf
has moved on since we last packaged it, and if so, pulls it in and updates
every file that needs to change to ship a new release.

Why this works without watching GitHub Releases or tags: Google doesn't cut
those for noto-emoji's font builds (their last tagged release is from 2021).
Instead they commit the actual built .ttf straight to main as it's updated,
and the font's own `name` table (ID 5, version string) embeds the exact
source commit it was built from, e.g.:

    Version 2.057;GOOG;noto-emoji:20260911:fc4ca365e7c20e78278ae702aa20434bfe704c8f
             ^-----^     ^------^ ^------^ ^--------------------------------------^
             font ver    marker   build    the noto-emoji commit this came from
                                  date

That string is a reliable, free version oracle: re-fetch the font, read the
string, compare against what we shipped last time. No GitHub API calls, no
rate limits, no auth needed for the check itself.

Usage: python3 scripts/sync.py
Exits 0 either way; signals whether anything changed via GITHUB_OUTPUT (when
running in Actions) and via stdout (when run locally).
"""
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

from fontTools.ttLib import TTFont

UPSTREAM_FONT_URL = (
    "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/2D/fonts/NotoColorEmoji.ttf"
)
REPO_ROOT = Path(__file__).resolve().parent.parent
FONT_DEST = REPO_ROOT / "system" / "fonts" / "NotoColorEmoji.ttf"
VERSION_FILE = REPO_ROOT / ".upstream_version"
MODULE_PROP = REPO_ROOT / "module.prop"
UPDATE_JSON = REPO_ROOT / "update.json"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
REPO_SLUG = "ethanm6/noto-emoji-magisk"

# "Version 2.057;GOOG;noto-emoji:20260911:fc4ca365e7c20e78278ae702aa20434bfe704c8f"
VERSION_RE = re.compile(
    r"Version (?P<ver>[\d.]+);GOOG;noto-emoji:(?P<date>\d{8}):(?P<sha>[0-9a-f]+)"
)


def fetch_font(tmp_path: Path) -> None:
    req = urllib.request.Request(UPSTREAM_FONT_URL, headers={"User-Agent": "noto-emoji-magisk-sync"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp_path, "wb") as f:
        f.write(resp.read())


def read_version_string(font_path: Path) -> str:
    font = TTFont(str(font_path), lazy=True)
    name = font["name"]
    rec = name.getDebugName(5)  # nameID 5 = version string
    if not rec:
        raise RuntimeError("Font has no nameID 5 (version string) — upstream format may have changed")
    return rec


def write_github_output(key: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a") as f:
        # value is a single line (our version strings never contain newlines)
        f.write(f"{key}={value}\n")


def main() -> int:
    tmp_font = REPO_ROOT / "_upstream_fetch.ttf"
    fetch_font(tmp_font)

    new_version_string = read_version_string(tmp_font)
    old_version_string = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""

    if new_version_string == old_version_string:
        tmp_font.unlink(missing_ok=True)
        print(f"No change. Still at: {new_version_string}")
        write_github_output("changed", "false")
        return 0

    m = VERSION_RE.search(new_version_string)
    if not m:
        tmp_font.unlink(missing_ok=True)
        raise RuntimeError(f"Couldn't parse version string: {new_version_string!r}")

    ver, build_date, sha = m["ver"], m["date"], m["sha"]
    tag = f"v{ver}-{build_date}"
    version_code = int(build_date)  # YYYYMMDD — always increases day over day

    # 1. install the new font
    tmp_font.replace(FONT_DEST)

    # 2. record what we shipped, so next run's comparison is against this
    VERSION_FILE.write_text(new_version_string + "\n")

    # 3. module.prop — rewrite the version/versionCode lines in place
    prop_text = MODULE_PROP.read_text()
    prop_text = re.sub(r"^version=.*$", f"version={tag}", prop_text, flags=re.M)
    prop_text = re.sub(r"^versionCode=.*$", f"versionCode={version_code}", prop_text, flags=re.M)
    MODULE_PROP.write_text(prop_text)

    # 4. update.json
    zip_name = f"NotoColorEmoji_{tag}.zip"
    UPDATE_JSON.write_text(
        "{\n"
        f'  "version": "{tag}",\n'
        f'  "versionCode": {version_code},\n'
        f'  "zipUrl": "https://github.com/{REPO_SLUG}/releases/download/{tag}/{zip_name}",\n'
        f'  "changelog": "https://raw.githubusercontent.com/{REPO_SLUG}/main/CHANGELOG.md"\n'
        "}\n"
    )

    # 5. changelog entry
    today = date.today().isoformat()
    entry = (
        f"## {tag} ({today})\n\n"
        f"- Synced to upstream noto-emoji build {ver}, built {build_date[:4]}-{build_date[4:6]}-{build_date[6:]} "
        f"(commit [`{sha[:12]}`](https://github.com/googlefonts/noto-emoji/commit/{sha})).\n"
        f"- No changes outside the font itself.\n\n"
    )
    existing = CHANGELOG.read_text() if CHANGELOG.exists() else "# Changelog\n\n"
    marker = "# Changelog\n"
    idx = existing.index(marker) + len(marker)
    CHANGELOG.write_text(existing[:idx] + "\n" + entry + existing[idx:].lstrip("\n"))

    print(f"Updated: {old_version_string or '(none)'} -> {new_version_string}")
    write_github_output("changed", "true")
    write_github_output("tag", tag)
    write_github_output("zip_name", zip_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
