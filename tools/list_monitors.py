"""Print the monitors Windows reports: use the index as "monitor" in config.json."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import config  # noqa: E402

mons = config.monitors()
auto = config.pick_monitor("auto", mons)
for m in mons:
    kind = "portrait" if m["h"] > m["w"] else "landscape"
    flags = (" primary" if m["primary"] else "") + ('  <- used by "auto"' if auto and m["index"] == auto["index"] else "")
    print(f"{m['index']}: {m['w']}x{m['h']} at ({m['x']},{m['y']}) {kind}{flags}")
if not mons:
    print("No monitors found.")
