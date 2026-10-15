"""HWiNFO Panel: a tkinter dashboard for the HWiNFO64 sensor shared memory (see README.md)."""
import csv
import math
import os
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
import traceback

import config
import hwctl
import hwsm
import i18n
import layout
from i18n import t

HERE = os.path.dirname(os.path.abspath(__file__))
ICO = os.path.join(HERE, "panel.ico")


# ---------------------------------------------------------------- CSV logger
class Logger:
    """Every recording session (on -> off) goes to its own CSV file."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.f = self.w = self.path = None
        self.last = 0
        self.delim, self.dec = config.csv_format(cfg)

    def num(self, v, dec):
        """Locale friendly number, e.g. 64.555 -> '64,6' when the decimal symbol is a comma."""
        return f"{v:.{dec}f}".replace(".", self.dec)

    def close(self):
        if self.f:
            self.f.close()
        self.f = self.w = self.path = None

    def write(self, stamp, header, values):
        if self.f is None:
            d = config.log_dir(self.cfg)
            os.makedirs(d, exist_ok=True)
            self.path = os.path.join(d, stamp.replace(" ", "_").replace(":", "-") + ".csv")
            self.f = open(self.path, "a", newline="", encoding="utf-8-sig")
            self.w = csv.writer(self.f, delimiter=self.delim)
            self.w.writerow([t("csv_time")] + header)
        self.w.writerow([stamp] + values)
        self.f.flush()


# ---------------------------------------------------------------- design
C = dict(bg="#0b0f14", card="#121820", stripe="#151c25", border="#1f2833", track="#1e2630",
         fg="#f0f6fc", name="#c9d1d9", dim="#9198a1", faint="#6e7681",
         green="#3fb950", yellow="#e3b341", orange="#f0883e", red="#f85149")


def mix(c1, c2, tt):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * tt) for x, y in zip(a, b))


def round_rect(cv, x0, y0, x1, y1, r, **kw):
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1, x1 - r, y1,
           x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return cv.create_polygon(pts, smooth=True, **kw)


def draw_icon(cv, kind, cx, cy, s, col, bg):
    """s: half size of the icon. Simple vector icons (no font dependency)."""
    lw = max(2, s / 5)
    if kind == "gauge":
        cv.create_arc(cx - s, cy - s, cx + s, cy + s, start=-30, extent=240, style="arc", outline=col, width=lw)
        ang = math.radians(50)
        cv.create_line(cx, cy, cx + s * 0.7 * math.cos(ang), cy - s * 0.7 * math.sin(ang), fill=col,
                       width=lw, capstyle="round")
        cv.create_oval(cx - lw, cy - lw, cx + lw, cy + lw, fill=col, outline="")
    elif kind == "bolt":
        pts = [(0.2, -1), (-0.6, 0.15), (-0.05, 0.15), (-0.25, 1), (0.6, -0.2), (0.05, -0.2)]
        cv.create_polygon([v for x, y in pts for v in (cx + x * s, cy + y * s)], fill=col, outline="")
    elif kind == "temp":
        cv.create_line(cx - s * 0.15, cy - s * 0.75, cx - s * 0.15, cy + s * 0.3, fill=col, width=s * 0.5,
                       capstyle="round")
        cv.create_oval(cx - s * 0.57, cy + s * 0.08, cx + s * 0.27, cy + s * 0.92, fill=col, outline="")
        for k in (-0.6, -0.3, 0.0):
            cv.create_line(cx + s * 0.3, cy + k * s, cx + s * 0.7, cy + k * s, fill=col, width=max(1, lw * 0.6))
    elif kind == "fan":
        for k in range(3):
            a0 = math.radians(k * 120 + 90)
            pts = [cx, cy]
            for tt in range(1, 10):
                f = tt / 10
                ang = a0 - f * math.radians(80)
                rr = s * (0.35 + 0.65 * math.sin(f * math.pi) ** 0.5)
                pts += [cx + rr * math.cos(ang), cy - rr * math.sin(ang)]
            cv.create_polygon(pts, fill=col, outline="", smooth=True)
        cv.create_oval(cx - s * 0.24, cy - s * 0.24, cx + s * 0.24, cy + s * 0.24, fill=bg, outline=col,
                       width=max(1, lw * 0.7))
    elif kind == "net":
        for dx, up in ((-0.42, False), (0.42, True)):
            xx = cx + dx * s
            y0, y1 = (cy + s * 0.9, cy - s * 0.9) if up else (cy - s * 0.9, cy + s * 0.9)
            cv.create_line(xx, y0, xx, y1, fill=col, width=lw, arrow="last",
                           arrowshape=(s * 0.55, s * 0.55, s * 0.38))
    elif kind == "fps":
        round_rect(cv, cx - s, cy - s * 0.75, cx + s, cy + s * 0.5, s * 0.25, fill="", outline=col, width=lw)
        cv.create_polygon(cx - s * 0.22, cy - s * 0.42, cx - s * 0.22, cy + s * 0.17, cx + s * 0.33,
                          cy - s * 0.12, fill=col, outline="")
        cv.create_line(cx - s * 0.45, cy + s * 0.92, cx + s * 0.45, cy + s * 0.92, fill=col, width=lw,
                       capstyle="round")


def pick_font(*names):
    fams = set(tkfont.families())
    return next((n for n in names if n in fams), "TkDefaultFont")


def launch_command():
    """Command line that starts this panel again (used by Windows when the taskbar button is pinned)."""
    exe = sys.executable
    w = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.basename(exe).lower() == "python.exe" and os.path.isfile(w):
        exe = w
    return f'"{exe}" "{os.path.join(HERE, "panel.py")}"'


def main():
    cfg, note = config.load_config()
    i18n.set_language(cfg["language"])
    try:  # own taskbar identity instead of "python"
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID)
    except Exception:
        pass

    hw_exe = hwctl.detect_hwinfo(cfg["hwinfo_path"])
    tasks = hwctl.tasks_installed()
    manage = bool(cfg["manage_hwinfo"]) and tasks
    sync = bool(cfg["sync_hwinfo_interval"]) and tasks

    root = tk.Tk()
    root.title(config.APP_NAME)
    try:
        root.iconbitmap(default=ICO)
    except Exception:
        pass
    try:  # packaged (Store) Python: set identity + icon on the window itself before it is shown
        import winicon
        root.withdraw()
        root.update_idletasks()
        hwnd = int(root.wm_frame(), 16)
        winicon.set_window_identity(hwnd, config.APP_ID, ICO + ",0", launch_command(), config.APP_NAME)
        winicon.set_window_icons(hwnd, ICO)
        root.deiconify()
    except Exception as ex:
        print("icon could not be set:", ex, file=sys.stderr)
        root.deiconify()
    root.configure(bg=C["bg"])
    root.attributes("-topmost", bool(cfg["topmost"]))
    root.minsize(400, 480)

    mon = config.pick_monitor(cfg["monitor"])
    mode = str(cfg["window_mode"]).lower()

    def place(final=False):
        """Put the window on the chosen monitor, then maximise / full-screen it."""
        if mon:
            w, h = min(900, mon["ww"] - 40), min(1400, mon["wh"] - 60)
            x, y = mon["wx"] + 20, mon["wy"] + 20
        else:
            w, h = min(900, root.winfo_screenwidth() - 40), min(1400, root.winfo_screenheight() - 80)
            x, y = 20, 20
        root.state("normal")
        root.geometry(f"{w}x{h}+{x}+{y}")
        if not final:
            return
        root.update_idletasks()
        if mode == "fullscreen":
            root.attributes("-fullscreen", True)
        elif mode != "window":
            root.state("zoomed")

    place()

    F_TXT = pick_font("Segoe UI Variable Text", "Segoe UI")
    F_HEAD = pick_font("Segoe UI Variable Display", "Segoe UI Semibold", "Segoe UI")
    F_NUM = pick_font("Cascadia Mono", "Consolas")
    cv = tk.Canvas(root, bg=C["bg"], highlightthickness=0, bd=0)
    cv.pack(fill="both", expand=True)

    logger = Logger(cfg)
    stats = {}          # row.key -> [min, max, sum, count]; reset at panel start and when recording starts
    st = {"items": {}, "last": {}, "status": {}, "size": None, "ok": False, "sections": [], "auto": True,
          "auto_n": -1, "checked": False, "empty": None, "note": note}

    explicit = cfg["sections"] if isinstance(cfg["sections"], list) else None
    if explicit is not None:
        st["sections"] = layout.build_sections(explicit)
        st["auto"] = not st["sections"]
        st["checked"] = st["auto"]

    spin = tk.Spinbox(root, from_=config.INTERVAL_MIN, to=config.INTERVAL_MAX, increment=0.5, format="%.1f",
                      width=5, bg=C["track"], fg=C["fg"], insertbackground=C["fg"], buttonbackground=C["track"],
                      justify="center", relief="flat", highlightthickness=0, bd=0)
    spin.delete(0, "end")
    spin.insert(0, f"{cfg['interval']:.1f}")

    def current_hint():
        """Why there is no data (empty when everything is fine)."""
        if st["ok"]:
            return ""
        h = t("hint_no_shm") if hwctl.proc_running() else t("hint_not_running")
        if not tasks:
            h += " · " + t("hint_readonly")
        return h

    # ------------------------------------------------------------ drawing
    def build(W, H):
        cv.delete("all")
        st["items"].clear()
        st["last"].clear()
        st["empty"] = None
        sections = st["sections"]
        nrows = sum(len(s.rows) for s in sections)
        HEAD, FOOT, STATUS = 1.75, 0.35, 3.0    # in row heights
        m, g = max(10, W * 0.016), max(8, H * 0.005)
        rh = (H - 2 * m - len(sections) * g) / (nrows + len(sections) * (HEAD + FOOT) + STATUS)
        rh = max(14.0, rh)
        fs_name, fs_num = -max(10, int(rh * 0.50)), -max(10, int(rh * 0.52))
        fs_small, fs_head = -max(9, int(rh * 0.38)), -max(11, int(rh * 0.62))
        f_name, f_num = (F_TXT, fs_name), (F_NUM, fs_num)
        f_unit, f_head, f_col = (F_TXT, fs_small), (F_HEAD, fs_head, "bold"), (F_TXT, fs_small, "bold")
        cx0, cx1 = m, W - m
        cw = cx1 - cx0
        pad = cw * 0.035
        col_name = cx0 + pad
        bar_x0, bar_x1 = cx0 + cw * 0.40, cx0 + cw * 0.53
        unit_w = tkfont.Font(family=F_TXT, size=fs_small).measure("KB/s")
        col_now = cx0 + cw * 0.69                  # right edge of the number, unit follows
        col_min, col_max, col_avg = cx0 + cw * 0.795, cx0 + cw * 0.885, cx1 - pad
        yy = m
        if not sections:
            st["empty"] = cv.create_text(W / 2, H * 0.4, text="", justify="center", width=W * 0.8,
                                         font=(F_HEAD, fs_head, "bold"), fill=C["dim"])
        for sec in sections:
            accent = sec.color
            hh, pb = rh * HEAD, rh * FOOT
            ch = hh + len(sec.rows) * rh + pb
            round_rect(cv, cx0, yy, cx1, yy + ch, 16, fill=C["card"], outline=C["border"])
            cv.create_line(cx0 + 1.5, yy + 16, cx0 + 1.5, yy + ch - 16, fill=accent, width=3)
            hy = yy + hh * 0.5
            isz = rh * 0.40
            bubble = mix(C["card"], accent, 0.16)
            cv.create_oval(col_name, hy - isz * 1.6, col_name + isz * 3.2, hy + isz * 1.6, fill=bubble, outline="")
            draw_icon(cv, sec.icon, col_name + isz * 1.6, hy, isz, accent, bubble)
            cv.create_text(col_name + isz * 3.9, hy, text=sec.title, anchor="w", font=f_head, fill=C["fg"])
            for lbl, xx in ((t("col_now"), col_now + 6 + unit_w), (t("col_min"), col_min),
                            (t("col_max"), col_max), (t("col_avg"), col_avg)):
                cv.create_text(xx, hy, text=lbl, anchor="e", font=f_col, fill=mix(C["dim"], accent, 0.45))
            cv.create_line(cx0 + pad * 0.6, yy + hh - 1, cx1 - pad * 0.6, yy + hh - 1, fill=C["border"])
            ry = yy + hh
            for i, row in enumerate(sec.rows):
                if i % 2:
                    cv.create_rectangle(cx0 + 6, ry, cx1 - 6, ry + rh, fill=C["stripe"], outline="")
                my = ry + rh / 2
                cv.create_text(col_name, my, text=row.name, anchor="w", font=f_name, fill=C["name"])
                it = {"accent": accent}
                if row.bar:
                    bh = max(4, rh * 0.22)
                    round_rect(cv, bar_x0, my - bh / 2, bar_x1, my + bh / 2, bh / 2, fill=C["track"], outline="")
                    it["bar"] = cv.create_rectangle(bar_x0, my - bh / 2, bar_x0, my + bh / 2, fill=accent,
                                                    outline="")
                    it["bargeo"] = (bar_x0, bar_x1, my - bh / 2, my + bh / 2)
                it["now"] = cv.create_text(col_now, my, text="–", anchor="e", font=f_num, fill=C["fg"])
                it["unit"] = cv.create_text(col_now + 6, my, text=row.unit_eff, anchor="w", font=f_unit,
                                            fill=C["faint"])
                for k, xx in (("min", col_min), ("max", col_max), ("avg", col_avg)):
                    it[k] = cv.create_text(xx, my, text="–", anchor="e", font=f_num, fill=C["dim"])
                st["items"][id(row)] = it
                ry += rh
            yy += ch + g
        # ----- status bar (2 lines: controls + info)
        sb_h = rh * (STATUS - 0.2)
        sy = H - m - sb_h
        round_rect(cv, cx0, sy, cx1, sy + sb_h, 16, fill=C["card"], outline=C["border"])
        my = sy + sb_h * 0.36
        iy = sy + sb_h * 0.76
        pw = cw * 0.25
        s = st["status"]
        s["pill"] = round_rect(cv, col_name - 6, my - rh * 0.55, col_name - 6 + pw, my + rh * 0.55, rh * 0.52,
                               fill=C["track"], outline="", tags="logbtn")
        s["dot"] = cv.create_oval(col_name + rh * 0.2, my - rh * 0.18, col_name + rh * 0.56, my + rh * 0.18,
                                  fill=C["red"], outline="", tags="logbtn")
        s["txt"] = cv.create_text(col_name + rh * 0.8, my, text="", anchor="w",
                                  font=(F_TXT, fs_name, "bold"), fill=C["fg"], tags="logbtn")
        # recording mode switch: required rows <-> all sensors
        f_sw = (F_TXT, fs_small, "bold")
        sw_w, sw_h = rh * 1.7, rh * 0.8
        lx = col_name - 6 + pw + cw * 0.05
        s["sw_l"] = cv.create_text(lx, my, text=t("sw_required"), anchor="w", font=f_sw, fill=C["fg"],
                                   tags="modebtn")
        tx0 = lx + tkfont.Font(family=F_TXT, size=fs_small, weight="bold").measure(t("sw_required")) + rh * 0.35
        s["sw_track"] = round_rect(cv, tx0, my - sw_h / 2, tx0 + sw_w, my + sw_h / 2, sw_h / 2,
                                   fill=C["track"], outline=C["border"], tags="modebtn")
        kr = sw_h / 2 - 3
        s["sw_geo"] = (tx0 + 3 + kr, tx0 + sw_w - 3 - kr, my, kr)
        kx = s["sw_geo"][1] if cfg.get("log_all") else s["sw_geo"][0]
        s["sw_knob"] = cv.create_oval(kx - kr, my - kr, kx + kr, my + kr, fill=C["fg"], outline="", tags="modebtn")
        s["sw_r"] = cv.create_text(tx0 + sw_w + rh * 0.35, my, text=t("sw_all"), anchor="w", font=f_sw,
                                   fill=C["faint"], tags="modebtn")
        cv.create_text(cx1 - pad - cw * 0.115, my, text=t("interval_lbl"), anchor="e", font=f_unit, fill=C["dim"])
        spin.config(font=(F_NUM, fs_num))
        cv.create_window(cx1 - pad, my, window=spin, anchor="e", width=cw * 0.1, height=rh * 1.0)
        s["info"] = cv.create_text(col_name, iy, text="", anchor="w", font=f_unit, fill=C["dim"])
        for tag, fn in (("logbtn", toggle), ("modebtn", toggle_mode)):
            cv.tag_bind(tag, "<Button-1>", fn)
            cv.tag_bind(tag, "<Enter>", lambda e: cv.config(cursor="hand2"))
            cv.tag_bind(tag, "<Leave>", lambda e: cv.config(cursor=""))
        refresh_status()

    def set_text(iid, txt, color=None):
        key = (txt, color)
        if st["last"].get(iid) == key:
            return
        st["last"][iid] = key
        if color:
            cv.itemconfig(iid, text=txt, fill=color)
        else:
            cv.itemconfig(iid, text=txt)

    def refresh_status():
        s = st["status"]
        if not s:
            return
        on = cfg["logging"]
        all_ = cfg.get("log_all", False)
        cv.itemconfig(s["pill"], fill=mix(C["card"], C["green"] if on else C["red"], 0.18))
        cv.itemconfig(s["dot"], fill=C["green"] if on else C["red"])
        cv.itemconfig(s["txt"], text=t("log_on") if on else t("log_off"))
        cv.itemconfig(s["sw_track"], fill=mix(C["track"], "#58a6ff", 0.55) if all_ else C["track"])
        cv.itemconfig(s["sw_l"], fill=C["faint"] if all_ else C["fg"])
        cv.itemconfig(s["sw_r"], fill=C["fg"] if all_ else C["faint"])
        hint = current_hint()
        conn = t("conn_ok") if st["ok"] else (hint or t("conn_wait"))
        if st.get("frozen") and st["items"]:
            conn = t("frozen") + (" · " + hint if hint else "")
        ap = st.get("applying")
        if ap and time.time() - ap[0] < 12:
            conn = t("applying", ms=ap[1])
        if on:
            f = os.path.basename(logger.path) if logger.path else t("file_wait")
        else:
            f = t("file_hint")
        mode_txt = t("mode_all", n=st.get("nall", 0)) if all_ else t("mode_req", n=st.get("nreq", 0))
        info = f"{time.strftime('%H:%M:%S')}   ·   {conn}   ·   {mode_txt}   ·   {f}"
        if st.get("note"):
            info = st["note"] + "   ·   " + info
        cv.itemconfig(s["info"], text=info, fill=C["dim"] if st["ok"] else C["red"])
        if st["empty"]:
            cv.itemconfig(st["empty"], text=t("hint_empty") + ("\n\n" + hint if hint else ""))

    def animate_knob(target_x, steps=8):
        s = st["status"]
        x0, x1, my, kr = s["sw_geo"]
        cur = cv.coords(s["sw_knob"])
        if not cur:
            return
        cx = (cur[0] + cur[2]) / 2
        if steps <= 1 or abs(target_x - cx) < 0.5:
            cv.coords(s["sw_knob"], target_x - kr, my - kr, target_x + kr, my + kr)
            return
        nx = cx + (target_x - cx) * 0.45
        cv.coords(s["sw_knob"], nx - kr, my - kr, nx + kr, my + kr)
        root.after(16, lambda: animate_knob(target_x, steps - 1))

    def toggle_mode(e=None):
        cfg["log_all"] = not cfg.get("log_all", False)
        logger.close()          # new file when the mode changes
        logger.last = 0
        config.save_keys(cfg, "log_all")
        s = st["status"]
        if s:
            animate_knob(s["sw_geo"][1] if cfg["log_all"] else s["sw_geo"][0])
        refresh_status()

    def toggle(e=None):
        cfg["logging"] = not cfg["logging"]
        if cfg["logging"]:
            stats.clear()       # new recording: min/max/avg start over
        else:
            logger.close()
        logger.last = 0
        config.save_keys(cfg, "logging")
        refresh_status()

    pending = {"id": None, "apply": None}

    def set_interval(e=None):
        try:
            v = float(spin.get().replace(",", "."))
        except ValueError:
            v = cfg["interval"]
        v = config.clamp_interval(v)
        cfg["interval"] = v
        spin.delete(0, "end")
        spin.insert(0, f"{v:.1f}")
        config.save_keys(cfg, "interval")
        if sync:
            # wait 1.5 s so that clicking the spinbox arrows does not restart HWiNFO on every step
            if pending.get("apply"):
                root.after_cancel(pending["apply"])
            pending["apply"] = root.after(1500, push_interval)

    def push_interval():
        pending["apply"] = None
        ms = hwctl.apply_hwinfo_interval(cfg["interval"], hw_exe)
        if ms:
            st["last_restart"] = time.time()      # no automatic recovery while HWiNFO restarts
            st["applying"] = (time.time(), ms)

    def key_toggle(e):
        if root.focus_get() is not spin:
            toggle()

    spin.config(command=set_interval)
    spin.bind("<Return>", lambda e: (set_interval(), cv.focus_set()))
    spin.bind("<FocusOut>", set_interval)
    root.bind("<KeyPress-l>", key_toggle)
    root.bind("<KeyPress-L>", key_toggle)
    cv.bind("<Button-1>", lambda e: cv.focus_set(), add="+")
    root.bind("<F11>", lambda e: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    def on_resize(e):
        size = (e.width, e.height)
        if size == st["size"]:
            return
        st["size"] = size
        if pending["id"]:
            root.after_cancel(pending["id"])
        pending["id"] = root.after(120, lambda: build(*size))
    cv.bind("<Configure>", on_resize)

    # ------------------------------------------------------------ layout resolution
    def ensure_layout(rd):
        """Explicit layout: if none of its rows exists on this PC, fall back to auto-detection.
        Auto layout: (re)detect whenever the set of readings changes in size."""
        changed = False
        if not st["checked"]:
            st["checked"] = True
            if layout.count_matches(st["sections"], rd) == 0:
                st["auto"] = True
                st["sections"] = []
                changed = True
        if st["auto"] and len(rd) != st["auto_n"]:
            st["auto_n"] = len(rd)
            new = layout.build_sections(layout.autodetect(rd))
            old_sig = [r.key for r in layout.all_rows(st["sections"])]
            if [r.key for r in layout.all_rows(new)] != old_sig:
                st["sections"] = new
                changed = True
        if changed:
            logger.close()
            if st["size"]:
                build(*st["size"])

    # ------------------------------------------------------------ data
    def tick():
        try:
            rd = hwsm.read_all()
            ok = True
        except Exception:
            rd, ok = [], False
        st["ok"] = ok
        now = time.time()
        if ok:
            ensure_layout(rd)
        if ok and st.get("was_down"):
            # HWiNFO just started: first readings may be missing / zero; hold the old values for a few rounds
            st["was_down"] = False
            st["warm_until"] = now + max(3.0, 2.5 * hwctl.hwinfo_interval_ms(hw_exe) / 1000)
        if not ok:
            st["was_down"] = True
        frozen = (not ok) or now < st.get("warm_until", 0)
        st["frozen"] = frozen
        if ok:
            st["down_since"] = None
        elif manage:
            # e.g. the 12 h limit of the free version: no connection for 20 s -> restart HWiNFO (at most every 5 min)
            t0 = st.get("down_since") or now
            st["down_since"] = t0
            if now - t0 > 20 and now - st.get("last_restart", 0) > 300:
                st["last_restart"] = now
                if hwctl.proc_running():
                    hwctl.run_task(hwctl.TASK_STOP)
                    root.after(4000, lambda: hwctl.run_task(hwctl.TASK_START))
                else:
                    hwctl.run_task(hwctl.TASK_START)
        rows = layout.all_rows(st["sections"])
        st["nall"] = len(rd) if ok else st.get("nall", 0)
        st["nreq"] = len(rows)
        logvals = []
        for row in rows:
            r = row.match(rd) if ok else None
            logvals.append(logger.num(r["value"], row.csv_decimals()) if r else "")
            it = st["items"].get(id(row))
            if not it or frozen:
                continue        # frozen: last values stay on screen, stats / bars do not move
            if r:
                v = r["value"]
                s = stats.setdefault(row.key, [v, v, 0.0, 0])
                s[0], s[1], s[2], s[3] = min(s[0], v), max(s[1], v), s[2] + v, s[3] + 1
                avg = s[2] / s[3]
                col = layout.value_color(row, v, C["fg"])
                set_text(it["unit"], row.unit_eff)
                set_text(it["now"], row.fmt_value(v), col)
                for k, val in (("min", s[0]), ("max", s[1]), ("avg", avg)):
                    set_text(it[k], row.fmt_value(val), mix(layout.value_color(row, val, C["fg"]), C["card"], 0.18))
                if "bar" in it:
                    x0, x1, y0, y1 = it["bargeo"]
                    cv.coords(it["bar"], x0, y0, x0 + (x1 - x0) * layout.frac(row, v), y1)
                    cv.itemconfig(it["bar"], fill=col)
        if not frozen and ok and cfg["logging"] and rows and now - logger.last >= cfg["interval"] - 0.05:
            logger.last = now
            try:
                if cfg.get("log_all"):
                    hdr = [f"{r['sensor']} | {r['label']} [{r['unit']}]" for r in rd]
                    vals = [logger.num(r["value"], 3) for r in rd]
                else:
                    hdr = [f"{r.name} ({r.unit_eff})" for r in rows]
                    vals = logvals
                logger.write(time.strftime("%Y-%m-%d %H:%M:%S"), hdr, vals)
            except Exception:
                pass
        refresh_status()
        root.after(500, tick)

    def on_close():
        logger.close()
        if manage:
            hwctl.run_task(hwctl.TASK_STOP)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    st["last_restart"] = time.time()
    if sync and hwctl.apply_hwinfo_interval(cfg["interval"], hw_exe):
        pass                                          # the task adjusted the interval and (re)started HWiNFO
    elif manage and not hwctl.proc_running():
        hwctl.run_task(hwctl.TASK_START)
    # when opened from a shortcut Windows puts the window on the clicked screen: move it, then maximise
    root.after(200, lambda: place(final=True))
    root.after(400, tick)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        try:
            os.makedirs(config.data_dir(), exist_ok=True)
            with open(os.path.join(config.data_dir(), "panel.log"), "w", encoding="utf-8") as f:
                f.write(err)
        except OSError:
            pass
        try:
            import tkinter.messagebox as mb
            r = tk.Tk()
            r.withdraw()
            mb.showerror(config.APP_NAME, err[-1500:])
        except Exception:
            pass
        sys.exit(1)
