#!/usr/bin/env python

import base
import os
import platform

def _find_vs_hosting_v142(programFilesDir):
  """Pick the Visual Studio install and MSVC toolset to build with.

  ONLYOFFICE's third-party stack (boost 1.72, ICU, V8) is validated against the
  VS2019 v142 toolset, so prefer that wherever it lives -- newer Visual Studio
  releases can host it side by side. Failing that, take the *oldest* toolset
  available, since each MSVC release tends to break more of this vintage code
  than the last.

  Returns the chosen install's VC/Auxiliary/Build directory and records the
  toolset in the 'vcvars-ver' option, which base.vcvars_ver_arg() passes to
  vcvarsall.bat."""
  import glob
  build_dirs = []

  # vswhere reports every install including ones outside the default location,
  # which a plain glob over Program Files would miss.
  vswhere = os.path.abspath(base.get_script_dir(__file__) + "/../tools/win/vswhere/vswhere.exe")
  if os.path.isfile(vswhere):
    try:
      import subprocess
      out = subprocess.run([vswhere, "-products", "*", "-all", "-nologo",
                            "-format", "value", "-property", "installationPath"],
                           capture_output=True, text=True, errors="replace").stdout
      for line in out.splitlines():
        line = line.strip()
        if line:
          build_dirs.append(line + "/VC/Auxiliary/Build")
    except Exception as e:
      print("vswhere lookup failed (" + str(e) + "); falling back to a directory scan")

  for pf in {programFilesDir, base.get_env("ProgramFiles"), base.get_env("ProgramFiles(x86)")}:
    if pf:
      build_dirs += glob.glob(pf + "/Microsoft Visual Studio/*/*/VC/Auxiliary/Build")

  # (major, minor, build_dir) for every toolset on the machine
  found = []
  for build_dir in sorted(set(p.replace("\\", "/") for p in build_dirs)):
    if not base.is_dir(build_dir):
      continue
    msvc_dir = build_dir[:-len("/Auxiliary/Build")] + "/Tools/MSVC"
    for toolset in glob.glob(msvc_dir + "/*"):
      if not base.is_dir(toolset):
        continue
      parts = os.path.basename(toolset).split(".")
      if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        found.append((int(parts[0]), int(parts[1]), build_dir))

  if not found:
    print("WARNING: no MSVC toolset found under any Visual Studio install")
    return build_dirs[0].replace("\\", "/") if build_dirs else ""

  v142 = [t for t in found if msvc_family(t[0], t[1]) == "v142"]
  major, minor, build_dir = min(v142 or found)
  # vcvarsall takes the toolset directory version verbatim, e.g. 14.29
  options["vcvars-ver"] = "%d.%d" % (major, minor)
  options["msvc-family"] = msvc_family(major, minor)

  if v142:
    print("using the v142 toolset (%d.%d) from %s" % (major, minor, build_dir))
  else:
    print("WARNING: v142 toolset not installed; using %s (%d.%d) from %s"
          % (options["msvc-family"], major, minor, build_dir))
    print("         ONLYOFFICE's third-party stack is only validated against")
    print("         v142 -- install 'MSVC v142 build tools' if this build fails.")
  return build_dir


def msvc_family(major, minor):
  """Map an MSVC toolset directory version onto its platform-toolset name.

  The directory carries the compiler version (14.16, 14.29, 14.44); the name
  MSBuild, CMake and boost use is coarser -- one per Visual Studio release."""
  if major != 14:
    return "v%d0" % major
  if minor < 10:
    return "v140"   # VS2015
  if minor < 20:
    return "v141"   # VS2017
  if minor < 30:
    return "v142"   # VS2019
  return "v143"     # VS2022 and newer


def parse():
  configfile = open(base.get_script_dir() + "/../config", "r")
  configOptions = {}
  for line in configfile:
    name, value = line.partition("=")[::2]
    k = name.strip()
    v = value.strip(" '\"\r\n")
    if ("true" == v.lower()):
      v = "1"
    if ("false" == v.lower()):
      v = "0"
    configOptions[k] = v
    os.environ["OO_" + k.upper().replace("-", "_")] = v

  # export options
  global options
  options = configOptions

  # all platforms
  global platforms
  platforms = ["win_64", "win_32", "win_64_xp", "win_32_xp", "win_arm64", 
               "linux_64", "linux_32", "linux_arm64",
               "mac_64", "mac_arm64",
               "ios", 
               "android_arm64_v8a", "android_armv7", "android_x86", "android_x86_64"]

  # correction
  host_platform = base.host_platform()
  
  # platform
  if check_option("platform", "all"):
    if ("windows" == host_platform):
      options["platform"] += " win_64 win_32"
    elif ("linux" == host_platform):
      options["platform"] += " linux_64 linux_32"
    else:
      options["platform"] += " mac_64"

  if check_option("platform", "native"):
    bits = "32"
    if platform.machine().endswith('64'):
      bits = "64"
    if ("windows" == host_platform):
      options["platform"] += (" win_" + bits)
    elif ("linux" == host_platform):
      options["platform"] += (" linux_" + bits)
    else:
      options["platform"] += (" mac_" + bits)

  if ("mac" == host_platform) and check_option("platform", "mac_arm64") and not base.is_os_arm():
    if not check_option("platform", "mac_64"):
      options["platform"] = "mac_64 " + options["platform"]

  if (False):
    # use qemu on deploy for emulation 
    if ("windows" == host_platform) and check_option("platform", "win_arm64") and not base.is_os_arm():
      if not check_option("platform", "win_64"):
        options["platform"] = "win_64 " + options["platform"]

  if check_option("platform", "xp") and ("windows" == host_platform):
    options["platform"] += " win_64_xp win_32_xp"

  if check_option("platform", "android"):
    options["platform"] += " android_arm64_v8a android_armv7 android_x86 android_x86_64"

  # check vs-version
  if ("windows" == host_platform) and ("" == option("vs-version")):
    options["vs-version"] = "2019"
    if check_option("platform", "win_64_xp") or check_option("platform", "win_32_xp"):
      options["vs-version"] = "2015"

  if ("windows" == host_platform) and ("2019" == option("vs-version")):
      extend_option("config", "vs2019")
      
  # sysroot setup
  if "linux" != host_platform and "sysroot" in options:
    options["sysroot"] = ""

  if "linux" == host_platform and "sysroot" in options:
    if options["sysroot"] == "0":
      options["sysroot"] = ""
    elif options["sysroot"] == "1":
      dst_dir = os.path.abspath(base.get_script_dir(__file__) + '/../tools/linux/sysroot')
      dst_dir_amd64 = dst_dir + "/ubuntu16-amd64-sysroot"
      dst_dir_arm64 = dst_dir + "/ubuntu16-arm64-sysroot"
      if not base.is_dir(dst_dir_amd64) or not base.is_dir(dst_dir_arm64):
        base.cmd_in_dir(dst_dir, "python3", ["./fetch.py", "all"])
      options["sysroot_linux_64"] = dst_dir_amd64
      options["sysroot_linux_arm64"] = dst_dir_arm64
    else:
      # specific sysroot => one platform for build!
      options["sysroot"] = "1"
      options["sysroot_linux_64"] = options["sysroot"]
      options["sysroot_linux_arm64"] = options["sysroot"]

  if is_cef_107():
    extend_option("config", "cef_version_107")
  if is_v8_60():
    extend_option("config", "v8_version_60")

  # check vs-path
  if ("windows" == host_platform) and ("" == option("vs-path")):
    programFilesDir = base.get_env("ProgramFiles")
    if ("" != base.get_env("ProgramFiles(x86)")):
      programFilesDir = base.get_env("ProgramFiles(x86)")
    if ("2015" == options["vs-version"]):
      options["vs-path"] = programFilesDir + "/Microsoft Visual Studio 14.0/VC"
    elif ("2019" == options["vs-version"]):
      for edition in ("Enterprise", "Professional", "Community", "BuildTools"):
        candidate = programFilesDir + "/Microsoft Visual Studio/2019/" + edition + "/VC/Auxiliary/Build"
        if base.is_dir(candidate):
          options["vs-path"] = candidate
          break
      else:
        # No VS2019 on this machine. ONLYOFFICE's third-party stack is pinned to
        # the v142 toolset, which newer Visual Studio releases can host as a
        # side-by-side component -- find one and pin the toolset explicitly.
        options["vs-path"] = _find_vs_hosting_v142(programFilesDir)

  # check sdkjs-plugins
  if not "sdkjs-plugin" in options:
    options["sdkjs-plugin"] = "default"
  if not "sdkjs-plugin-server" in options:
    options["sdkjs-plugin-server"] = "default"

  if check_option("platform", "ios"):
    if not check_option("config", "no_bundle_xcframeworks"):
      if not check_option("config", "bundle_xcframeworks"):
        extend_option("config", "bundle_xcframeworks")

  if check_option("config", "bundle_xcframeworks"):
    if not check_option("config", "bundle_dylibs"):
      extend_option("config", "bundle_dylibs")

  if ("mac" == host_platform) and check_option("module", "desktop"):
    if not check_option("config", "bundle_dylibs"):
      extend_option("config", "bundle_dylibs")

  if check_option("use-system-qt", "1"):
    base.cmd_in_dir(base.get_script_dir() + "/../tools/linux", "python", ["use_system_qt.py"])
    options["qt-dir"] = base.get_script_dir() + "/../tools/linux/system_qt"

  # disable all warnings (enable if needed with core_enable_all_warnings options)
  if not check_option("config", "core_enable_all_warnings"):
    extend_option("config", "core_disable_all_warnings")

  return

def check_compiler(platform):
  compiler = {}
  compiler["compiler"] = option("compiler")
  compiler["compiler_64"] = compiler["compiler"] + "_64"

  if ("" != compiler["compiler"]):
    if ("ios" == platform):
      compiler["compiler_64"] = compiler["compiler"]
    return compiler

  if (0 == platform.find("win")):
    compiler["compiler"] = "msvc" + options["vs-version"]
    compiler["compiler_64"] = "msvc" + options["vs-version"] + "_64"
    if (0 == platform.find("win_arm")):
      compiler["compiler"] = "msvc" + options["vs-version"] + "_arm"
      compiler["compiler_64"] = "msvc" + options["vs-version"] + "_arm64"
  elif (0 == platform.find("linux")):
    compiler["compiler"] = "gcc"
    compiler["compiler_64"] = "gcc_64"
    if (0 == platform.find("linux_arm")) and not base.is_os_arm():
      compiler["compiler"] = "gcc_arm"
      compiler["compiler_64"] = "gcc_arm64"
  elif (0 == platform.find("mac")):
    compiler["compiler"] = "clang"
    compiler["compiler_64"] = "clang_64"
  elif ("ios" == platform):
    compiler["compiler"] = "ios"
    compiler["compiler_64"] = "ios"
  elif (0 == platform.find("android")):
    compiler["compiler"] = platform
    compiler["compiler_64"] = platform

  if base.host_platform() == "mac":
    if not base.is_dir(options["qt-dir"] + "/" + compiler["compiler_64"]):
      if base.is_dir(options["qt-dir"] + "/macos"):
        compiler["compiler"] = "macos"
        compiler["compiler_64"] = "macos"

  return compiler

def check_option(name, value):
  if not name in options:
    return False
  tmp = " " + options[name] + " "
  if (-1 == tmp.find(" " + value + " ")):
    return False
  return True

def option(name):
  if name in options:
    return options[name]
  return ""

def extend_option(name, value):
  if name in options:
    options[name] = options[name] + " " + value
  else:
    options[name] = value

def set_option(name, value):
  options[name] = value

def branding():
  branding = option("branding-name")
  if ("" == branding):
    branding = "onlyoffice"
  return branding

def is_mobile_platform():
  all_platforms = option("platform")
  if (-1 != all_platforms.find("android")):
    return True
  if (-1 != all_platforms.find("ios")):
    return True
  return False

def get_custom_sysroot_bin(platform):
  use_platform = platform
  if "linux_arm64" == platform and not base.is_os_arm():
    # use cross compiler
    use_platform = "linux_64"

  return option("sysroot_" + use_platform) + "/usr/bin"

def get_custom_sysroot_lib(platform, isNatural=False):
  use_platform = platform
  if "linux_arm64" == platform and not base.is_os_arm() and not isNatural:
    # use cross compiler
    use_platform = "linux_64"

  if ("linux_64" == use_platform):
    return option("sysroot_linux_64") + "/usr/lib/x86_64-linux-gnu"
  if ("linux_arm64" == use_platform):
    return option("sysroot_linux_arm64") + "/usr/lib/aarch64-linux-gnu"
  return ""

def parse_defaults():
  defaults_path = base.get_script_dir() + "/../defaults"
  if ("" != option("branding")):
    defaults_path_branding = base.get_script_dir() + "/../../" + option("branding") + "/build_tools/defaults"
    if base.is_file(defaults_path_branding):
      defaults_path = defaults_path_branding
  defaults_file = open(defaults_path, "r")
  defaults_options = {}
  for line in defaults_file:
    name, value = line.partition("=")[::2]
    k = name.strip()
    v = value.strip(" '\"\r\n")
    if ("true" == v.lower()):
      v = "1"
    if ("false" == v.lower()):
      v = "0"
    defaults_options[k] = v

  for name in defaults_options:
    if name in options:
      options[name] = options[name].replace("default", defaults_options[name])
    else:
      options[name] = defaults_options[name]

  if ("config_addon" in defaults_options):
    extend_option("config", defaults_options["config_addon"])

  return

def is_cef_107():
  if ("linux" == base.host_platform()) and (5004 > base.get_gcc_version()) and not check_option("platform", "android"):
    return True
  return False

def is_v8_60():
  if check_option("platform", "linux_arm64"):
    return False

  if ("linux" == base.host_platform()) and (5004 > base.get_gcc_version()) and not check_option("platform", "android"):
    return True

  if ("windows" == base.host_platform()) and ("2015" == option("vs-version")):
    return True

  #if check_option("config", "use_v8"):
  #  return True

  return False
