# PW Presentation

A standalone presentation editor for Windows, built from a fork of
[ONLYOFFICE Desktop Editors](https://github.com/ONLYOFFICE/DesktopEditors)
with the document, spreadsheet, PDF and Visio editors removed.

## Features

- Create and edit presentations (`.pptx`, `.ppt`, `.odp`)
- Slide layouts and slide masters
- Transitions (fade, wipe, push, split, and more)
- Animations (appear, fly in, zoom, spin, and more)
- Insert images, shapes, tables and charts
- Speaker notes
- Slideshow mode
- PDF export
- Reads and writes Microsoft PowerPoint files

## File associations

`.pptx` `.ppt` `.odp` `.ppsx` `.pps` `.potx`

## System requirements

- Windows 10 or 11 (64-bit)
- 4 GB RAM
- 1 GB disk space

---

## Repository layout

This is a monorepo. Each top-level directory is a fork of the corresponding
ONLYOFFICE repository, pinned to the commits recorded in [UPSTREAM.md](UPSTREAM.md).

| Directory | Role |
|---|---|
| `sdkjs/` | editor engine (JavaScript) |
| `web-apps/` | editor UI |
| `desktop-apps/` | Qt desktop shell, installer scripts |
| `desktop-sdk/` | CEF wrapper |
| `core/` | C++ engine, x2t converter, fonts, rendering |
| `build_tools/` | build system |
| `dictionaries/`, `document-templates/` | data |
| `branding/` | PW Presentation icons |

[ANALYSIS.md](ANALYSIS.md) documents the dependency map that shaped the fork —
in particular **why `sdkjs/word/` and `sdkjs/cell/` are still present**: the
presentation editor's build config requires 197 files from `word/` and 10 from
`cell/`, because slide text bodies are Word document-content objects and chart
data is a spreadsheet model. The product is made presentation-only at the
*bundle* level (`build.py --product slide`) rather than by deleting shared
sources.

## Building

### Prerequisites

- Visual Studio with the C++ workload
- Qt (the build auto-detects the kit under `--qt-dir`)
- Node.js, Python 3, Java
- Inno Setup 6+ (for the installer)

### JavaScript / UI only

Fast, and sufficient to verify every presentation-only change:

```bash
cd sdkjs/build && python build.py --product slide --desktop
```

```bash
cd web-apps/build && npm install && npx grunt
```

```bash
cd desktop-apps/common/loginpage/build && npm install && npx grunt
```

### Full desktop build

```bash
cd build_tools && python configure.py --update 0 --platform win_64 --module desktop --qt-dir "C:/Qt/<version>"
```

```bash
cd build_tools && python make.py
```

Note that `make.py` builds the entire third-party stack from source, including
V8 via Chromium's `depot_tools`. Budget several hours and tens of gigabytes of
free disk.

## Differences from upstream ONLYOFFICE

- Only the presentation editor is built and shipped
- Start screen, jump list and file dialogs offer presentations only
- Separate registry keys, data directory, mutex and window class, so
  PW Presentation and ONLYOFFICE can be installed side by side
- The auto-update module is **disabled**. Upstream points it at ONLYOFFICE's
  appcast, which would otherwise update a PW Presentation install into
  ONLYOFFICE Desktop Editors. Releases are published on GitHub instead.

## Licence

PW Presentation is a derivative work of ONLYOFFICE Desktop Editors and is
distributed under the **GNU AGPL v3**, the same licence as the upstream
project. Upstream copyright is retained:
© Ascensio System SIA. Non-code assets carry their original CC BY-SA 4.0 terms.

<https://github.com/RaviSoni804426/PW-Presentation>
