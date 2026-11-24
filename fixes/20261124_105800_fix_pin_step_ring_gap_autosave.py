# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_AUTOSAVE_1 = '''    try:
        hfss.odesktop.SetAutoSaveEnabled(False)
    except Exception:
        pass'''

NEW_AUTOSAVE_1 = '''    try:
        hfss.odesktop.SetRegistryInt("Desktop/Settings/ProjectOptions/EnableAutoSave", 0)
    except Exception:
        pass'''

OLD_AUTOSAVE_2 = '''    try:
        hfss.odesktop.SetAutoSaveEnabled(True)
    except Exception:
        pass'''

NEW_AUTOSAVE_2 = '''    try:
        hfss.odesktop.SetRegistryInt("Desktop/Settings/ProjectOptions/EnableAutoSave", 1)
    except Exception:
        pass'''

OLD_PIN = '''    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=diel_name, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.275mm", height="6.95mm", name=pin_air, material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"], radius="0.175mm", height="0.58mm", name=pin_pcb, material="copper")'''

NEW_PIN = '''    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=diel_name, material="vacuum")
    # Ступенька пина на высоте 0.28 мм — видна внутри бокового окна высотой 0.55 мм (DETAIL A)
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.28mm"], radius="0.275mm", height="7.22mm", name=pin_air, material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"], radius="0.175mm", height="0.31mm", name=pin_pcb, material="copper")'''
# --- Часть 2/2 ---
OLD_RING_CUT_1 = '''    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_RingOut", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_RingIn", material="vacuum")'''

NEW_RING_CUT_1 = '''    # Облегающий вырез отдельно вокруг кольца (r_out + gap_gnd) и отдельно вокруг T-лапок (r_tab_out + gap_gnd)
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_RingOut", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_RingIn", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_TabArc", material="vacuum")
    hfss.modeler.create_box(origin=["x_res - W_tab/2 - gap_gnd", "-r_tab_out - gap_gnd - 0.5mm", "h - 0.01mm"], sizes=["W_tab + 2*gap_gnd", "2*(r_tab_out + gap_gnd) + 1.0mm", "t_cu + 0.02mm"], name="Cut_TabBox", material="vacuum")'''

OLD_RING_CUT_2 = '''    hfss.modeler.subtract("Cut_RingOut", "Cut_RingIn", keep_originals=False)
    pools["top_cuts"].append("Cut_RingOut")'''

NEW_RING_CUT_2 = '''    hfss.modeler.intersect(["Cut_TabBox", "Cut_TabArc"], keep_originals=False)
    hfss.modeler.unite(["Cut_RingOut", "Cut_TabBox"])
    hfss.modeler.subtract("Cut_RingOut", "Cut_RingIn", keep_originals=False)
    pools["top_cuts"].append("Cut_RingOut")'''

OLD_RING_VIAS = '''        if abs(math.cos(ang)) > 0.25:
            add_svia(f"SVia_RO_{k}", f"x_res + ({math.cos(ang):.5f})*(r_tab_out + gap_gnd + via_offset)", f"({math.sin(ang):.5f})*(r_tab_out + gap_gnd + via_offset)")'''

NEW_RING_VIAS = '''        if abs(math.cos(ang)) > 0.38:
            add_svia(f"SVia_RO_{k}", f"x_res + ({math.cos(ang):.5f})*(r_out + gap_gnd + via_offset)", f"({math.sin(ang):.5f})*(r_out + gap_gnd + via_offset)")'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace(OLD_AUTOSAVE_1, NEW_AUTOSAVE_1)
        .replace(OLD_AUTOSAVE_2, NEW_AUTOSAVE_2)
        .replace(OLD_PIN, NEW_PIN)
        .replace(OLD_RING_CUT_1, NEW_RING_CUT_1)
        .replace(OLD_RING_CUT_2, NEW_RING_CUT_2)
        .replace(OLD_RING_VIAS, NEW_RING_VIAS)
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_105800_fix_pin_step_ring_gap_autosave.py ===
