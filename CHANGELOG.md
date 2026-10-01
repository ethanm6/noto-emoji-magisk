# Changelog

## v2.057-20260911 (2026-10-01)

- Initial release. Synced to upstream noto-emoji build 2.057, built
  2026-09-11 (commit
  [`fc4ca365e7c2`](https://github.com/googlefonts/noto-emoji/commit/fc4ca365e7c20e78278ae702aa20434bfe704c8f)).
- From here on, `.github/workflows/sync.yml` checks upstream daily and
  cuts a new release automatically whenever Google updates the font —
  see `scripts/sync.py` for how the version is detected.
