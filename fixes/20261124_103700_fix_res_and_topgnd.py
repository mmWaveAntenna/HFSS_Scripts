# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_VARS = '''        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.2mm"), ("via_offset", "0.4mm"),'''
NEW_VARS = '''        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.0mm"), ("via_offset", "0.4mm"),'''

OLD_FEEDS = '''        ("RES_Feed_2", "x_res - W/2", "r_tab_out - 0.3mm", "L_feed + 0.3mm"), ("RES_Feed_1", "x_res - W/2", "-r_tab_out - L_feed", "L_feed + 0.3mm"),'''
NEW_FEEDS = '''        ("RES_Feed_2", "x_res - W/2", "r_tab_out - 0.05mm", "L_feed + 0.05mm"), ("RES_Feed_1", "x_res - W/2", "-r_tab_out - L_feed", "L_feed + 0.05mm"),'''

OLD_SLOTS = '''        ("Cut_RES_Feed", "x_res - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "2*y_top_res"),'''
NEW_SLOTS = '''        ("Cut_RES_1", "x_res - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "L_feed + gap_gnd"),
        ("Cut_RES_2", "x_res - W/2 - gap_gnd", "r_tab_out - gap_gnd", "W + 2*gap_gnd", "L_feed + gap_gnd"),'''

OLD_PAD_CLEAR = '''    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h"], sizes=["10.50mm", "6.24mm", "t_cu"], name=pad_name, material="copper")
    pools["gnd_metal"].append(pad_name)'''
NEW_PAD_CLEAR = '''    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h"], sizes=["10.50mm", "6.24mm", "t_cu"], name=pad_name, material="copper")
    pad_clr = f"PadVoid_{port_name}"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h - 0.01mm"], sizes=["10.50mm", "6.24mm", "t_cu + 0.02mm"], name=pad_clr, material="vacuum")
    pools["top_cuts"].append(pad_clr)
    pools["top_pads"].append(pad_name)'''

OLD_POOLS = '''    pools = {
        "gnd_metal": ["GND", "GND_TOP"], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],'''
NEW_POOLS = '''    pools = {
        "gnd_metal": ["GND", "GND_TOP"], "top_pads": [], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],'''
# --- Часть 2/2 ---
OLD_PHASE2_GND = '''    hfss.modeler.unite(pools["top_cuts"])
    hfss.modeler.subtract("GND_TOP", pools["top_cuts"], keep_originals=False)
    hfss.modeler.unite(pools["bot_cuts"])
    hfss.modeler.subtract("GND", pools["bot_cuts"], keep_originals=False)
    gnd_parts = pools["gnd_metal"]'''

NEW_PHASE2_GND = '''    hfss.modeler.unite(pools["top_cuts"])
    hfss.modeler.subtract("GND_TOP", pools["top_cuts"], keep_originals=False)
    hfss.modeler.unite(pools["bot_cuts"])
    hfss.modeler.subtract("GND", pools["bot_cuts"], keep_originals=False)
    gnd_parts = pools["gnd_metal"] + pools["top_pads"]'''

OLD_STITCH = '''    for pref, xc, y0, y1 in [
        ("THRU", "x_thru", -l_thru_v/2 + 2.2, l_thru_v/2 - 2.2), ("LINE", "x_line", -l_line_v/2 + 2.2, l_line_v/2 - 2.2),
        ("OPENA", "x_open", -y_res_v + 2.2, -y_res_v + l_ref_v + 0.5), ("OPENB", "x_open", y_res_v - l_ref_v - 0.5, y_res_v - 2.2),
        ("RES1", "x_res", -y_res_v + 2.2, -r_tab_v - 0.8), ("RES2", "x_res", r_tab_v + 0.8, y_res_v - 2.2),
    ]:'''

NEW_STITCH = '''    for pref, xc, y0, y1 in [
        ("THRU", "x_thru", -l_thru_v/2 + 2.1, l_thru_v/2 - 2.1), ("LINE", "x_line", -l_line_v/2 + 2.1, l_line_v/2 - 2.1),
        ("OPENA", "x_open", -y_res_v + 2.1, -y_res_v + l_ref_v + 0.5), ("OPENB", "x_open", y_res_v - l_ref_v - 0.5, y_res_v - 2.1),
        ("RES1", "x_res", -y_res_v + 2.1, -r_tab_v - 0.6), ("RES2", "x_res", r_tab_v + 0.6, y_res_v - 2.1),
    ]:'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace(OLD_VARS, NEW_VARS)
        .replace(OLD_FEEDS, NEW_FEEDS)
        .replace(OLD_SLOTS, NEW_SLOTS)
        .replace(OLD_PAD_CLEAR, NEW_PAD_CLEAR)
        .replace(OLD_POOLS, NEW_POOLS)
        .replace(OLD_PHASE2_GND, NEW_PHASE2_GND)
        .replace(OLD_STITCH, NEW_STITCH)
        .replace("for k in range(24):", "for k in range(40):")
        .replace("2.0 * math.pi * k / 24.0", "2.0 * math.pi * k / 40.0")
        .replace("for k in range(8):", "for k in range(16):")
        .replace("2.0 * math.pi * k / 8.0", "2.0 * math.pi * k / 16.0")
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_103700_fix_res_and_topgnd.py ===
