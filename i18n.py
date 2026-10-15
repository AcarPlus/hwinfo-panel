"""UI strings (English / Turkish). Use ``t("key")``; the language is chosen once with ``set_language``."""
import ctypes

_STR = {
    "en": {
        # column headers
        "col_now": "NOW", "col_min": "MIN", "col_max": "MAX", "col_avg": "AVG",
        # default section titles
        "sec_clock": "CLOCK / USAGE", "sec_power": "POWER", "sec_temp": "TEMPERATURES", "sec_fan": "FANS",
        "sec_net": "NETWORK / DISK", "sec_fps": "FPS",
        # default row names
        "clock": "Clock", "gpu": "GPU", "cpu_usage": "CPU Total Usage", "cpu_maxthread": "CPU Busiest Thread",
        "gpu_clock": "GPU Clock", "gpu_load": "GPU Core Load", "vram": "VRAM Used", "ram": "RAM Used",
        "cpu_pkg_power": "CPU Package Power", "cpu_core_power": "CPU Core Power", "cpu_soc_power": "CPU SoC Power",
        "cpu_core_volt": "CPU Core Voltage", "gpu_power": "GPU Power", "gpu_volt": "GPU Core Voltage",
        "cpu_temp": "CPU Temperature", "cpu_ccd": "CPU CCD{n}", "cpu_iod": "CPU IOD Hotspot",
        "cpu_core_max": "CPU Hottest Core", "gpu_temp": "GPU", "gpu_hot": "GPU Hot Spot",
        "gpu_memtemp": "VRAM (Mem Junction)", "gpu_fan": "GPU Fan", "dimm": "RAM DIMM {n}", "mb": "Motherboard {n}",
        "download": "Download", "upload": "Upload", "disk_read": "Disk Read", "disk_write": "Disk Write",
        "fps": "FPS", "fps_1": "FPS 1% Low", "fps_01": "FPS 0.1% Low", "drive": "Drive",
        # status bar
        "log_on": "RECORDING ON", "log_off": "RECORDING OFF", "sw_required": "Required", "sw_all": "All data",
        "interval_lbl": "interval (s)", "conn_ok": "HWiNFO connected", "conn_wait": "waiting for HWiNFO…",
        "frozen": "data paused, HWiNFO reconnecting…",
        "applying": "setting HWiNFO polling interval to {ms} ms · values held…",
        "mode_all": "all data ({n} columns)", "mode_req": "required data ({n} columns)",
        "file_wait": "waiting", "file_hint": "press L to record",
        "hint_not_running": "HWiNFO is not running: start HWiNFO64 in sensors mode",
        "hint_no_shm": "HWiNFO is running but shared memory is off: Settings > Shared Memory Support",
        "hint_empty": "Waiting for HWiNFO sensor data…",
        "hint_readonly": "read-only mode (run install.ps1 to let the panel start/stop HWiNFO)",
        "csv_time": "Time",
    },
    "tr": {
        "col_now": "ŞİMDİ", "col_min": "MİN", "col_max": "MAKS", "col_avg": "ORT",
        "sec_clock": "SAAT / KULLANIM", "sec_power": "GÜÇ", "sec_temp": "SICAKLIK", "sec_fan": "FAN",
        "sec_net": "AĞ / DİSK", "sec_fps": "FPS",
        "clock": "Saat", "gpu": "GPU", "cpu_usage": "CPU Toplam Kullanım", "cpu_maxthread": "CPU En Yüklü Thread",
        "gpu_clock": "GPU Saati", "gpu_load": "GPU Çekirdek Yükü", "vram": "VRAM Kullanılan", "ram": "RAM Kullanılan",
        "cpu_pkg_power": "CPU Paket Gücü", "cpu_core_power": "CPU Core Gücü", "cpu_soc_power": "CPU SoC Gücü",
        "cpu_core_volt": "CPU Core Voltajı", "gpu_power": "GPU Toplam Güç", "gpu_volt": "GPU Çekirdek Voltajı",
        "cpu_temp": "CPU Sıcaklığı", "cpu_ccd": "CPU CCD{n}", "cpu_iod": "CPU IOD Hotspot",
        "cpu_core_max": "CPU En Sıcak Çekirdek", "gpu_temp": "GPU", "gpu_hot": "GPU Hot Spot",
        "gpu_memtemp": "VRAM (Mem Junction)", "gpu_fan": "GPU Fan", "dimm": "RAM DIMM {n}", "mb": "Anakart {n}",
        "download": "Download", "upload": "Upload", "disk_read": "Disk Okuma", "disk_write": "Disk Yazma",
        "fps": "FPS", "fps_1": "FPS 1% Low", "fps_01": "FPS 0.1% Low", "drive": "Disk",
        "log_on": "KAYIT AÇIK", "log_off": "KAYIT KAPALI", "sw_required": "Gerekli", "sw_all": "Tüm veriler",
        "interval_lbl": "aralık (sn)", "conn_ok": "HWiNFO bağlı", "conn_wait": "HWiNFO bekleniyor…",
        "frozen": "veri akışı duraklatıldı, HWiNFO yeniden bağlanıyor…",
        "applying": "HWiNFO tarama aralığı {ms} ms yapılıyor · değerler bekletiliyor…",
        "mode_all": "tüm veriler ({n} sütun)", "mode_req": "gerekli veriler ({n} sütun)",
        "file_wait": "bekleniyor", "file_hint": "kayıt için L",
        "hint_not_running": "HWiNFO çalışmıyor: HWiNFO64'ü sensör modunda açın",
        "hint_no_shm": "HWiNFO çalışıyor ama paylaşılan bellek kapalı: Ayarlar > Shared Memory Support",
        "hint_empty": "HWiNFO sensör verisi bekleniyor…",
        "hint_readonly": "salt okunur mod (HWiNFO'yu panelin açıp kapatması için install.ps1 çalıştırın)",
        "csv_time": "Zaman",
    },
}

_lang = "en"


def windows_language():
    """'tr' if the Windows display language is Turkish, otherwise 'en'."""
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "tr" if (lid & 0x3FF) == 0x1F else "en"
    except Exception:
        return "en"


def set_language(code):
    """code: 'auto' | 'tr' | 'en'. Returns the language actually used."""
    global _lang
    code = (code or "auto").lower()
    _lang = windows_language() if code == "auto" else (code if code in _STR else "en")
    return _lang


def language():
    return _lang


def t(key, **kw):
    s = _STR.get(_lang, _STR["en"]).get(key) or _STR["en"].get(key) or key
    return s.format(**kw) if kw else s
