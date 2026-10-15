"""Read-only access to the HWiNFO64 sensor shared memory (``Global\\HWiNFO_SENS_SM2``).

Every reading is returned as a dict:
    type        1 temp, 2 volt, 3 fan, 4 current, 5 power, 6 clock, 7 usage, 8 other
    sensor      ORIGINAL (English) sensor name   -> use this for matching
    label       ORIGINAL (English) reading label -> use this for matching
    sensor_user / label_user   names as shown in HWiNFO (localised / user renamed)
    id, unit, value, min, max, avg
"""
import ctypes
import struct
from ctypes import wintypes

SHM_NAME = "Global\\HWiNFO_SENS_SM2"
TYPE_NAMES = {1: "temp", 2: "volt", 3: "fan", 4: "current", 5: "power", 6: "clock", 7: "usage", 8: "other"}

_k = ctypes.WinDLL("kernel32", use_last_error=True)
_k.OpenFileMappingW.restype = wintypes.HANDLE
_k.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
_k.MapViewOfFile.restype = ctypes.c_void_p
_k.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
_k.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
_k.CloseHandle.argtypes = [wintypes.HANDLE]

FILE_MAP_READ = 4


def _s(b):
    return b.split(b"\0")[0].decode("mbcs", errors="replace")


def read_all():
    """All readings, or RuntimeError if the shared memory is not available."""
    h = _k.OpenFileMappingW(FILE_MAP_READ, False, SHM_NAME)
    if not h:
        raise RuntimeError("HWiNFO shared memory not available (error %d)" % ctypes.get_last_error())
    p = _k.MapViewOfFile(h, FILE_MAP_READ, 0, 0, 0)
    if not p:
        _k.CloseHandle(h)
        raise RuntimeError("MapViewOfFile failed (error %d)" % ctypes.get_last_error())
    try:
        sig, ver, rev, poll, so, ss, sc, ro, rs, rc = struct.unpack("<IIIqIIIIII", ctypes.string_at(p, 44))
        buf = ctypes.string_at(p, ro + rs * rc)
    finally:
        _k.UnmapViewOfFile(p)
        _k.CloseHandle(h)
    sens = []
    for i in range(sc):
        o = so + i * ss
        sens.append((_s(buf[o + 8:o + 136]), _s(buf[o + 136:o + 264])))
    out = []
    for i in range(rc):
        o = ro + i * rs
        t, si, rid = struct.unpack_from("<III", buf, o)
        lab = _s(buf[o + 12:o + 140])
        usr = _s(buf[o + 140:o + 268])
        unit = _s(buf[o + 268:o + 284])
        val, vmin, vmax, vavg = struct.unpack_from("<dddd", buf, o + 284)
        s_orig, s_user = sens[si] if si < len(sens) else ("", "")
        out.append(dict(type=t, sensor=s_orig, sensor_user=s_user or s_orig, id=rid, label=lab or usr,
                        label_user=usr or lab, unit=unit, value=val, min=vmin, max=vmax, avg=vavg))
    return out
