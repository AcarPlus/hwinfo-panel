# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: one-folder, windowed build -> dist\HWiNFO Panel\HWiNFO Panel.exe
# Build with packaging\build.ps1 (creates its own venv); SPECPATH is this folder.
import os
import re

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo)

ROOT = os.path.dirname(SPECPATH)
with open(os.path.join(ROOT, "version.py"), encoding="utf-8") as _f:
    VERSION = re.search(r'__version__\s*=\s*"([^"]+)"', _f.read()).group(1)
_nums = (tuple(int(x) for x in re.findall(r"\d+", VERSION)) + (0, 0, 0, 0))[:4]

_vi = VSVersionInfo(
    ffi=FixedFileInfo(filevers=_nums, prodvers=_nums, mask=0x3F, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0),
    kids=[
        StringFileInfo([StringTable("040904B0", [
            StringStruct("CompanyName", "AcarPlus"),
            StringStruct("FileDescription", "HWiNFO Panel"),
            StringStruct("FileVersion", VERSION),
            StringStruct("InternalName", "HWiNFO Panel"),
            StringStruct("LegalCopyright", "MIT License"),
            StringStruct("OriginalFilename", "HWiNFO Panel.exe"),
            StringStruct("ProductName", "HWiNFO Panel"),
            StringStruct("ProductVersion", VERSION),
        ])]),
        VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
    ],
)
_work = os.path.join(os.path.abspath(workpath), "version_info.txt")
os.makedirs(os.path.dirname(_work), exist_ok=True)
with open(_work, "w", encoding="utf-8") as _f:
    _f.write(str(_vi))

a = Analysis(
    [os.path.join(ROOT, "panel.py")],
    pathex=[ROOT],
    binaries=[],
    # read at run time from sys._MEIPASS (see config.APP_DIR); hidden.vbs / set_interval.ps1 are what the
    # scheduled tasks run (the Setup copies them to {app}\tasks, install.ps1 users do not need the bundle)
    datas=[
        (os.path.join(ROOT, "panel.ico"), "."),
        (os.path.join(ROOT, "hidden.vbs"), "."),
        (os.path.join(ROOT, "set_interval.ps1"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["unittest", "pydoc", "test", "numpy", "PIL", "matplotlib"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HWiNFO Panel",
    icon=os.path.join(ROOT, "panel.ico"),
    version=_work,
    console=False,
    debug=False,
    strip=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="HWiNFO Panel")
