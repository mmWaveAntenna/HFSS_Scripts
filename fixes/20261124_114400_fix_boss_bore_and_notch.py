import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_NOTCH = '''    for cname, orig, sz in [
        (f"Notch_{port_name}", [f"({x_expr}) - 1.20mm", notch_y0, "h - 0.01mm"], ["2.40mm", "0.95mm", "t_cu + 0.02mm"]),
        (f"Chan_{port_name}", [f"({x_expr}) - W/2 - 0.43mm", chan_y0, "h - 0.01mm"], ["W + 0.86mm", "1.00mm", "t_cu + 0.02mm"]),
    ]:'''

NEW_NOTCH = '''    # Входной вырез Notch продолжается с той же шириной зазора от полоска (W + 2*gap_gnd)
    for cname, orig, sz in [
        (f"Notch_{port_name}", [f"({x_expr}) - W/2 - gap_gnd", notch_y0, "h - 0.01mm"], ["W + 2*gap_gnd", "0.95mm", "t_cu + 0.02mm"]),
        (f"Chan_{port_name}", [f"({x_expr}) - W/2 - 0.43mm", chan_y0, "h - 0.01mm"], ["W + 0.86mm", "1.00mm", "t_cu + 0.02mm"]),
    ]:'''

OLD_BOSS = '''    boss_name, barrel_name, win_cut = f"Coax_Boss_{port_name}", f"Coax_Barrel_{port_name}", f"BossWindow_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu"], radius="1.75mm", height="0.60mm", name=boss_name, material="pec")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="2.26mm", height="6.95mm", name=barrel_name, material="pec")
    win_y0 = f"({y_expr})" if dir_y > 0 else f"({y_expr}) - 1.90mm"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 0.75mm", win_y0, "h + t_cu - 0.01mm"], sizes=["1.50mm", "1.90mm", "0.56mm"], name=win_cut, material="vacuum")'''

NEW_BOSS = '''    boss_name, barrel_name, win_cut, boss_bore = f"Coax_Boss_{port_name}", f"Coax_Barrel_{port_name}", f"BossWindow_{port_name}", f"BossBore_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu"], radius="1.75mm", height="0.60mm", name=boss_name, material="pec")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="2.26mm", height="6.95mm", name=barrel_name, material="pec")
    win_y0 = f"({y_expr})" if dir_y > 0 else f"({y_expr}) - 1.90mm"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 0.75mm", win_y0, "h + t_cu - 0.01mm"], sizes=["1.50mm", "1.90mm", "0.56mm"], name=win_cut, material="vacuum")
    # Центральный цилиндрический вырез Ø 1.27 мм (R = 0.635 мм) во втулке вокруг пина (исключает КЗ задней стенки втулки на пин)
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.01mm"], radius="0.635mm", height="0.57mm", name=boss_bore, material="vacuum")
    hfss.modeler.unite([win_cut, boss_bore])'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = text.replace(OLD_NOTCH, NEW_NOTCH).replace(OLD_BOSS, NEW_BOSS)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_114400_fix_boss_bore_and_notch.py ===
