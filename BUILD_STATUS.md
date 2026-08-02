# Build status

## JavaScript / UI layer — built and verified

```bash
cd build_tools
OO_ONLY_BUILD_JS=1 PRODUCT_VERSION=1.0.0 BUILD_NUMBER=1 \
COMPANY_NAME=pwpresentation \
APP_COPYRIGHT="PW Presentation. Based on ONLYOFFICE (c) Ascensio System SIA. Licensed under GNU AGPL v3." \
PUBLISHER_URL="https://github.com/RaviSoni804426/PW-Presentation" \
python make.py
```

Output: `build_tools/out/js/onlyoffice/desktop/` — 218 MB.

| Check | Result |
|---|---|
| sdkjs bundles shipped | `slide/` only — no word, cell or visio bundle |
| Editor UIs shipped | `presentationeditor` + shared `common`/`api` |
| Start-screen creation tiles | PPTX only |
| Page title | "PW Presentation" (was "Hello ONLYOFFICE Documents") |
| Word text engine in slide bundle | 2178 refs — confirms `sdkjs/word` cannot be deleted |

## C++ layer — building

Toolchain that finally worked, and what stood in the way:

| Component | State |
|---|---|
| **VS 2019 Build Tools** at `C:\BuildTools2019` (v142 / 14.29.30133) | installed via `vs_BuildTools.exe --quiet --installPath C:\BuildTools2019` |
| `config.py` toolset resolution | discovers installs via vswhere, prefers v142, maps compiler version → platform toolset (`14.29`→`v142`); pins vcvarsall with `-vcvars_ver` |
| `base._call_vcvarsall_and_return_env` | fixed: split bytes as str on Python 3, never worked |
| `NoDefaultCurrentDirectoryInExePath=1` in harness env | cleared by the build wrapper; cmd.exe otherwise refuses `bootstrap.bat` etc. from the CWD |
| boost 1.72 | **builds** — vc142 static libs; runs inside an explicit vcvarsall env because its own VS probe misses non-standard install paths |
| CEF 5414 | prebuilt download, extracted |
| ICU | building under MSBuild `PlatformToolset=v142` |
| openssl, v8, core, Qt apps | pending; v8 gets `vs2019_install`/`GYP_MSVS_OVERRIDE_PATH` pointed at the resolved VS |
| Windows SDK | 10.0.19041 + 10.0.26100, Debuggers present (v8 requirement) |

Disk: `core/build`, `build_tools/out`, `3dParty/v8_89`, `3dParty/cef` are
junctioned into `C:\pwbuild` (D: lacks the headroom for a Chromium checkout).

## Packaging layout (Phase 6, ready)

Two executables ship, mirroring upstream:

- `PWPresentation.exe` — the projicons launcher: Explorer icons, jump list;
  starts `./editors.exe` by literal name
- `editors.exe` — the Qt app (qmake TARGET `PWPresentation`, renamed at deploy)

`deploy_desktop.py` produces `build_tools/out/win_64/onlyoffice/DesktopEditors/`;
`desktop-apps/package/make_inno.ps1 -CompanyName PW -ProductName PWPresentation`
drives Inno Setup (installed: Inno Setup 7, `C:\Program Files\Inno Setup 7`).
The installer associates only ppt/pptx/pps/ppsx/odp/pot/potx/pptm, registers a
single ShellNew entry and start-menu jump entry, and no update service.
