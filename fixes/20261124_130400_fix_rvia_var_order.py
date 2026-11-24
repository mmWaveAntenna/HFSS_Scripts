import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

BAD_BLOCK = '\n        ("r_via_out", "r_out + gap_gnd + via_offset"), ("r_via_in", "max(r_in - gap_gnd - via_offset, 0.25mm)"), ("phi_guard", "asin(min((W/2 + gap_gnd + via_offset) / r_via_out, 0.95))"),'

AFTER_RIN_ANCHOR = '("r_out", "r_mean + W_ring/2"), ("r_in", "r_mean - W_ring/2"),'
GOOD_BLOCK = (
    AFTER_RIN_ANCHOR
    + '\n        ("r_via_out", "r_out + gap_gnd + via_offset"),'
    + '\n        ("r_via_in", "max(r_in - gap_gnd - via_offset, 0.25mm)"),'
    + '\n        ("phi_guard", "asin(min((W/2 + gap_gnd + via_offset) / r_via_out, 0.95))"),'
)

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
assert AFTER_RIN_ANCHOR in text, "Якорь r_out / r_in не найден!"

updated = text.replace(BAD_BLOCK, "").replace(AFTER_RIN_ANCHOR, GOOD_BLOCK, 1)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_130400_fix_rvia_var_order.py ===
