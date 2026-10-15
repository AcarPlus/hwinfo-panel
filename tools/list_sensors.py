"""Print every sensor / reading of the data source (HWiNFO shared memory, LibreHardwareMonitor or built-in).

Use it to find the ORIGINAL (English) names for the regexes in config.json:
    python tools/list_sensors.py                      # everything, data source from config.json
    python tools/list_sensors.py gpu fan              # only lines containing all words (case-insensitive)
    python tools/list_sensors.py --backend builtin    # or hwinfo / lhm / auto

Output columns: sensor (orig) | label (orig) | type | unit | value
(The output may contain serial numbers / device names: do not paste it into public places.)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend  # noqa: E402
import config  # noqa: E402
import hwsm  # noqa: E402


def main():
    args = sys.argv[1:]
    name = backend.cli_backend(args)
    if name:
        i = args.index("--backend")
        del args[i:i + 2]
    words = [w.lower() for w in args]
    cfg, _ = config.load_config()
    try:
        src, rd = backend.read_once(cfg, name)
    except Exception as ex:
        print("Cannot read sensor data:", ex)
        print("HWiNFO: start HWiNFO64 and enable Settings -> 'Shared Memory Support' (sensors window).")
        print("LibreHardwareMonitor: Options -> Remote Web Server -> Run.")
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
