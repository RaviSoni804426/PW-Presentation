# Build status

## What builds today

The entire JavaScript/UI layer builds and has been verified presentation-only.

```bash
cd build_tools
OO_ONLY_BUILD_JS=1 PRODUCT_VERSION=1.0.0 BUILD_NUMBER=1 \
COMPANY_NAME=pwpresentation \
APP_COPYRIGHT="PW Presentation. Based on ONLYOFFICE (c) Ascensio System SIA. Licensed under GNU AGPL v3." \
PUBLISHER_URL="https://github.com/RaviSoni804426/PW-Presentation" \
python make.py
```

Output: `build_tools/out/js/onlyoffice/desktop/` — 218 MB.

Verified in that output:

| Check | Result |
|---|---|
| sdkjs bundles shipped | `slide/sdk-all.js` (29 MB) and `slide/sdk-all-min.js` only — no word, cell or visio bundle |
| Editor UIs shipped | `presentationeditor`, plus shared `common` and `api` |
| Start-screen creation tiles | PPTX only; no DOCX, XLSX or PDF tile |
| Word text engine present in slide bundle | yes — 2178 references, confirming it cannot be deleted |
| Cell workbook model present in slide bundle | yes — 233 references |

## What does not build yet: the C++ layer

The native side (`core`, `desktop-sdk`, the Qt shell) has not been built. The
blocker is the toolchain, not the PW Presentation changes.

### Requirement: Visual Studio 2019

ONLYOFFICE v9.4's `build_tools` only ever sets `vs-version` to `2015` or
`2019` (`scripts/config.py`), and every third-party module keys off that value:

| Module | Pinned to |
|---|---|
| `boost.py` | boost 1.72 with toolset `msvc-14.2`, bootstrap `vc142` |
| `icu.py` | MSBuild `PlatformToolset=v142` |
| `heif.py` | CMake generator `Visual Studio 16 2019` |
| `v8_89.py` | `GYP_MSVS_VERSION` = `vs-version`; V8 8.9 dates from early 2021 and predates VS2022 entirely |

This repository carries patches that make the first three adapt to whichever
MSVC toolset is actually installed (see the Phase 5 commits). **V8 remains
pinned**: it is fetched with Chromium's `depot_tools` and built with GN/ninja,
and its own build scripts decide which Visual Studio to use.

The practical fix is to install **Visual Studio 2019 Build Tools**, or add the
**MSVC v142** individual component to a newer Visual Studio — with v142 present
the patched `config.py` finds and pins it automatically, and every module above
falls back into its validated configuration.

On the machine this was developed on, adding v142 non-interactively failed:
`setup.exe modify --quiet` exits 5007 ("commands with --quiet should be run
elevated from the beginning"), and the self-elevating bootstrapper left the
component uninstalled. Adding it through the Visual Studio Installer UI is the
reliable route.

### Also budget for

- **Disk**: V8's `fetch` + `gclient sync` alone pulls a Chromium-sized
  checkout; CEF adds a further download. Tens of gigabytes, well beyond the
  ~31 GB free on `D:` when this was written. `core/build` and `build_tools/out`
  are already junctioned to `C:\pwbuild` here.
- **Time**: several hours for the third-party stack before the ONLYOFFICE
  solution itself starts compiling.

### Bugs fixed along the way

`base._call_vcvarsall_and_return_env()` split `subprocess` output as `str`
while `Popen` returned `bytes`, so it raised `TypeError` on Python 3 and never
produced a usable MSVC environment. Fixed in this fork.

## Remaining phases

Phases 6–8 (installer, functional testing, release) all consume the built
`PWPresentation.exe` and are blocked behind the C++ build. Everything that can
be prepared ahead of it already is:

- Inno Setup 7 installed
- `desktop-apps/package/inno/defines.iss` rebranded
- Icons generated for the app and for `.pptx` / `.ppt` / `.pps` / `.ppsx` /
  `.odp` / `.potx`
