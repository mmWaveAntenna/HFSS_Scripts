import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

ANCHOR = '''    for k in range(40):'''

INSERT_OPEN_VIAS = '''    # Прошивка торцов разомкнутых линий OPEN_A и OPEN_B (по 2 via за торцом с отступом via_offset >= 200 мкм от края меди)
    for s_lbl, s_sgn in [("L", "-"), ("R", "+")]:
        add_svia(f"SVia_OPENA_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "-y_top_res + L_ref + gap_gnd + via_offset")
        add_svia(f"SVia_OPENB_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "y_top_res - L_ref - gap_gnd - via_offset")

    for k in range(40):'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
assert ANCHOR in text, "Якорь 'for k in range(40):' не найден в файле!"
if "SVia_OPENA_End_L" not in text:
    updated = text.replace(ANCHOR, INSERT_OPEN_VIAS, 1)
    ast.parse(updated)
    TARGET.write_text(updated, encoding="utf-8")
    new_count = len(updated.splitlines())
    print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
else:
    print(f"[{ts} MSK] {TARGET.name}: торцевые via уже присутствуют.")
# === fixes/20261124_121000_fix_open_end_vias_anchor.py ===
