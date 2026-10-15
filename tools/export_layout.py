"""Write the auto-detected layout into config.json so you can edit it by hand ("sections" for HWiNFO,
"sections_lhm" / "sections_builtin" for the other data sources).

    python tools/export_layout.py            # refuses to overwrite an existing explicit layout
    python tools/export_layout.py --force
    python tools/export_layout.py --backend builtin   # or hwinfo / lhm / auto (default: config.json "backend")

Uses the data source and the language set in config.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend  # noqa: E402
import config  # noqa: E402
import i18n  # noqa: E402
import layout  # noqa: E402


def main():
    cfg, _ = config.load_config()
    i18n.set_language(cfg["language"])
    try:
        name, rd = backend.read_once(cfg, backend.cli_backend(sys.argv))
    except Exception as ex:
        print("Cannot read sensor data:", ex)
        return 1
    key = config.layout_key(name)
    if isinstance(cfg.get(key), list) and "--force" not in sys.argv:
        print(f"config.json already has an explicit '{key}' list. Use --force to replace it.")
        return 1
    secs = layout.autodetect(rd)
    path = config.config_path()
    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = json.load(f)
    except Exception:
        raw = dict(config.DEFAULTS)
    raw[key] = secs
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {sum(len(s['rows']) for s in secs)} rows in {len(secs)} sections ('{key}') to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
