# Upstream sources

All sources below were cloned shallow (`--depth 1`) from the ONLYOFFICE
organisation and are tracked here as a monorepo. Each repo's original `.git`
directory was renamed to `.git-upstream` (gitignored) so the working tree can
live in this repository while remaining diffable against upstream.

To restore upstream tracking for a repo:  `mv <repo>/.git-upstream <repo>/.git`

| Repo | Upstream | Commit | Date |
|------|----------|--------|------|
| `build_tools` | https://github.com/ONLYOFFICE/build_tools | `a9f9895b17` | 2026-05-19 |
| `core` | https://github.com/ONLYOFFICE/core | `3250a848ee` | 2026-05-19 |
| `desktop-apps` | https://github.com/ONLYOFFICE/desktop-apps | `8f452c7f70` | 2026-05-19 |
| `desktop-sdk` | https://github.com/ONLYOFFICE/desktop-sdk | `2f16486ade` | 2026-05-19 |
| `dictionaries` | https://github.com/ONLYOFFICE/dictionaries | `d3223bbb77` | 2025-05-26 |
| `document-templates` | https://github.com/ONLYOFFICE/document-templates | `71430c9f18` | 2026-04-28 |
| `sdkjs` | https://github.com/ONLYOFFICE/sdkjs | `72b0421c0b` | 2026-05-19 |
| `web-apps` | https://github.com/ONLYOFFICE/web-apps | `9c0ca538c3` | 2026-05-19 |

Base release: **ONLYOFFICE v9.4.0** (6 build-critical repos merged from `release/v9.4.0` on 2026-05-19).

