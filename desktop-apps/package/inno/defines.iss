; -- PW Presentation Defines --
; Derived from ONLYOFFICE Desktop Editors (GNU AGPL v3).
; Identity values are deliberately distinct from ONLYOFFICE's so both products
; can be installed side by side.

#define sCompanyName                    "PW"
#define sIntCompanyName                 sCompanyName
#define sProductName                    "Presentation"
#define sIntProductName                 "PWPresentation"
#define sAppName                        str(sCompanyName + " " + sProductName)
#define sPackageName                    str(sIntCompanyName + "-" + sIntProductName)
#define sAppPublisher                   "PW Presentation"
#define sAppPublisherURL                "https://github.com/RaviSoni804426/PW-Presentation"
#define sAppSupportURL                  "https://github.com/RaviSoni804426/PW-Presentation/issues"
#define sAppCopyright                   str("Based on ONLYOFFICE (c) Ascensio System SIA " + GetDateTimeString("yyyy",,) + ". Licensed under GNU AGPL v3.")
#define sAppIconName                    "PW Presentation"
#define sOldAppIconName                 "PW Presentation"
#define sAppProtocol                    'pw-presentation'

#define APP_PATH                        str(sIntCompanyName + "\" + sIntProductName)
#define UPD_PATH                        str(sIntProductName + "Updates")
#define APP_REG_PATH                    str("Software\" + APP_PATH)
#define APP_REG_UNINST_KEY              str(sCompanyName + " " + sProductName)
#define APP_USER_MODEL_ID               "PW.Presentation.1"
#define APP_MUTEX_NAME                  "PWPRESENTATION"
#define APPWND_CLASS_NAME               "PWPresentationWindowClass"

; Two executables ship: iconsExe is the user-facing launcher (projicons build,
; carries the icons and jump list) and NAME_EXE_OUT is the real Qt app it
; starts -- projicons launches "./editors.exe" by that literal name.
#define iconsExe                        "PWPresentation.exe"
#define NAME_EXE_OUT                    "editors.exe"

#define ASSC_APP_NAME                   "PW Presentation"
#define ASCC_REG_PREFIX                 "PWP"
#define ASCC_REG_REGISTERED_APP_NAME    "PW Presentation"
#define ASSOC_PROG_ID                   "PWP.Presentation"
#define ASSOC_APP_FRIENDLY_NAME         "PW Presentation"
