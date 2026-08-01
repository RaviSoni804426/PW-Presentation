# Phase 2 — Codebase analysis & dependency map

Base: ONLYOFFICE v9.4.0 (see [UPSTREAM.md](UPSTREAM.md)).

---

## 1. The headline finding

**`sdkjs/word/` and `sdkjs/cell/` cannot be deleted.**

`sdkjs/configs/slide.json` is the authoritative file list the presentation
editor is built from. It pulls in:

| Source folder | Files required by the presentation editor |
|---|---:|
| `word/`   | **197** |
| `common/` | 132 |
| `slide/`  | 34 |
| `cell/`   | **10** |
| `vendor/` | 10 |
| **total** | **383** |

The presentation editor reuses Word's entire text engine — `Paragraph.js`,
`Run.js`, `DocumentContent.js`, `Table.js`, the Math module, numbering,
spell-checking, structured document tags — because every text box, table and
placeholder on a slide *is* a Word document-content object. It reuses Cell's
`Workbook`/`parserFormula` because embedded chart data is a spreadsheet.

The 10 `cell/` files required:

```
cell/utils/utils.js                        cell/model/Serialize.js
cell/model/SheetMemory.js                  cell/model/CellInfo.js
cell/model/FormulaObjects/parserFormula.js cell/model/HeaderFooter.js
cell/model/WorkbookElems.js                cell/view/DrawingObjectsController.js
cell/model/Workbook.js                     cell/view/HandlerList.js
```

### What is actually deletable in `sdkjs/`

| Folder | On disk | Needed by slide | Deletable |
|---|---:|---:|---:|
| `word/`   | 232 files (13.2 MB) | 197 | 35 files (2.1 MB) |
| `cell/`   | 62 files (10.1 MB)  | 10  | 52 files (7.2 MB) |
| `common/` | 174 files (25.1 MB) | 132 | 42 files (13.0 MB) |
| `slide/`  | 37 files (5.7 MB)   | 34  | 3 files (2.1 MB) |
| `pdf/`    | 67 files (20.6 MB)  | 0   | 67 files (20.6 MB) |
| `visio/`  | 12 files (0.7 MB)   | 0   | 12 files (0.7 MB) |

Deleting shared source to save ~40 MB is a poor trade against the risk of
breaking the editor. **The strip happens at the bundle level instead** — see §3.

---

## 2. Where the size actually is

`web-apps/apps/` — the per-editor UIs, which are genuinely independent:

| App | Size | Files | Verdict |
|---|---:|---:|---|
| `spreadsheeteditor`  | 444.9 MB | 14003 | delete |
| `documenteditor`     |  95.1 MB |  5416 | delete |
| `pdfeditor`          |  34.6 MB |  1317 | delete |
| `visioeditor`        |   6.1 MB |   350 | delete |
| **presentationeditor** | 66.8 MB | 4925 | **keep** |
| `common` (shared)    |   9.4 MB |  4653 | keep |
| `api` (shared)       |   0.1 MB |    10 | keep |

Removing the four non-presentation UIs reclaims **580.7 MB** with no impact on
the presentation editor.

---

## 3. The build system already supports presentation-only

`sdkjs/build/build.py` takes `--product`:

```
python build.py --product slide --desktop
```

This emits only `deploy/sdkjs/slide/sdk-all{,-min}.js`. The word/cell/visio
bundles are never produced, so shipping their shared *sources* costs nothing in
the installed product.

Two constraints found in `build.py`:

- Line 269 requires **all five** config files (`externs`, `word`, `cell`,
  `slide`, `visio`) to be present even when building one product — so
  `sdkjs/configs/*.json` must not be deleted.
- `OTHER_FILES` unconditionally copies `cell/css/*.css` and
  `pdf/src/engine/*` into deploy — so those two paths must survive, or
  `build.py` must be patched alongside their removal.

`build_tools/configure.py` takes `--module 'desktop'` to build only the desktop
app, skipping the server and builder modules.

---

## 4. Branding hooks (no source-wide find/replace needed)

ONLYOFFICE exposes first-class rebranding points. A blanket
`ONLYOFFICE` → `PW Presentation` replace across `.py`/`.cpp`/`.h` would rewrite
clone URLs, registry keys and namespaces and break the build; these hooks
achieve the same result safely.

| Hook | Where | Controls |
|---|---|---|
| `APP_COPYRIGHT`, `PUBLISHER_URL`, `COMPANY_NAME`, `PRODUCT_VERSION` | env vars read by `sdkjs/build/build.py` | JS bundle license header, `AscCommon.g_cCompanyName` |
| `--branding-name`, `--branding-url`, `--branding` | `build_tools/configure.py` | output paths, server/JS branding dir |
| `APP_NAME`, `APP_TITLE`, `WINDOW_NAME`, `REG_APP_NAME`, `APP_DATA_PATH`, `FILE_PREFIX`, `URL_SITE` | `desktop-apps/win-linux/src/defines.h` | window title, registry location, user-data dir |
| `VERSION`/`ProductName` block | `desktop-apps/win-linux/*.rc` | Explorer file properties |

---

## 5. Files that gate the product surface

Everything that makes the app *offer* Word/Spreadsheet/PDF lives in four places:

| What | File | Detail |
|---|---|---|
| Start-screen "create new" tiles | `desktop-apps/common/loginpage/src/panelrecent.js` **:688–737** | array of 4 tiles: `word` (DOCX), `cell` (XLSX), `slide` (PPTX), `form` (PDF). Keep `slide` only. |
| Tile → editor routing | `desktop-apps/common/loginpage/src/panels.js` **:305–306** | `new:xlsx → cell`, `new:pptx → slide` |
| Open/Save dialog filters | `desktop-apps/win-linux/src/components/cfiledialog.cpp` **:73–97, 265–270, 366–395** | per-format filter map + grouped "Text documents / Spreadsheets / Presentations" filters |
| Windows file associations | `desktop-apps/win-linux/src/platform_win/association.cpp` | which extensions the app registers |

The tile for `slide` already uses orange (`#F4893A` → `#DE7341`), which matches
the intended PW Presentation icon colour.

---

## 6. Toolchain status on this machine

| Requirement | Status |
|---|---|
| Visual Studio 2026 Community + C++ (`18.8.12021.73`) | present |
| Qt 6.11.1 `msvc2022_64` (`base.py` needs ≥ 6.6) | present |
| Node.js, Java 23, CMake, Perl, NASM | present |
| 7-Zip, curl, vswhere | vendored in `build_tools/tools/win/` |
| Inno Setup 6 | **missing** — needed for Phase 6 |
| Free space on `D:` | **32.4 GB** — likely short for a full desktop build |

---

## 7. Revised Phase 3 plan

1. Delete `web-apps/apps/{documenteditor,spreadsheeteditor,pdfeditor,visioeditor}` — 580 MB, zero risk.
2. Keep all of `sdkjs/` source; build with `--product slide` so only the
   presentation bundle ships.
3. Trim the start-screen tile array to `slide` only.
4. Restrict file-dialog filters to presentation formats.
5. Register only presentation extensions.

No stubbing or mocking is required, because nothing is being deleted out from
under the slide editor.
