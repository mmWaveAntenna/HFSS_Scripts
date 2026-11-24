import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_TOPPAD = '''    pad_name = f"TopPad_{port_name}"
    if dir_y > 0:
        pad_y0, notch_y0, chan_y0 = f"({y_expr}) - 4.29mm", f"({y_expr}) + 1.00mm", f"({y_expr})"
    else:
        pad_y0, notch_y0, chan_y0 = f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.00mm"

    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h"], sizes=["10.50mm", "6.24mm", "t_cu"], name=pad_name, material="copper")
    pad_clr = f"PadVoid_{port_name}"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h - 0.01mm"], sizes=["10.50mm", "6.24mm", "t_cu + 0.02mm"], name=pad_clr, material="vacuum")
    pools["top_cuts"].append(pad_clr)
    pools["top_pads"].append(pad_name)'''

NEW_TOPPAD = '''    if dir_y > 0:
        notch_y0, chan_y0 = f"({y_expr}) + 1.00mm", f"({y_expr})"
    else:
        notch_y0, chan_y0 = f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.00mm"'''

OLD_POOLS = '''        "gnd_metal": ["GND", "GND_TOP"], "top_pads": [], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],'''
NEW_POOLS = '''        "gnd_metal": ["GND", "GND_TOP"], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],'''

OLD_GND_PARTS = '''    gnd_parts = pools["gnd_metal"] + pools["top_pads"]'''
NEW_GND_PARTS = '''    gnd_parts = pools["gnd_metal"]'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace(OLD_TOPPAD, NEW_TOPPAD)
        .replace(OLD_POOLS, NEW_POOLS)
        .replace(OLD_GND_PARTS, NEW_GND_PARTS)
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_110100_remove_toppad_cut_gnd_top.py ===
