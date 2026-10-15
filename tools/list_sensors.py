"""Print every HWiNFO sensor / reading found in shared memory.

Use it to find the ORIGINAL (English) names for the regexes in config.json:
    python tools/list_sensors.py            # everything
    python tools/list_sensors.py gpu fan    # only lines containing all words (case-insensitive)

Output columns: sensor (orig) | label (orig) | type | unit | value
(The output may contain serial numbers / device names: do not paste it into public places.)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hwsm  # noqa: E402


def main():
    words = [w.lower() for w in sys.argv[1:]]
    try:
        rd = hwsm.read_all()
    except Exception as ex:
        print("Cannot read HWiNFO shared memory:", ex)
        print("Start HWiNFO64 and enable Settings -> 'Shared Memory Support' (sensors window).")
        return 1
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    last = None
    n = 0
    for r in rd:
        tname = hwsm.TYPE_NAMES.get(r["type"], str(r["type"]))
        line = f"{r['sensor']} | {r['label']} | {r['type']}({tname}) | {r['unit']} | {r['value']:.2f}"
        if words and not all(w in line.lower() for w in words):
            continue
        if r["sensor"] != last:
            print()
            last = r["sensor"]
        print(line)
        n += 1
    print(f"\n{n} readings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
