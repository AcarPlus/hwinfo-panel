"""Headless check: does every row of your layout (config.json and the auto-detected one) find a reading?

    python tools/check_layout.py                     # uses the running HWiNFO
    python tools/check_layout.py --readings x.json   # JSON list of reading dicts instead (testing)

Prints only row names and counts (no values).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
import hwsm  # noqa: E402
import i18n  # noqa: E402
import layout  # noqa: E402


def report(title, sections, rd):
    rows = layout.all_rows(sections)
    miss = [r.name for r in rows if not r.match(rd)]
    print(f"{title}: {len(sections)} sections, {len(rows)} rows, {len(rows) - len(miss)} matched, {len(miss)} unmatched")
    for m in miss:
        print("   unmatched:", m)
    return len(miss)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cfg, _ = config.load_config()
    i18n.set_language(cfg["language"])
    if "--readings" in sys.argv:
        with open(sys.argv[sys.argv.index("--readings") + 1], encoding="utf-8") as f:
            rd = json.load(f)
    else:
        try:
            rd = hwsm.read_all()
        except Exception as ex:
            print("Cannot read HWiNFO shared memory:", ex)
            return 1
    print(f"{len(rd)} readings")
    bad = 0
    if isinstance(cfg["sections"], list):
        bad += report("config.json layout", layout.build_sections(cfg["sections"]), rd)
    else:
        print("config.json layout: auto")
    auto = layout.build_sections(layout.autodetect(rd))
    bad += report("auto-detected layout", auto, rd)
    for s in auto:
        print(f"   [{s.title}] " + ", ".join(r.name for r in s.rows))
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
