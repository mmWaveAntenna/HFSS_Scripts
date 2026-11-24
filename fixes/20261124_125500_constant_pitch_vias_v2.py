import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

NEW_STITCH_BLOCK = '''    # Постоянный шаг via_pitch (1.0 мм) при изменении f0_GHz / радиуса (запас 2.5x через min(..., end))
    for pref, xc, y0_e, y1_e, span_v in [
        ("THRU", "x_thru", "-L_thru/2 + 2.1mm", "L_thru/2 - 2.1mm", abs(l_thru_v - 4.2)),
        ("LINE", "x_line", "-L_line/2 + 2.1mm", "L_line/2 - 2.1mm", abs(l_line_v - 4.2)),
        ("OPENA", "x_open", "-y_top_res + 2.1mm", "-y_top_res + L_ref + 0.5mm", abs(l_ref_v - 1.6)),
        ("OPENB", "x_open", "y_top_res - L_ref - 0.5mm", "y_top_res - 2.1mm", abs(l_ref_v - 1.6)),
        ("RES1", "x_res", "-y_top_res + 2.1mm", "-r_tab_out - 0.6mm", abs((y_res_v - 2.1) - (r_tab_v + 0.6))),
        ("RES2", "x_res", "r_tab_out + 0.6mm", "y_top_res - 2.1mm", abs((y_res_v - 2.1) - (r_tab_v + 0.6))),
    ]:
        n_max = max(2, int(2.5 * span_v / pitch_v) + 1)
        for i in range(n_max + 1):
            y_expr = f"min(({y0_e}) + {i}*via_pitch, {y1_e})"
            add_svia(f"SVia_{pref}_L_{i}", f"{xc} - (W/2 + gap_gnd + via_offset)", y_expr)
            add_svia(f"SVia_{pref}_R_{i}", f"{xc} + (W/2 + gap_gnd + via_offset)", y_expr)

    for s_lbl, s_sgn in [("L", "-"), ("R", "+")]:
        add_svia(f"SVia_OPENA_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "-y_top_res + L_ref + gap_gnd + via_offset")
        add_svia(f"SVia_OPENB_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "y_top_res - L_ref - gap_gnd - via_offset")

    def stitch_arc(prefix, xc_e, r_e, a_start_e, a_end_e, max_arc_mm):
        n_arc = max(2, int(2.5 * max_arc_mm / pitch_v) + 1)
        for k in range(n_arc + 1):
            phi_e = f"min(({a_start_e}) + ({k}*via_pitch)/({r_e}), {a_end_e})"
            add_svia(f"SVia_{prefix}_{k}", f"{xc_e} + ({r_e})*cos({phi_e})", f"({r_e})*sin({phi_e})")

    r_out_v = hfss.get_evaluated_value("r_via_out") * 1000.0
    r_in_v = hfss.get_evaluated_value("r_via_in") * 1000.0
    stitch_arc("R1_R", "x_res", "r_via_out", "-pi/2 + phi_guard", "pi/2 - phi_guard", math.pi * r_out_v)
    stitch_arc("R1_L", "x_res", "r_via_out", "pi/2 + phi_guard", "3*pi/2 - phi_guard", math.pi * r_out_v)
    add_svia("SVia_RC", "x_res", "0mm")
    stitch_arc("R1_I", "x_res", "r_via_in", "0", "2*pi", 2 * math.pi * r_in_v)

    n_f2_max = max(2, int(2.5 * abs((y_res_v - 2.1) - (r_tab_v + 0.6)) / pitch_v) + 1)
    for i in range(n_f2_max + 1):
        d_expr = f"min((r_tab_out + 0.6mm) + {i}*via_pitch, y_top_res - 2.1mm)"
        add_svia(f"SVia_R2B_L_{i}", "x_res2 - (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2B_R_{i}", "x_res2 + (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2R_B_{i}", f"x_res2 + ({d_expr})", "-(W/2 + gap_gnd + via_offset)")
        add_svia(f"SVia_R2R_T_{i}", f"x_res2 + ({d_expr})", "W/2 + gap_gnd + via_offset")
    stitch_arc("R2_Q4", "x_res2", "r_via_out", "-pi/2 + phi_guard", "-phi_guard", 0.5 * math.pi * r_out_v)
    stitch_arc("R2_BIG", "x_res2", "r_via_out", "phi_guard", "3*pi/2 - phi_guard", 1.5 * math.pi * r_out_v)
    add_svia("SVia_R2C", "x_res2", "0mm")
    stitch_arc("R2_I", "x_res2", "r_via_in", "0", "2*pi", 2 * math.pi * r_in_v)

'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())

var_anchor = '("via_offset", "0.4mm"),'
assert var_anchor in text, "Якорь via_offset не найден!"
if '"r_via_out"' not in text:
    text = text.replace(
        var_anchor,
        var_anchor + '\n        ("r_via_out", "r_out + gap_gnd + via_offset"), ("r_via_in", "max(r_in - gap_gnd - via_offset, 0.25mm)"), ("phi_guard", "asin(min((W/2 + gap_gnd + via_offset) / r_via_out, 0.95))"),',
        1,
    )

start_marker = "    param_segments = [" if "    param_segments = [" in text else "    for pref, xc, y0, y1 in ["
end_marker = "    # === ФАЗА 2: ПАКЕТНЫЕ БУЛЕВЫ ОПЕРАЦИИ И ПОРТЫ ==="
assert start_marker in text and end_marker in text, f"Не найдены границы блока: {start_marker!r} / {end_marker!r}"

i0 = text.index(start_marker)
i1 = text.index(end_marker)
updated = text[:i0] + NEW_STITCH_BLOCK + text[i1:]

ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_125500_constant_pitch_vias_v2.py ===
