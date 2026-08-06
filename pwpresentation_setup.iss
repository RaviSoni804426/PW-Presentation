; PW Presentation - Inno Setup installer script
; Build with:  ISCC.exe /DSourceDir="<path to the built app>" pwpresentation_setup.iss
;
; The repository had no installer script; the shipped installer was produced
; outside version control, so it could not be rebuilt when the application
; changed. This packages a deployed application directory.

#define AppName        "PW Presentation"
#define AppVersion     "1.0.0.1"
#define AppExeName     "PWPresentation.exe"
#ifndef SourceDir
  #define SourceDir    "C:\Program Files\PW\PWPresentation"
#endif
; Relative to this script, so it keeps working wherever the repo is checked out.
#define BrandingIcon   SourcePath + "branding\icons\PWPresentation.ico"

[Setup]
; Matches the AppId already written to the registry
; (HKLM\...\Uninstall\PW Presentation_is1), so this upgrades the existing
; install in place rather than landing beside it.
AppId=PW Presentation
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Physics Wallah
; The existing install lives under a nested PW\ folder; keep it so upgrades
; land on top of the current one instead of creating a second copy.
DefaultDirName={autopf}\PW\PWPresentation
DefaultGroupName={#AppName}
OutputDir={#SourcePath}installer-output
OutputBaseFilename=PW-PWPresentation-{#AppVersion}-x64
SetupIconFile={#BrandingIcon}
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
; The payload is ~1.1 GB and mostly already-compressed data (CEF, fonts), so
; ultra64 costs a great deal of time for very little size gain.
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=2
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
PrivilegesRequired=admin
DisableProgramGroupPage=yes
DisableDirPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "assoc_pptx"; Description: "Open .pptx files with {#AppName}"; GroupDescription: "File associations:"
Name: "assoc_ppt";  Description: "Open .ppt files with {#AppName}";  GroupDescription: "File associations:"
Name: "assoc_odp";  Description: "Open .odp files with {#AppName}";  GroupDescription: "File associations:"

[Files]
; Keep rollback copies of patched binaries out of the payload. Do NOT add a
; bare "*.bak" - ONLYOFFICE ships real product files with that extension
; (dictionaries/hyph_sl_SI.dic.bak), and excluding those silently drops
; product data. Only the suffixes our patch scripts create are listed.
;
; unins000.* is excluded because SourceDir defaults to a deployed install
; directory, and that directory contains the uninstaller from whichever install
; created it. Shipping it would put a stale uninstaller inside the payload,
; which then lands next to the real one Inno generates.
Source: "{#SourceDir}\*"; DestDir: "{app}"; Excludes: "*.bak-*,*.bak2,*.bak3,unins000.*"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";  Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";      Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; --- Application registration -------------------------------------------
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#AppExeName}"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName}"; Flags: uninsdeletekey

; --- ProgIDs -------------------------------------------------------------
; Presentation formats only. PW Presentation is a presentation-only application.
Root: HKCR; Subkey: "PWPresentation.pptx"; ValueType: string; ValueName: ""; ValueData: "PowerPoint Presentation"; Flags: uninsdeletekey; Tasks: assoc_pptx
Root: HKCR; Subkey: "PWPresentation.pptx\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: assoc_pptx
Root: HKCR; Subkey: "PWPresentation.pptx\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: assoc_pptx
Root: HKCR; Subkey: ".pptx"; ValueType: string; ValueName: ""; ValueData: "PWPresentation.pptx"; Flags: uninsdeletevalue; Tasks: assoc_pptx

Root: HKCR; Subkey: "PWPresentation.ppt"; ValueType: string; ValueName: ""; ValueData: "PowerPoint 97-2003 Presentation"; Flags: uninsdeletekey; Tasks: assoc_ppt
Root: HKCR; Subkey: "PWPresentation.ppt\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: assoc_ppt
Root: HKCR; Subkey: "PWPresentation.ppt\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: assoc_ppt
Root: HKCR; Subkey: ".ppt"; ValueType: string; ValueName: ""; ValueData: "PWPresentation.ppt"; Flags: uninsdeletevalue; Tasks: assoc_ppt

Root: HKCR; Subkey: "PWPresentation.odp"; ValueType: string; ValueName: ""; ValueData: "OpenDocument Presentation"; Flags: uninsdeletekey; Tasks: assoc_odp
Root: HKCR; Subkey: "PWPresentation.odp\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#AppExeName},0"; Tasks: assoc_odp
Root: HKCR; Subkey: "PWPresentation.odp\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Tasks: assoc_odp
Root: HKCR; Subkey: ".odp"; ValueType: string; ValueName: ""; ValueData: "PWPresentation.odp"; Flags: uninsdeletevalue; Tasks: assoc_odp

; --- "Open with" entries (always registered, even without taking over the
;     default) so the formats show up in Explorer's Open-with list. --------
Root: HKCR; Subkey: "Applications\{#AppExeName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: ".pptx\OpenWithProgids"; ValueType: string; ValueName: "PWPresentation.pptx"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".ppt\OpenWithProgids";  ValueType: string; ValueName: "PWPresentation.ppt";  ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".odp\OpenWithProgids";  ValueType: string; ValueName: "PWPresentation.odp";  ValueData: ""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: postinstall nowait skipifsilent
