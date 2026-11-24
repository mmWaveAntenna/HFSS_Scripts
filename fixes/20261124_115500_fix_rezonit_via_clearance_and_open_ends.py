import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_FM_VIAS = '''    via_coords = [(-0.80, 1.45*dir_y), (0.80, 1.45*dir_y), (-0.80, 0.90*dir_y), (0.80, 0.90*dir_y), (-0.80, 0.35*dir_y), (0.80, 0.35*dir_y)]
    for deg in (-15.0, -45.0, -75.0, -105.0, -135.0, -165.0):
        rad = math.radians(deg)
        via_coords.append((round(0.82 * math.cos(rad), 4), round(0.82 * math.sin(rad) * dir_y, 4)))'''

NEW_FM_VIAS = '''    # Отступ центра via от края меди >= 0.35 мм (край отверстия Ø 0.25 мм -> >= 225 мкм по нормам Резонит)
    via_coords = [(-0.95, 1.45*dir_y), (0.95, 1.45*dir_y), (-0.95, 0.90*dir_y), (0.95, 0.90*dir_y), (-0.95, 0.35*dir_y), (0.95, 0.35*dir_y)]
    for deg in (-15.0, -45.0, -75.0, -105.0, -135.0, -165.0):
        rad = math.radians(deg)
        via_coords.append((round(0.90 * math.cos(rad), 4), round(0.90 * math.sin(rad) * dir_y, 4)))'''

OLD_OPEN_STITCH = '''    for k in range(24):'''

NEW_OPEN_STITCH = '''    # Прошивка торцов разомкнутых линий OPEN_A и OPEN_B (по 2 via за торцом с отступом via_offset >= 200 мкм от края меди)
    for s_lbl, s_sgn in [("L", "-"), ("R", "+")]:
        add_svia(f"SVia_OPENA_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "-y_top_res + L_ref + gap_gnd + via_offset")
        add_svia(f"SVia_OPENB_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "y_top_res - L_ref - gap_gnd - via_offset")

    for k in range(24):'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = text.replace(OLD_FM_VIAS, NEW_FM_VIAS).replace(OLD_OPEN_STITCH, NEW_OPEN_STITCH)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_115500_fix_rezonit_via_clearance_and_open_ends.py ===
