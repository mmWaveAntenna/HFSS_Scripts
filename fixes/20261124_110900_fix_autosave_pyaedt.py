import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_OFF = '''    try:
        hfss.odesktop.SetRegistryInt("Desktop/Settings/ProjectOptions/EnableAutoSave", 0)
    except Exception:
        pass'''

NEW_OFF = '''    try:
        hfss.autosave_disable()
    except Exception:
        pass'''

OLD_ON = '''    try:
        hfss.odesktop.SetRegistryInt("Desktop/Settings/ProjectOptions/EnableAutoSave", 1)
    except Exception:
        pass'''

NEW_ON = '''    try:
        hfss.autosave_enable()
    except Exception:
        pass'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = text.replace(OLD_OFF, NEW_OFF).replace(OLD_ON, NEW_ON)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_110900_fix_autosave_pyaedt.py ===
