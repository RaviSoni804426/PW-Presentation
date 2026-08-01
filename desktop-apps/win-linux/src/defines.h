/*
 * Copyright (C) Ascensio System SIA, 2009-2026
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation, together with the
 * additional terms provided in the LICENSE file.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. For
 * details, see the GNU AGPL at: https://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA by email at info@onlyoffice.com
 * or by postal mail at 20A-6 Ernesta Birznieka-Upisha Street, Riga,
 * LV-1050, Latvia, European Union.
 *
 * The interactive user interfaces in modified versions of the Program
 * are required to display Appropriate Legal Notices in accordance with
 * Section 5 of the GNU AGPL version 3.
 *
 * No trademark rights are granted under this License.
 *
 * All non-code elements of the Product, including illustrations,
 * icon sets, and technical writing content, are licensed under the
 * Creative Commons Attribution-ShareAlike 4.0 International License:
 * https://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
 * This license applies only to such non-code elements and does not
 * modify or replace the licensing terms applicable to the Program's
 * source code, which remains licensed under the GNU Affero General
 * Public License v3.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 */

#ifndef DEFINES_H
#define DEFINES_H

#define rePortalName        "^https?:\\/\\/(.+)"
#define reFileExtension     "\\.(\\w{1,10})$"
#define reUserName          "([^\\.]+)\\.?([^\\.]+)?"
#define reCmdLang           "--(keep)?lang[:|=](\\w{2,5})"

/* PW Presentation branding.
 *
 * The identity values below (data path, registry group, mutex, window class,
 * user-model id, protocol) are deliberately distinct from ONLYOFFICE's so that
 * both products can be installed side by side without sharing settings,
 * single-instance locks or taskbar grouping. */
#define APP_NAME "PWPresentation"
#define APP_TITLE "PW Presentation"
#ifdef __linux
# define APP_DATA_PATH "/pwpresentation/pwpresentation"
# define REG_GROUP_KEY "pwpresentation"
# define APP_MUTEX_NAME "pw:presentation"
# define DESKTOP_FILE_NAME "pw-presentation"
#else
# define APP_DATA_PATH "/PWPresentation/PWPresentation"
# define APP_REG_NAME  "PWPresentation"
# define REG_GROUP_KEY "PWPresentation"
# define REG_UNINST_KEY "PW Presentation"
# define APP_MUTEX_NAME "PWPRESENTATION"
#endif

#define WINDOW_NAME "PW Presentation"
#define WINDOW_TITLE WINDOW_NAME
#define WINDOW_CLASS_NAME L"PWPresentationWindowClass"
#define WINDOW_EDITOR_CLASS_NAME L"PWPresentationSingleWindowClass"
#define REG_APP_NAME "PWPresentation"
#define APP_DEFAULT_LOCALE "en-US"
#define APP_DEFAULT_SYSTEM_LOCALE 1
#define APP_USER_MODEL_ID "PW.Presentation.1"
#define APP_SIMPLE_WINDOW_TITLE "PW Presentation"
#define APP_PROTOCOL "pw-presentation"
#define FILE_PREFIX "pwpresentation_"

#define URL_SITE                "https://github.com/RaviSoni804426/PW-Presentation"
#define URL_SIGNUP              "https://github.com/RaviSoni804426/PW-Presentation"

#define GET_REGISTRY_USER(variable) \
    QSettings variable(QSettings::NativeFormat, QSettings::UserScope, REG_GROUP_KEY, REG_APP_NAME);
#define GET_REGISTRY_SYSTEM(variable) \
    QSettings variable(QSettings::SystemScope, REG_GROUP_KEY, REG_APP_NAME);

#define LOCAL_PATH_OPEN         1
#define LOCAL_PATH_SAVE         2

#define ACTIONPANEL_CONNECT     255
#define ACTIONPANEL_ACTIVATE    ACTIONPANEL_CONNECT + 1

#define URL_AGPL "https://www.gnu.org/licenses/agpl-3.0.en.html"
#define DOWNLOAD_PAGE "https://github.com/RaviSoni804426/PW-Presentation/releases"
#define RELEASE_NOTES "https://github.com/RaviSoni804426/PW-Presentation/releases"

#ifdef __linux
typedef unsigned char BYTE;
#else
# define UM_INSTALL_UPDATE      WM_USER+254
#endif

#define UM_ENDMOVE (QEvent::User + 2)

#define TO_WSTR(str)            L ## str
#define WSTR(str)               TO_WSTR(str)

#ifdef __linux
# define VK_F1 0x70
# define VK_F4 0x73
# define VK_TAB 0x09
#endif

#define APP_PORT   12010
#define SVC_PORT   12011
#define INSTANCE_SVC_PORT 12012
#define INSTANCE_APP_PORT 13012

#define WARNING_LAUNCH_WITH_ADMIN_RIGHTS "App can't working correctly under admin rights."

#include "defines_p.h"

#endif // DEFINES_H

