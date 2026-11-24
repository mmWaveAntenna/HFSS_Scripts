# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

VARS_OLD = '''    hfss["bot_cut_dia"] = "0.96mm"'''
VARS_NEW = '''    hfss["bot_cut_dia"] = "0.96mm"
    hfss["gap_gnd"] = "0.5mm"
    hfss["via_dia"] = "0.25mm"
    hfss["via_pitch"] = "1.2mm"
    hfss["via_offset"] = "0.4mm"'''

SUB_OLD = '''    # Подложка и нижняя земля
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 10mm", "-t_cu"],
        sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"],
        name="GND", material="copper"
    )
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 10mm", "0mm"],
        sizes=["x_res + 20mm", "2*y_top_res + 20mm", "h"],
        name="Substrate", material="FR4_epoxy"
    )'''

SUB_NEW = SUB_OLD + '''
    # Сплошная земля верхнего слоя (с вырезами под линии, резонатор и футпринты FMCN1476)
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 10mm", "h"],
        sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"],
        name="GND_TOP", material="copper"
    )'''

SHIELD_HELPER = '''
def build_top_ground_shield(hfss):
    """Формирует вырезы в GND_TOP с отступом gap_gnd и прошивает экран земляными via."""
    cuts = []
    # 1. Каналы вдоль THRU, LINE, OPEN_A и OPEN_B (с отступом gap_gnd от торцов OPEN)
    trl_slots = [
        ("Cut_THRU", "x_thru - W/2 - gap_gnd", "-L_thru/2", "W + 2*gap_gnd", "L_thru"),
        ("Cut_LINE", "x_line - W/2 - gap_gnd", "-L_line/2", "W + 2*gap_gnd", "L_line"),
        ("Cut_OPEN_A", "x_open - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "L_ref + gap_gnd"),
        ("Cut_OPEN_B", "x_open - W/2 - gap_gnd", "y_top_res - L_ref - gap_gnd", "W + 2*gap_gnd", "L_ref + gap_gnd"),
        ("Cut_RES_Feed", "x_res - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "2*y_top_res"),
    ]
    for cname, x0, y0, dx, dy in trl_slots:
        hfss.modeler.create_box(origin=[x0, y0, "h - 0.01mm"], sizes=[dx, dy, "t_cu + 0.02mm"], name=cname, material="vacuum")
        cuts.append(cname)

    # 2. Кольцевой вырез вокруг резонатора и T-лапок (оставляет островок земли внутри r_in - gap_gnd)
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_RingOut", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_RingIn", material="vacuum")
    hfss.modeler.subtract("Cut_RingOut", "Cut_RingIn", keep_originals=False)
    cuts.append("Cut_RingOut")

    for c in cuts:
        hfss.modeler.subtract("GND_TOP", c, keep_originals=False)
'''
# --- Часть 2/2 ---
SHIELD_VIAS = '''
    # 3. Прошивка земляными via вдоль линий и вокруг/внутри резонатора (HFSS-выражения для параметризации)
    vias = []
    l_thru_v = hfss.get_evaluated_value("L_thru") * 1000.0
    l_line_v = hfss.get_evaluated_value("L_line") * 1000.0
    l_ref_v = hfss.get_evaluated_value("L_ref") * 1000.0
    y_res_v = hfss.get_evaluated_value("y_top_res") * 1000.0
    r_tab_v = hfss.get_evaluated_value("r_tab_out") * 1000.0
    r_in_v = hfss.get_evaluated_value("r_in") * 1000.0
    pitch_v = hfss.get_evaluated_value("via_pitch") * 1000.0

    def add_via(vname, vx_expr, vy_expr):
        hfss.modeler.create_cylinder(
            orientation="Z", origin=[vx_expr, vy_expr, "-t_cu"],
            radius="via_dia/2", height="h + 2*t_cu", name=vname, material="copper"
        )
        vias.append(vname)

    def stitch_line(prefix, x_c, y_start, y_end):
        n = max(1, int(abs(y_end - y_start) / pitch_v))
        for i in range(n + 1):
            yv = y_start + (y_end - y_start) * i / max(1, n)
            for s_lbl, s_sgn in [("L", "-"), ("R", "+")]:
                add_via(f"SVia_{prefix}_{s_lbl}_{i}", f"{x_c} {s_sgn} (W/2 + gap_gnd + via_offset)", f"{yv:.4f}mm")

    stitch_line("THRU", "x_thru", -l_thru_v / 2.0 + 2.2, l_thru_v / 2.0 - 2.2)
    stitch_line("LINE", "x_line", -l_line_v / 2.0 + 2.2, l_line_v / 2.0 - 2.2)
    stitch_line("OPENA", "x_open", -y_res_v + 2.2, -y_res_v + l_ref_v + 0.5)
    stitch_line("OPENB", "x_open", y_res_v - l_ref_v - 0.5, y_res_v - 2.2)
    stitch_line("RES1", "x_res", -y_res_v + 2.2, -r_tab_v - 0.8)
    stitch_line("RES2", "x_res", r_tab_v + 0.8, y_res_v - 2.2)

    # Периметр вокруг резонатора и островок земли внутри кольца
    n_arc = max(12, int(2 * math.pi * (r_tab_v + 0.9) / pitch_v))
    for k in range(n_arc):
        ang = 2.0 * math.pi * k / n_arc
        ca, sa = math.cos(ang), math.sin(ang)
        if abs(ca) > 0.25:  # не заходим в подводящие фидеры
            add_via(f"SVia_RingOut_{k}", f"x_res + ({ca:.5f})*(r_tab_out + gap_gnd + via_offset)", f"({sa:.5f})*(r_tab_out + gap_gnd + via_offset)")
    add_via("SVia_RingCenter", "x_res", "0mm")
    if r_in_v > 1.8:
        for k in range(8):
            ang = 2.0 * math.pi * k / 8.0
            add_via(f"SVia_RingIn_{k}", f"x_res + ({math.cos(ang):.5f})*(r_in - gap_gnd - via_offset)", f"({math.sin(ang):.5f})*(r_in - gap_gnd - via_offset)")

    hfss.modeler.unite(["GND", "GND_TOP"] + vias)
'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace(VARS_OLD, VARS_NEW)
        .replace(SUB_OLD, SUB_NEW)
        .replace('hfss.modeler.subtract(["Substrate", "GND", pad_name], hole_name', 'hfss.modeler.subtract(["Substrate", "GND", "GND_TOP", pad_name], hole_name')
        .replace("def main():", SHIELD_HELPER + SHIELD_VIAS + "\n\ndef main():")
        .replace("    # Open Region + Radiation Boundary", "    build_top_ground_shield(hfss)\n\n    # Open Region + Radiation Boundary")
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_100600_add_top_gnd_shield_vias.py ===
