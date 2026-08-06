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

#include <QApplication>
#include <QProcess>
#include <QFileInfo>
#include <QDir>
#include <Windows.h>
#include <tlhelp32.h>
#include <string.h>
#include <string>
#include <utility>
#include <vector>
#ifndef __OS_WIN_XP
# include "jumplist.h"
# include "shellassoc.h"
# include <shlobj_core.h>
#endif
/* For APP_MUTEX_NAME. Taken from the editor's own header rather than declared
   again here: this file already keeps a second copy of APP_USER_MODEL_ID in
   ProjIcons.pro, and that copy silently drifting from defines.h is exactly
   what made PW Docs share a taskbar button with its siblings. */
#include "defines.h"


void SetAppUserModelId()
{
    if (HMODULE lib = LoadLibrary(L"shell32")) {
        HRESULT (WINAPI *SetAppUserModelID)(PCWSTR AppID);
        *(FARPROC*)&SetAppUserModelID = GetProcAddress(lib, "SetCurrentProcessExplicitAppUserModelID");
        if (SetAppUserModelID)
            SetAppUserModelID(TEXT(APP_USER_MODEL_ID));
        FreeLibrary(lib);
    }
}


/* --- single-instance recovery ----------------------------------------------
   editors.exe guards itself with a named mutex plus a hidden receiver window,
   and hands a second launch's command line to the first instance over
   WM_COPYDATA. A crash or a forced kill can leave a process that still holds
   the mutex but never answers again. The next launch then blocks trying to
   hand off to it, so no window ever appears and the process never exits -
   every further click of the icon just stacks up another stuck process behind
   the same mutex. That is what makes the icon look dead: no window, no error.

   Clear those leftovers here, before editors.exe is started, so clicking the
   icon always opens the app. Two rules keep this safe:

     - if any process from this install still shows a window, nothing is
       touched at all; a live editor must never be killed, even if it is busy
       and temporarily not answering;
     - a process too young to have opened its window yet is left alone, so
       double-clicking the icon cannot kill the instance that is still coming up.

   Only this install's own processes are ever considered, so the other PW apps
   are never affected. */

// Minimum age before a windowless process counts as stuck rather than starting.
#define STARTUP_GRACE_MS 90000

static BOOL CALLBACK findVisibleWindow(HWND hwnd, LPARAM lparam)
{
    std::pair<DWORD, bool> *seek = reinterpret_cast<std::pair<DWORD, bool>*>(lparam);
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid == seek->first && IsWindowVisible(hwnd)) {
        seek->second = true;
        return FALSE;
    }
    return TRUE;
}

static bool ownsVisibleWindow(DWORD pid)
{
    std::pair<DWORD, bool> seek(pid, false);
    EnumWindows(findVisibleWindow, reinterpret_cast<LPARAM>(&seek));
    return seek.second;
}

static void ClearWedgedInstance(const QString &appDir)
{
    HANDLE hMutex = OpenMutex(SYNCHRONIZE, FALSE, TEXT(APP_MUTEX_NAME));
    if (!hMutex)
        return;                 // nothing registered: an ordinary cold start
    CloseHandle(hMutex);

    const std::wstring prefix =
        (QDir::toNativeSeparators(appDir) + QStringLiteral("\\")).toStdWString();

    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE)
        return;

    std::vector<HANDLE> stuck;
    bool showingWindow = false;

    PROCESSENTRY32W pe;
    pe.dwSize = sizeof(pe);
    if (Process32FirstW(snap, &pe)) {
        do {
            if (_wcsicmp(pe.szExeFile, L"editors.exe") != 0 &&
                _wcsicmp(pe.szExeFile, L"editors_helper.exe") != 0)
                continue;

            HANDLE proc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_TERMINATE,
                                      FALSE, pe.th32ProcessID);
            if (!proc)
                continue;

            wchar_t path[MAX_PATH] = {0};
            DWORD len = MAX_PATH;
            if (!QueryFullProcessImageNameW(proc, 0, path, &len) ||
                _wcsnicmp(path, prefix.c_str(), prefix.size()) != 0) {
                CloseHandle(proc);  // not ours - another PW app, or unrelated
                continue;
            }

            if (ownsVisibleWindow(pe.th32ProcessID)) {
                showingWindow = true;
                CloseHandle(proc);
                continue;
            }

            FILETIME created, exited, kernel, user, nowFt;
            if (GetProcessTimes(proc, &created, &exited, &kernel, &user)) {
                GetSystemTimeAsFileTime(&nowFt);
                ULARGE_INTEGER c, now;
                c.LowPart    = created.dwLowDateTime;  c.HighPart   = created.dwHighDateTime;
                now.LowPart  = nowFt.dwLowDateTime;    now.HighPart = nowFt.dwHighDateTime;
                if (now.QuadPart > c.QuadPart &&
                    (now.QuadPart - c.QuadPart) / 10000ULL < STARTUP_GRACE_MS) {
                    CloseHandle(proc);  // still starting up
                    continue;
                }
            }
            stuck.push_back(proc);
        } while (Process32NextW(snap, &pe));
    }
    CloseHandle(snap);

    for (size_t i = 0; i < stuck.size(); ++i) {
        if (!showingWindow)
            TerminateProcess(stuck[i], 0);
        CloseHandle(stuck[i]);
    }
}


int main(int argc, char *argv[])
{
    SetAppUserModelId();

    QApplication a(argc, argv);
//    return a.exec();

    QStringList _cmdArgs(QCoreApplication::arguments().mid(1));
#ifndef __OS_WIN_XP
    if (_cmdArgs.contains("--create-jump-list")) {
        CreateJumpList();
        return 0;
    } else
    if (_cmdArgs.contains("--remove-jump-list")) {
        ClearHistory();
        DeleteJumpList();
        return 0;
    } else
    if (_cmdArgs.contains("--assoc")) {
        if (_cmdArgs.size() > 1) {
            std::wstring assocLine = _cmdArgs.at(1).toStdWString();
            size_t len = assocLine.length();
            if (len == 0)
                return 0;

            std::vector<AssocPair> assocList;
            wchar_t *buf = &assocLine[0];
            if (buf[len - 1] == ';')
                buf[len - 1] = '\0';

            size_t last_sep_pos = 0;
            wchar_t *it = buf;
            while (1) {
                while (*it != '\0' && *it != ';')
                    it++;
                wchar_t tmp = *it;
                *it = '\0';
                wchar_t *pair = buf + last_sep_pos;
                if (wchar_t *colon = wcschr(pair, L':')) {
                    *colon = L'\0';
                    assocList.push_back({pair, colon + 1});
                }
                if (tmp == '\0')
                    break;
                last_sep_pos = it - buf + 1;
                it++;
            }
            if (!assocList.empty())
                SetUserFileAssoc(assocList);
        }
        return 0;
    }
#endif

    QFileInfo _fi(QString::fromLocal8Bit(argv[0]));

    qputenv("Path", "./converter;" + qgetenv("Path"));

#define APP_LAUNCH_NAME "./DesktopEditors.exe"

    // Undo a previous crash or forced kill, or this launch would hand off to a
    // process that never answers and no window would appear.
    ClearWedgedInstance(_fi.absolutePath());

//    QProcess::startDetached(fi.absolutePath() + APP_LAUNCH_NAME, _cmdArgs, fi.absolutePath());
    QProcess::startDetached(_fi.absolutePath() + "./editors.exe", _cmdArgs, _fi.absolutePath());

    return 0;
}
