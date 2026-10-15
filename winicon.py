"""Gives a window its own taskbar identity + icon (SHGetPropertyStoreForWindow).
Packaged (Microsoft Store) Python ignores the process-level AppUserModelID, so it is set on the window itself."""
import ctypes
from ctypes import wintypes

_FMTID = "{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}"
PID_RELAUNCH_CMD, PID_RELAUNCH_ICON, PID_RELAUNCH_NAME, PID_ID = 2, 3, 4, 5


class GUID(ctypes.Structure):
    _fields_ = [("d1", wintypes.DWORD), ("d2", wintypes.WORD), ("d3", wintypes.WORD), ("d4", ctypes.c_ubyte * 8)]


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID), ("pid", wintypes.DWORD)]


def _guid(s):
    g = GUID()
    ctypes.oledll.ole32.CLSIDFromString(ctypes.c_wchar_p(s), ctypes.byref(g))
    return g


def set_window_identity(hwnd, app_id, icon_path, relaunch_cmd, name):
    iid = _guid("{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}")
    ps = ctypes.c_void_p()
    ctypes.oledll.shell32.SHGetPropertyStoreForWindow(wintypes.HWND(hwnd), ctypes.byref(iid), ctypes.byref(ps))
    vtbl = ctypes.cast(ctypes.cast(ps, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    SetValue = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(PROPERTYKEY), ctypes.c_void_p)(vtbl[6])
    Commit = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p)(vtbl[7])
    Release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtbl[2])
    keep = []

    def setstr(pid, text):
        pv = (ctypes.c_ubyte * 24)()
        ctypes.memmove(pv, ctypes.byref(ctypes.c_ushort(31)), 2)          # VT_LPWSTR
        buf = ctypes.create_unicode_buffer(text)
        keep.append(buf)
        ctypes.memmove(ctypes.addressof(pv) + 8, ctypes.byref(ctypes.c_void_p(ctypes.addressof(buf))), 8)
        key = PROPERTYKEY(_guid(_FMTID), pid)
        SetValue(ps, ctypes.byref(key), ctypes.addressof(pv))

    try:
        setstr(PID_RELAUNCH_CMD, relaunch_cmd)
        setstr(PID_RELAUNCH_ICON, icon_path)
        setstr(PID_RELAUNCH_NAME, name)
        setstr(PID_ID, app_id)
        Commit(ps)
    finally:
        Release(ps)


def set_window_icons(hwnd, ico_path):
    """Big / small icon through WM_SETICON (Alt+Tab, title bar, taskbar)."""
    u = ctypes.windll.user32
    u.LoadImageW.restype = wintypes.HANDLE
    u.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int,
                             wintypes.UINT]
    u.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    for which, size in ((1, 48), (0, 16)):   # ICON_BIG, ICON_SMALL
        h = u.LoadImageW(None, ico_path, 1, size, size, 0x10)   # IMAGE_ICON, LR_LOADFROMFILE
        if h:
            u.SendMessageW(hwnd, 0x80, which, h)                 # WM_SETICON
