import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_STITCH_1 = '''    for pref, xc, y0, y1 in [
        ("THRU", "x_thru", -l_thru_v/2 + 2.1, l_thru_v/2 - 2.1), ("LINE", "x_line", -l_line_v/2 + 2.1, l_line_v/2 - 2.1),
        ("OPENA", "x_open", -y_res_v + 2.1, -y_res_v + l_ref_v + 0.5), ("OPENB", "x_open", y_res_v - l_ref_v - 0.5, y_res_v - 2.1),
        ("RES1", "x_res", -y_res_v + 2.1, -r_tab_v - 0.6), ("RES2", "x_res", r_tab_v + 0.6, y_res_v - 2.1),
    ]:
        n = max(1, int(abs(y1 - y0) / pitch_v))
        for i in range(n + 1):
            yv = y0 + (y1 - y0) * i / max(1, n)
            add_svia(f"SVia_{pref}_L_{i}", f"{xc} - (W/2 + gap_gnd + via_offset)", f"{yv:.4f}mm")
            add_svia(f"SVia_{pref}_R_{i}", f"{xc} + (W/2 + gap_gnd + via_offset)", f"{yv:.4f}mm")'''

NEW_STITCH_1 = '''    # Параметрическая расстановка via вдоль всех линий (двигаются за L_line, r_tab_out, y_top_res при смене f0_GHz)
    param_segments = [
        ("THRU", "x_thru", "-L_thru/2 + 2.1mm", "L_thru/2 - 2.1mm", abs(l_thru_v - 4.2)),
        ("LINE", "x_line", "-L_line/2 + 2.1mm", "L_line/2 - 2.1mm", abs(l_line_v - 4.2)),
        ("OPENA", "x_open", "-y_top_res + 2.1mm", "-y_top_res + L_ref + 0.5mm", abs(l_ref_v - 1.6)),
        ("OPENB", "x_open", "y_top_res - L_ref - 0.5mm", "y_top_res - 2.1mm", abs(l_ref_v - 1.6)),
        ("RES1", "x_res", "-y_top_res + 2.1mm", "-r_tab_out - 0.6mm", abs((y_res_v - 2.1) - (r_tab_v + 0.6))),
        ("RES2", "x_res", "r_tab_out + 0.6mm", "y_top_res - 2.1mm", abs((y_res_v - 2.1) - (r_tab_v + 0.6))),
    ]
    for pref, xc, y0_e, y1_e, span_v in param_segments:
        n = max(1, int(span_v / pitch_v))
        for i in range(n + 1):
            t = i / max(1, n)
            y_expr = f"({y0_e}) + ({t:.5f})*(({y1_e}) - ({y0_e}))"
            add_svia(f"SVia_{pref}_L_{i}", f"{xc} - (W/2 + gap_gnd + via_offset)", y_expr)
            add_svia(f"SVia_{pref}_R_{i}", f"{xc} + (W/2 + gap_gnd + via_offset)", y_expr)'''

OLD_STITCH_2 = '''    # Прошивка via второго резонатора (90°)
    n_f2 = max(1, int(abs((y_res_v - 2.1) - (r_tab_v + 0.6)) / pitch_v))
    for i in range(n_f2 + 1):
        dv = (r_tab_v + 0.6) + ((y_res_v - 2.1) - (r_tab_v + 0.6)) * i / max(1, n_f2)
        add_svia(f"SVia_R2B_L_{i}", "x_res2 - (W/2 + gap_gnd + via_offset)", f"-{dv:.4f}mm")
        add_svia(f"SVia_R2B_R_{i}", "x_res2 + (W/2 + gap_gnd + via_offset)", f"-{dv:.4f}mm")
        add_svia(f"SVia_R2R_B_{i}", f"x_res2 + {dv:.4f}mm", "-(W/2 + gap_gnd + via_offset)")
        add_svia(f"SVia_R2R_T_{i}", f"x_res2 + {dv:.4f}mm", "+(W/2 + gap_gnd + via_offset)")'''

NEW_STITCH_2 = '''    # Параметрическая прошивка via второго резонатора (90°, без унарного плюса по DL-15)
    n_f2 = max(1, int(abs((y_res_v - 2.1) - (r_tab_v + 0.6)) / pitch_v))
    for i in range(n_f2 + 1):
        t = i / max(1, n_f2)
        d_expr = f"(r_tab_out + 0.6mm) + ({t:.5f})*((y_top_res - 2.1mm) - (r_tab_out + 0.6mm))"
        add_svia(f"SVia_R2B_L_{i}", "x_res2 - (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2B_R_{i}", "x_res2 + (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2R_B_{i}", f"x_res2 + ({d_expr})", "-(W/2 + gap_gnd + via_offset)")
        add_svia(f"SVia_R2R_T_{i}", f"x_res2 + ({d_expr})", "W/2 + gap_gnd + via_offset")'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
assert OLD_STITCH_1 in text and OLD_STITCH_2 in text, "Якоря прошивки via не найдены!"
updated = text.replace(OLD_STITCH_1, NEW_STITCH_1, 1).replace(OLD_STITCH_2, NEW_STITCH_2, 1)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_124800_fix_unary_plus_and_param_vias.py ===
