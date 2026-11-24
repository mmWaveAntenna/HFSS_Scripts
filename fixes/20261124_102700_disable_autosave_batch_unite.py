import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_INIT = '''    hfss = Hfss(project="TRL_Calibration_FR4_FMCN1476", design="TRL_Kit", solution_type="DrivenModal", new_desktop=True)
    hfss.modeler.model_units = "mm"'''

NEW_INIT = '''    hfss = Hfss(project="TRL_Calibration_FR4_FMCN1476", design="TRL_Kit", solution_type="DrivenModal", new_desktop=True)
    hfss.modeler.model_units = "mm"
    try:
        hfss.odesktop.SetAutoSaveEnabled(False)
    except Exception:
        pass'''

OLD_UNITE = '''    hfss.modeler.unite(pools["gnd_metal"])'''

NEW_UNITE = '''    gnd_parts = pools["gnd_metal"]
    for i in range(1, len(gnd_parts), 50):
        hfss.modeler.unite([gnd_parts[0]] + gnd_parts[i:i + 50])'''

OLD_SAVE = '''    hfss.save_project()'''

NEW_SAVE = '''    try:
        hfss.odesktop.SetAutoSaveEnabled(True)
    except Exception:
        pass
    hfss.save_project()'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = text.replace(OLD_INIT, NEW_INIT).replace(OLD_UNITE, NEW_UNITE).replace(OLD_SAVE, NEW_SAVE)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_102700_disable_autosave_batch_unite.py ===
