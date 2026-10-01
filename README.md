# Noto Color Emoji (Current) — Magisk module

Systemlessly replaces `/system/fonts/NotoColorEmoji.ttf` with the current
build straight from Google's
[googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji) repo —
the same stock art style Pixel ships, just not frozen at whatever Unicode
emoji version your ROM happened to launch with.

## Why this exists

Every other emoji Magisk module I could find either changes the art style
entirely (iOS, Blobmoji, Twemoji) or claims to be current and isn't — the
ones that stay in Google's own style are all stuck around Unicode 14.0
(2021-2022), apparently because nobody's bothered to automate the update.
So this one is: a scheduled job checks upstream daily and publishes a new
release the moment Google ships one, with no manual rebuild step.

## Install

1. Download the zip from the [Releases](../../releases) page.
2. Flash it in Magisk.
3. Reboot.

Updates are offered in Magisk directly, same as any other module.

## How the auto-update works

Google doesn't tag releases for noto-emoji's font builds (their last one is
from 2021) — instead they commit the actual built `.ttf` straight to the
`main` branch as it's updated. That file's own `name` table embeds the
exact source commit it was built from:

```
Version 2.057;GOOG;noto-emoji:20260911:fc4ca365e7c20e78278ae702aa20434bfe704c8f
```

`.github/workflows/sync.yml` runs daily on GitHub's own servers (your
computer doesn't need to be on). It re-fetches that file, reads the string
above, and compares it against `.upstream_version` — the value this repo
last shipped. If they differ, `scripts/sync.py` pulls in the new font,
rewrites `module.prop`/`update.json`/`CHANGELOG.md`, and the workflow
zips it, commits, tags, and publishes a GitHub release automatically.

No SELinux context override is needed here (unlike
[google-sans-flex-magisk](https://github.com/ethanm6/google-sans-flex-magisk)'s
`font_fallback.xml`) — `NotoColorEmoji.ttf` is a plain font file read like
any other under `/system/fonts/`, so Magisk's own default permissions are
enough and there's no `customize.sh` at all.

## Credit & licensing

The font itself is Google's [Noto Emoji](https://github.com/googlefonts/noto-emoji)
project, unmodified, under the SIL Open Font License 1.1 — see the
[`LICENSE`](LICENSE) index. The sync script and workflow are original,
GPL-3.0-or-later.

This project is not affiliated with or endorsed by Google.
