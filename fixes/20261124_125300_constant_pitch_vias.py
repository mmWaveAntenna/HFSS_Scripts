# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_VARS = '''        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.0mm"), ("via_offset", "0.4mm"),'''
NEW_VARS = '''        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.0mm"), ("via_offset", "0.4mm"),
        ("r_via_out", "r_out + gap_gnd + via_offset"),
        ("r_via_in", "max(r_in - gap_gnd - via_offset, 0.25mm)"),
        ("phi_guard", "asin(min((W/2 + gap_gnd + via_offset) / r_via_out, 0.95))"),'''

OLD_STITCH_ALL = '''    # Параметрическая расстановка via вдоль всех линий (двигаются за L_line, r_tab_out, y_top_res при смене f0_GHz)
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
            add_svia(f"SVia_{pref}_R_{i}", f"{xc} + (W/2 + gap_gnd + via_offset)", y_expr)

    # Прошивка торцов разомкнутых линий OPEN_A и OPEN_B (по 2 via за торцом с отступом via_offset >= 200 мкм от края меди)
    for s_lbl, s_sgn in [("L", "-"), ("R", "+")]:
        add_svia(f"SVia_OPENA_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "-y_top_res + L_ref + gap_gnd + via_offset")
        add_svia(f"SVia_OPENB_End_{s_lbl}", f"x_open {s_sgn} 0.25mm", "y_top_res - L_ref - gap_gnd - via_offset")

    for k in range(40):
        ang = 2.0 * math.pi * k / 40.0
        ca, sa = math.cos(ang), math.sin(ang)
        if abs(math.cos(ang)) > 0.38:
            add_svia(f"SVia_RO_{k}", f"x_res + ({ca:.5f})*(r_out + gap_gnd + via_offset)", f"({sa:.5f})*(r_out + gap_gnd + via_offset)")
    add_svia("SVia_RC", "x_res", "0mm")
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        add_svia(f"SVia_RI_{k}", f"x_res + ({math.cos(ang):.5f})*(r_in - gap_gnd - via_offset)", f"({math.sin(ang):.5f})*(r_in - gap_gnd - via_offset)")

    # Параметрическая прошивка via второго резонатора (90°, без унарного плюса по DL-15)
    n_f2 = max(1, int(abs((y_res_v - 2.1) - (r_tab_v + 0.6)) / pitch_v))
    for i in range(n_f2 + 1):
        t = i / max(1, n_f2)
        d_expr = f"(r_tab_out + 0.6mm) + ({t:.5f})*((y_top_res - 2.1mm) - (r_tab_out + 0.6mm))"
        add_svia(f"SVia_R2B_L_{i}", "x_res2 - (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2B_R_{i}", "x_res2 + (W/2 + gap_gnd + via_offset)", f"-({d_expr})")
        add_svia(f"SVia_R2R_B_{i}", f"x_res2 + ({d_expr})", "-(W/2 + gap_gnd + via_offset)")
        add_svia(f"SVia_R2R_T_{i}", f"x_res2 + ({d_expr})", "W/2 + gap_gnd + via_offset")
    for k in range(40):
        ang = 2.0 * math.pi * k / 40.0
        ca, sa = math.cos(ang), math.sin(ang)
        if not ((sa < -0.92 and abs(ca) < 0.38) or (ca > 0.92 and abs(sa) < 0.38)):
            add_svia(f"SVia_R2O_{k}", f"x_res2 + ({ca:.5f})*(r_out + gap_gnd + via_offset)", f"({sa:.5f})*(r_out + gap_gnd + via_offset)")
    add_svia("SVia_R2C", "x_res2", "0mm")
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        add_svia(f"SVia_R2I_{k}", f"x_res2 + ({math.cos(ang):.5f})*(r_in - gap_gnd - via_offset)", f"({math.sin(ang):.5f})*(r_in - gap_gnd - via_offset)")'''
# --- Часть 2/2 ---
NEW_STITCH_ALL = '''    # Постоянный шаг via_pitch (1.0 мм) при изменении f0_GHz / радиуса (запас 2.5x через min(..., end))
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
    # Резонатор 1: 2 дуги по ~pi между верхним и нижним фидерами + внутренний островок
    stitch_arc("R1_R", "x_res", "r_via_out", "-pi/2 + phi_guard", "pi/2 - phi_guard", math.pi * r_out_v)
    stitch_arc("R1_L", "x_res", "r_via_out", "pi/2 + phi_guard", "3*pi/2 - phi_guard", math.pi * r_out_v)
    add_svia("SVia_RC", "x_res", "0mm")
    stitch_arc("R1_I", "x_res", "r_via_in", "0", "2*pi", 2 * math.pi * r_in_v)

    # Резонатор 2 (90°): фидеры по -Y и +X, малый сектор pi/2 и большой сектор 3*pi/2
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
    stitch_arc("R2_I", "x_res2", "r_via_in", "0", "2*pi", 2 * math.pi * r_in_v)'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
assert OLD_VARS in text and OLD_STITCH_ALL in text, "Якоря прошивки via не найдены!"
updated = text.replace(OLD_VARS, NEW_VARS, 1).replace(OLD_STITCH_ALL, NEW_STITCH_ALL, 1)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_125300_constant_pitch_vias.py ===
