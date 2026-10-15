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
        # settings window
        "st_title": "Settings",
        "st_tab_look": "Appearance", "st_tab_log": "Logging", "st_tab_hw": "HWiNFO", "st_tab_layout": "Layout",
        "st_save": "Save", "st_cancel": "Cancel", "st_apply": "Apply", "st_applied": "Applied.",
        "st_invalid": "Check the fields marked in red.", "st_write_err": "config.json could not be written.",
        "st_auto": "Automatic", "st_language": "Language", "st_columns": "Columns", "st_monitor": "Monitor",
        "st_mon_primary": "primary", "st_mon_portrait": "portrait", "st_window_mode": "Window mode",
        "st_wm_maximized": "Maximized", "st_wm_fullscreen": "Full screen", "st_wm_window": "Window",
        "st_topmost": "Always on top", "st_scale": "Row / font scale (%)", "st_scale_hint": "80 - 150, rows never exceed the available height",
        "st_interval": "Interval (s)", "st_interval_hint": "0.5 - 30", "st_logging": "Recording on (L)",
        "st_data": "Recorded data", "st_logdir": "Log folder", "st_logdir_hint": "empty = default folder",
        "st_browse": "Browse…", "st_openfolder": "Open folder", "st_delim": "CSV delimiter",
        "st_decimal": "CSV decimal symbol", "st_tab": "Tab",
        "st_hwpath": "HWiNFO64.EXE", "st_detected": "Detected", "st_notfound": "not found",
        "st_manage": "Start HWiNFO with the panel and stop it when the panel closes",
        "st_sync": "Set HWiNFO's polling interval to the logging interval",
        "st_tasks_ok": "Scheduled tasks: installed (the panel can start / stop HWiNFO without a UAC prompt).",
        "st_tasks_no": "Scheduled tasks: not installed. Run install.ps1 (see README) so the panel can start / stop HWiNFO and set its interval; until then these two options have no effect.",
        "st_lay_show": "Show", "st_lay_name": "Name", "st_lay_green": "Green at", "st_lay_red": "Red at",
        "st_lay_bar": "Bar", "st_lay_title": "Title", "st_lay_color": "Colour",
        "st_lay_reset": "Reset to auto layout", "st_lay_add": "Add sensor", "st_lay_open": "Open config.json",
        "st_lay_reset_q": "Go back to the automatic layout? The custom layout is removed from config.json when you save.",
        "st_lay_empty": "No layout yet: waiting for HWiNFO data.", "st_lay_auto_note": "Automatic layout (editing anything turns it into your own layout).",
        "st_open_err": "Could not open it.",
        "st_add_title": "Add sensor", "st_search": "Search", "st_col_sensor": "Sensor", "st_col_label": "Reading",
        "st_col_unit": "Unit", "st_col_value": "Value", "st_add_to": "Add to section", "st_add_btn": "Add",
        "st_add_none": "HWiNFO data is not available.", "st_custom_section": "Custom", "st_close": "Close",
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
        "st_title": "Ayarlar",
        "st_tab_look": "Görünüm", "st_tab_log": "Kayıt", "st_tab_hw": "HWiNFO", "st_tab_layout": "Düzen",
        "st_save": "Kaydet", "st_cancel": "İptal", "st_apply": "Uygula", "st_applied": "Uygulandı.",
        "st_invalid": "Kırmızı işaretli alanları kontrol edin.", "st_write_err": "config.json yazılamadı.",
        "st_auto": "Otomatik", "st_language": "Dil", "st_columns": "Sütun sayısı", "st_monitor": "Monitör",
        "st_mon_primary": "ana", "st_mon_portrait": "dikey", "st_window_mode": "Pencere modu",
        "st_wm_maximized": "Büyütülmüş", "st_wm_fullscreen": "Tam ekran", "st_wm_window": "Pencere",
        "st_topmost": "Her zaman üstte", "st_scale": "Satır / yazı ölçeği (%)", "st_scale_hint": "80 - 150, satırlar kullanılabilir yüksekliği aşmaz",
        "st_interval": "Aralık (sn)", "st_interval_hint": "0,5 - 30", "st_logging": "Kayıt açık (L)",
        "st_data": "Kaydedilen veri", "st_logdir": "Kayıt klasörü", "st_logdir_hint": "boş = varsayılan klasör",
        "st_browse": "Gözat…", "st_openfolder": "Klasörü aç", "st_delim": "CSV ayırıcı",
        "st_decimal": "CSV ondalık işareti", "st_tab": "Sekme",
        "st_hwpath": "HWiNFO64.EXE", "st_detected": "Bulunan", "st_notfound": "bulunamadı",
        "st_manage": "HWiNFO'yu panel ile aç, panel kapanınca kapat",
        "st_sync": "HWiNFO tarama aralığını kayıt aralığıyla eşitle",
        "st_tasks_ok": "Zamanlanmış görevler: kurulu (panel HWiNFO'yu UAC sormadan açıp kapatabilir).",
        "st_tasks_no": "Zamanlanmış görevler: kurulu değil. Panelin HWiNFO'yu açıp kapatması ve aralığını ayarlaması için install.ps1 çalıştırın (README); o zamana kadar bu iki seçeneğin etkisi yoktur.",
        "st_lay_show": "Göster", "st_lay_name": "Ad", "st_lay_green": "Yeşil", "st_lay_red": "Kırmızı",
        "st_lay_bar": "Çubuk", "st_lay_title": "Başlık", "st_lay_color": "Renk",
        "st_lay_reset": "Otomatik düzene sıfırla", "st_lay_add": "Sensör ekle", "st_lay_open": "config.json'u aç",
        "st_lay_reset_q": "Otomatik düzene dönülsün mü? Kaydettiğinizde özel düzen config.json'dan kaldırılır.",
        "st_lay_empty": "Henüz düzen yok: HWiNFO verisi bekleniyor.", "st_lay_auto_note": "Otomatik düzen (bir şeyi değiştirirseniz kendi düzeniniz olur).",
        "st_open_err": "Açılamadı.",
        "st_add_title": "Sensör ekle", "st_search": "Ara", "st_col_sensor": "Sensör", "st_col_label": "Okuma",
        "st_col_unit": "Birim", "st_col_value": "Değer", "st_add_to": "Eklenecek bölüm", "st_add_btn": "Ekle",
        "st_add_none": "HWiNFO verisi yok.", "st_custom_section": "Özel", "st_close": "Kapat",
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
