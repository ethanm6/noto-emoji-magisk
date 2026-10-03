![Noto](https://substackcdn.com/image/fetch/w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fbucketeer-e05bbc84-baa3-437e-9518-adb32be77984.s3.amazonaws.com%2Fpublic%2Fimages%2Fab4b4276-9bb0-42a6-a675-510fcb6055df_1940x1088.png)

# Noto Color Emoji (Current) — Magisk module

Systemlessly replaces `/system/fonts/NotoColorEmoji.ttf` with the current
build straight from Google's
[googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji) — same
stock art style Pixel ships, just not frozen at whatever Unicode emoji
version your ROM launched with.

A scheduled GitHub Action checks upstream daily and publishes a new release
automatically whenever Google updates the font — see
[`scripts/sync.py`](scripts/sync.py) for how. No action needed on your end.

## Install

1. Download the zip from the [Releases](../../releases) page.
2. Flash it in Magisk.
3. Reboot.

Updates are offered in Magisk directly, same as any other module.

## Credit & licensing

The font itself is Google's [Noto Emoji](https://github.com/googlefonts/noto-emoji)
project, unmodified, under the SIL Open Font License 1.1 — see the
[`LICENSE`](LICENSE) index. The sync script and workflow are original,
GPL-3.0-or-later.

This project is not affiliated with or endorsed by Google.

## Support

If you find this project useful, you can support development:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/ethanm6)
