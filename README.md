# HWiNFO Panel

A compact always-on-top dashboard for Windows that shows live data from [HWiNFO](https://www.hwinfo.com/):
clocks, usage, power, temperatures, fans, network/disk throughput and PresentMon FPS, each with a colour
gradient (green to red), a bar, and panel-side MIN / MAX / AVG. It can also record the values to CSV files.
Made for a small secondary or portrait monitor, but it runs happily on any screen (window, maximized or full screen).

> Not affiliated with, endorsed by, or sponsored by HWiNFO / REALiX s.r.o. HWiNFO is a trademark of its owner.
> This project only *reads* the sensor data that HWiNFO publishes through its documented shared memory interface.

Türkçe açıklama için aşağıya bakın: [Türkçe](#türkçe).

## Features

- Layout built **automatically from your hardware** (per-core CPU clocks for AMD and Intel incl. P-/E-cores, CPU
  usage / power / temperatures, GPU NVIDIA / AMD / Intel, RAM / VRAM, motherboard VRM / PCH temps, all motherboard
  fans, drive temperatures, network of the busiest adapter, disk read/write, PresentMon FPS). Rows that do not exist
  on your PC are simply left out.
- Fully **configurable** (`config.json`): sections, rows, regex matching on HWiNFO's *original English* names,
  number formats, units, colour limits, bars.
- 256-step green to red colour gradient per row from its limits (reversed limits for FPS: low = red).
- **CSV logging**: every on/off session writes a new file; "required rows" or "all sensors" (slide switch);
  interval 0.5 to 30 s (spin box in the panel). Press `L` to toggle recording, `F11` for full screen.
- Optional (after `install.ps1`): the panel **starts HWiNFO when it opens and stops it when it closes**, writes the
  logging interval to HWiNFO's `SensorInterval`, and restarts HWiNFO automatically when the shared memory is gone for
  more than 20 s (the free HWiNFO version stops its sensors after 12 hours). Without this the panel runs in read-only
  mode and shows a hint when HWiNFO is not running.
- English and Turkish UI (follows the Windows display language by default).
- Pure Python standard library; no packages to install.

## Requirements

- Windows 10 / 11
- [HWiNFO64](https://www.hwinfo.com/download/) with **Settings > "Shared Memory Support" enabled**
  (in the Sensors window settings). The free version limits the shared memory to **12 hours** per start; with the
  installed tasks the panel restarts HWiNFO for you, otherwise restart it yourself.
- Python 3.10+ with tkinter (python.org installer, or the Microsoft Store version). Check:
  `python -c "import tkinter"`.

## Install

1. Download / clone this folder anywhere (it is used in place, do not delete it afterwards).
2. Enable *Shared Memory Support* in HWiNFO.
3. In PowerShell, in this folder:

   ```powershell
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```

   * creates the Start Menu shortcut **HWiNFO Panel** (with its own taskbar icon),
   * asks once for administrator rights (UAC) to copy `hidden.vbs` and `set_interval.ps1` to
     `%ProgramFiles%\HWiNFO Panel` and to register three scheduled tasks
     `\HWiNFO Panel\Start`, `Stop`, `SetInterval`. They let the panel start/stop HWiNFO (which itself needs
     administrator rights) without a UAC prompt each time. Use `-NoTasks` to skip this part.
   * `-HwinfoPath "D:\Tools\HWiNFO64\HWiNFO64.EXE"` if your HWiNFO is not found automatically.

   You can also skip the installer completely: `pythonw panel.py` (or `python panel.py`) works, in read-only mode.

4. Start **HWiNFO Panel** from the Start Menu.

Uninstall: `powershell -ExecutionPolicy Bypass -File uninstall.ps1` removes the tasks, the Program Files folder and the
shortcut and keeps your settings and logs; add `-Purge` to delete them as well.

Security note: the tasks run only the two files in `%ProgramFiles%\HWiNFO Panel` (writable by administrators only).
The only user-writable input is a text file containing the interval, which is accepted only as an integer
(clamped to 250 to 60000 ms).

## Files and settings

Everything personal lives in `%LOCALAPPDATA%\HWiNFO Panel\` (created on first run, never part of the repository):

| File | Purpose |
|---|---|
| `config.json` | your settings and (optionally) your layout |
| `logs\` | CSV recordings (default folder, see `log_dir`) |
| `hwinfo_interval.txt` | interval handed to the `SetInterval` task |
| `panel.log` | traceback if the panel crashed at start |

Set the environment variable `HWINFO_PANEL_DIR` to use another folder (portable use).

### config.json

| Key | Values | Meaning |
|---|---|---|
| `language` | `"auto"`, `"tr"`, `"en"` | UI language (`auto` = Windows display language) |
| `monitor` | `"auto"` or index | `auto` = first non-primary portrait monitor, otherwise the primary one. Indexes: `python tools/list_monitors.py` |
| `window_mode` | `"maximized"`, `"fullscreen"`, `"window"` | how the window is placed on that monitor |
| `topmost` | `true` / `false` | keep the window on top |
| `interval` | 0.5 to 30 | CSV logging interval in seconds |
| `logging` | `true` / `false` | recording on/off (also toggled in the panel) |
| `log_all` | `true` / `false` | `false` = only the rows shown, `true` = every HWiNFO sensor |
| `log_dir` | path or `""` | CSV folder; `""` = `%LOCALAPPDATA%\HWiNFO Panel\logs` |
| `csv_delimiter`, `csv_decimal` | `"auto"` or a character | `auto` uses the Windows list separator / decimal symbol so Excel opens the file correctly |
| `sync_hwinfo_interval` | `true` / `false` | also set HWiNFO's polling interval to `interval` (needs the installed tasks) |
| `manage_hwinfo` | `true` / `false` | start HWiNFO with the panel, stop it on close (needs the installed tasks) |
| `hwinfo_path` | `"auto"` or path | location of `HWiNFO64.EXE` (auto: registry, then `%ProgramFiles%\HWiNFO64`) |
| `sections` | `"auto"` or a list | the layout, see below |

### Customising the layout

With `"sections": "auto"` the layout is detected from your sensors each time the panel starts. To edit it, write the
detected layout into `config.json` (HWiNFO must be running):

```
python tools/export_layout.py
```

and change the `sections` list. If none of your rows exists on a PC, the panel falls back to auto-detection.

```json
"sections": [
  {
    "title": "TEMPERATURES",
    "color": "#ff7b72",
    "icon": "temp",
    "rows": [
      { "name": "GPU", "sensor": "^dGPU \\[#0\\]", "label": "^GPU Temperature", "type": 1,
        "format": "{:.0f}", "unit": "°C", "limits": [30, 88], "bar": true },
      { "name": "Case fan", "sensor": "Super-I/O", "label": "^System 1$", "type": 3,
        "format": "{:.0f}", "unit": "RPM", "limits": [300, 1800] }
    ]
  }
]
```

* `icon`: `gauge`, `bolt`, `temp`, `fan`, `net`, `fps`. `color`: any `#rrggbb`.
* `sensor`, `label`: **case-insensitive regular expressions** (`re.search`) matched against HWiNFO's
  **original English** sensor and reading names, so a layout works with any HWiNFO / Windows language. `sensor` is
  optional. The first matching reading wins. `type` (optional): 1 temp, 2 voltage, 3 fan, 4 current, 5 power,
  6 clock, 7 usage, 8 other.
* `format`: Python format for the number, e.g. `"{:.1f}"`. `unit`: text shown (default: HWiNFO's unit).
* `limits`: `[green_value, red_value]`: the colour moves from green to red between them (a bigger green value than
  red value reverses it, as for FPS). Without `limits` the row has no bar / gradient. `bar`: `false` hides the bar.
* To find the names on your PC: `python tools/list_sensors.py` (optionally with filter words:
  `python tools/list_sensors.py gpu temp`). The output may contain serial numbers; do not post it publicly.

### CSV format

One file per recording session: `YYYY-MM-DD_HH-MM-SS.csv` in `log_dir`, UTF-8 with BOM, first column the time stamp,
then one column per row ("name (unit)") or, in "all data" mode, one column per HWiNFO reading
("sensor | label [unit]"). Delimiter and decimal symbol follow your Windows regional settings by default
(e.g. `;` and `,` in Turkish / German Excel).

### Privacy

Everything stays on your PC. The panel reads HWiNFO's local shared memory and writes only the files above.
It has no network code and sends nothing anywhere.

## Troubleshooting

* "HWiNFO is running but shared memory is off": enable *Shared Memory Support* in HWiNFO's settings and restart it.
* Values freeze every 12 hours with the free HWiNFO: install the tasks (`install.ps1`) for automatic restart.
* Wrong monitor: `python tools/list_monitors.py`, then set `"monitor"`.
* Python icon instead of the panel icon in the taskbar when started with `python panel.py`: use the Start Menu shortcut.
* Crash on start: see `%LOCALAPPDATA%\HWiNFO Panel\panel.log`.

## Development

`hwsm.py` (shared memory reader), `layout.py` (rows, matching, auto-detection), `config.py` (settings, monitors),
`hwctl.py` (HWiNFO detection and tasks), `i18n.py` (strings), `panel.py` (UI), `winicon.py` (taskbar identity),
`make_icon.py` (regenerates `panel.ico`). License: MIT.

---

## Türkçe

HWiNFO'nun paylaşılan belleğinden canlı veri gösteren, her zaman üstte duran küçük bir Windows panosu: saat/kullanım,
güç, sıcaklık, fan, ağ/disk ve PresentMon FPS; her satırda yeşilden kırmızıya renk, çubuk ve panel tarafında
MİN / MAKS / ORT. İsterseniz değerleri CSV dosyasına kaydeder. HWiNFO / REALiX ile bağlantısı yoktur.

**Gereksinimler:** Windows 10/11; HWiNFO64 (Ayarlar > **Shared Memory Support** açık; ücretsiz sürümde paylaşılan
bellek her başlatmada **12 saat** ile sınırlıdır); Python 3.10+ (tkinter dahil).

**Kurulum:** klasörü bir yere koyun, HWiNFO'da Shared Memory Support'u açın, bu klasörde
`powershell -ExecutionPolicy Bypass -File install.ps1` çalıştırın. Başlat menüsüne "HWiNFO Panel" kısayolu eklenir ve
(bir kez UAC onayıyla) HWiNFO'yu her seferinde UAC sormadan açıp kapatan 3 zamanlanmış görev kurulur
(`-NoTasks` ile atlanır; görevler olmadan panel salt okunur çalışır). Kaldırma: `uninstall.ps1`
(ayarlar ve kayıtlar kalır, silmek için `-Purge`).

**Ayarlar:** `%LOCALAPPDATA%\HWiNFO Panel\config.json` ilk açılışta oluşur. `language` (`auto`/`tr`/`en`), `monitor`,
`window_mode`, `interval`, `log_dir`, `manage_hwinfo` vb. yukarıdaki tabloda açıklanmıştır. Düzen varsayılan olarak
donanımınızdan otomatik üretilir; düzenlemek için HWiNFO açıkken `python tools/export_layout.py` ile `sections`
listesini yazdırıp elle değiştirin. Sensör ve etiket kalıpları HWiNFO'nun **İngilizce orijinal adlarına** göre
(düzenli ifade) eşleşir; adları görmek için `python tools/list_sensors.py` kullanın (çıktıda seri numaraları
olabilir, paylaşmayın).

**Kısayollar:** `L` kaydı açar/kapatır, `F11` tam ekran. **CSV:** her kayıt oturumu ayrı dosyadır; ayırıcı ve ondalık
işareti varsayılan olarak Windows bölge ayarlarından alınır (Türkçe Excel için `;` ve `,`).
**Gizlilik:** veriler bilgisayarınızdan çıkmaz; ağ erişimi yoktur.
