# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

PART_1 = '''# -*- coding: utf-8 -*-
"""Генератор TRL + кольцевой резонатор с разъёмами FMCN1476 и верхним экраном GND_TOP.
Архитектура: Фаза 1 (создание всех примитивов) -> Фаза 2 (пакетные булевы операции для чистого дерева истории).
"""
import math
try:
    from pyaedt import Hfss
except ImportError:
    from ansys.aedt.core import Hfss


def queue_fmcn1476(hfss, x_expr, y_expr, dir_y, line_obj, port_name, pools):
    """Создаёт примитивы разъёма FMCN1476 и регистрирует их в булевых пулах pools."""
    z_port = "h + t_cu + 7.5mm"
    pad_name = f"TopPad_{port_name}"
    if dir_y > 0:
        pad_y0, notch_y0, chan_y0 = f"({y_expr}) - 4.29mm", f"({y_expr}) + 1.00mm", f"({y_expr})"
    else:
        pad_y0, notch_y0, chan_y0 = f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.00mm"

    hfss.modeler.create_box(origin=[f"({x_expr}) - 5.25mm", pad_y0, "h"], sizes=["10.50mm", "6.24mm", "t_cu"], name=pad_name, material="copper")
    pools["gnd_metal"].append(pad_name)

    for cname, orig, sz in [
        (f"Notch_{port_name}", [f"({x_expr}) - 1.20mm", notch_y0, "h - 0.01mm"], ["2.40mm", "0.95mm", "t_cu + 0.02mm"]),
        (f"Chan_{port_name}", [f"({x_expr}) - W/2 - 0.43mm", chan_y0, "h - 0.01mm"], ["W + 0.86mm", "1.00mm", "t_cu + 0.02mm"]),
    ]:
        hfss.modeler.create_box(origin=orig, sizes=sz, name=cname, material="vacuum")
        pools["top_cuts"].append(cname)

    pin_clear = f"PinClear_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h - 0.01mm"], radius="0.50mm", height="t_cu + 0.02mm", name=pin_clear, material="vacuum")
    pools["top_cuts"].append(pin_clear)

    line_pad = f"LinePad_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h"], radius="0.28mm", height="t_cu", name=line_pad, material="copper")
    pools["sig_groups"][line_obj].append(line_pad)

    for side, sign in [("L", -1), ("R", 1)]:
        hole_name = f"MntHole_{port_name}_{side}"
        hfss.modeler.create_cylinder(orientation="Z", origin=[f"({x_expr}) + ({sign}*3.58mm)", y_expr, "-t_cu - 0.1mm"], radius="0.80mm", height="h + 2*t_cu + 0.2mm", name=hole_name, material="vacuum")
        pools["all_holes"].append(hole_name)

    via_coords = [(-0.80, 1.45*dir_y), (0.80, 1.45*dir_y), (-0.80, 0.90*dir_y), (0.80, 0.90*dir_y), (-0.80, 0.35*dir_y), (0.80, 0.35*dir_y)]
    for deg in (-15.0, -45.0, -75.0, -105.0, -135.0, -165.0):
        rad = math.radians(deg)
        via_coords.append((round(0.82 * math.cos(rad), 4), round(0.82 * math.sin(rad) * dir_y, 4)))
    for idx, (dx, dy) in enumerate(via_coords):
        vname = f"Via_{port_name}_{idx}"
        hfss.modeler.create_cylinder(orientation="Z", origin=[f"({x_expr}) + ({dx}mm)", f"({y_expr}) + ({dy}mm)", "-t_cu"], radius="via_dia/2", height="h + 2*t_cu", name=vname, material="copper")
        pools["gnd_metal"].append(vname)

    boss_name, barrel_name, win_cut = f"Coax_Boss_{port_name}", f"Coax_Barrel_{port_name}", f"BossWindow_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu"], radius="1.75mm", height="0.60mm", name=boss_name, material="pec")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="2.26mm", height="6.95mm", name=barrel_name, material="pec")
    win_y0 = f"({y_expr})" if dir_y > 0 else f"({y_expr}) - 1.90mm"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 0.75mm", win_y0, "h + t_cu - 0.01mm"], sizes=["1.50mm", "1.90mm", "0.56mm"], name=win_cut, material="vacuum")

    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="1.46mm", height="6.95mm", name=diel_name, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=pin_air, material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"], radius="0.175mm", height="0.58mm", name=pin_pcb, material="copper")

    antipad_name = f"AntiPad_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "-t_cu - 0.05mm"], radius="bot_cut_dia/2", height="t_cu + 0.10mm", name=antipad_name, material="vacuum")
    pools["bot_cuts"].append(antipad_name)

    pec_cap, port_sheet = f"PEC_Cap_{port_name}", f"PortSheet_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, z_port], radius="2.26mm", height="0.2mm", name=pec_cap, material="pec")
    hfss.modeler.create_circle(orientation="XY", origin=[x_expr, y_expr, z_port], radius="1.46mm", name=port_sheet, is_covered=True)
    pools["coax_ops"].append((barrel_name, boss_name, win_cut, diel_name, pin_air, pin_pcb, port_name, port_sheet, x_expr, y_expr, z_port))
'''
# --- Часть 2/2 ---
PART_2 = '''
def main():
    hfss = Hfss(project="TRL_Calibration_FR4_FMCN1476", design="TRL_Kit", solution_type="DrivenModal", new_desktop=True)
    hfss.modeler.model_units = "mm"

    for k, v in [
        ("h", "0.115mm"), ("W", "0.2mm"), ("t_cu", "0.035mm"), ("er", "4.4"), ("f0_GHz", "10.0"),
        ("L_thru", "10mm"), ("L_ref", "L_thru/2"), ("L_feed", "L_thru/2"), ("bot_cut_dia", "0.96mm"),
        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.2mm"), ("via_offset", "0.4mm"),
        ("eps_eff", "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"), ("dL", "75mm/(f0_GHz*sqrt(eps_eff))"), ("L_line", "L_thru + dL"),
        ("W_ring", "0.2mm"), ("W_tab", "0.6mm"), ("R_tab", "0.2mm"), ("gap_couple", "0.15mm"),
        ("eps_ring", "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"), ("r_mean", "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"),
        ("r_out", "r_mean + W_ring/2"), ("r_in", "r_mean - W_ring/2"), ("r_tab_in", "r_out + gap_couple"),
        ("r_tab_out", "r_tab_in + R_tab"), ("y_top_res", "r_tab_out + L_feed"),
        ("pitch_trl", "20mm"), ("pitch_res", "20mm"), ("x_thru", "0mm"), ("x_line", "pitch_trl"),
        ("x_open", "2*pitch_trl"), ("x_res", "2*pitch_trl + pitch_res"),
    ]:
        hfss[k] = v

    # === ФАЗА 1: СОЗДАНИЕ ВСЕХ ПРИМИТИВОВ ===
    pools = {
        "gnd_metal": ["GND", "GND_TOP"], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],
        "sig_groups": {"THRU_Line": ["THRU_Line"], "LINE_Line": ["LINE_Line"], "OPEN_A": ["OPEN_A"], "OPEN_B": ["OPEN_B"], "TAB_BOX": ["TAB_BOX", "RES_Feed_1", "RES_Feed_2"]},
    }
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "-t_cu"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"], name="GND", material="copper")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "0mm"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "h"], name="Substrate", material="FR4_epoxy")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "h"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"], name="GND_TOP", material="copper")

    for name, x0, y0, dy in [
        ("THRU_Line", "x_thru - W/2", "-L_thru/2", "L_thru"), ("LINE_Line", "x_line - W/2", "-L_line/2", "L_line"),
        ("OPEN_A", "x_open - W/2", "-y_top_res", "L_ref"), ("OPEN_B", "x_open - W/2", "y_top_res - L_ref", "L_ref"),
        ("RES_Feed_2", "x_res - W/2", "r_tab_out - 0.3mm", "L_feed + 0.3mm"), ("RES_Feed_1", "x_res - W/2", "-r_tab_out - L_feed", "L_feed + 0.3mm"),
    ]:
        hfss.modeler.create_box(origin=[x0, y0, "h"], sizes=["W", dy, "t_cu"], name=name, material="copper")

    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_out", height="t_cu", name="RING_OUT", material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_in", height="t_cu", name="RING_IN", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_out", height="t_cu", name="TAB_RING", material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_in", height="t_cu", name="TAB_IN", material="vacuum")
    hfss.modeler.create_box(origin=["x_res - W_tab/2", "-r_tab_out - 1mm", "h"], sizes=["W_tab", "2*r_tab_out + 2mm", "t_cu"], name="TAB_BOX", material="copper")

    for cname, x0, y0, dx, dy in [
        ("Cut_THRU", "x_thru - W/2 - gap_gnd", "-L_thru/2", "W + 2*gap_gnd", "L_thru"),
        ("Cut_LINE", "x_line - W/2 - gap_gnd", "-L_line/2", "W + 2*gap_gnd", "L_line"),
        ("Cut_OPEN_A", "x_open - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "L_ref + gap_gnd"),
        ("Cut_OPEN_B", "x_open - W/2 - gap_gnd", "y_top_res - L_ref - gap_gnd", "W + 2*gap_gnd", "L_ref + gap_gnd"),
        ("Cut_RES_Feed", "x_res - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "2*y_top_res"),
    ]:
        hfss.modeler.create_box(origin=[x0, y0, "h - 0.01mm"], sizes=[dx, dy, "t_cu + 0.02mm"], name=cname, material="vacuum")
        pools["top_cuts"].append(cname)
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_RingOut", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_RingIn", material="vacuum")

    for x_e, y_e, d_y, l_obj, p_name in [
        ("x_thru", "-L_thru/2", 1, "THRU_Line", "P_THRU_1"), ("x_thru", "L_thru/2", -1, "THRU_Line", "P_THRU_2"),
        ("x_line", "-L_line/2", 1, "LINE_Line", "P_LINE_1"), ("x_line", "L_line/2", -1, "LINE_Line", "P_LINE_2"),
        ("x_open", "-y_top_res", 1, "OPEN_A", "P_OPEN_A"), ("x_open", "y_top_res", -1, "OPEN_B", "P_OPEN_B"),
        ("x_res", "-y_top_res", 1, "TAB_BOX", "P_RES_1"), ("x_res", "y_top_res", -1, "TAB_BOX", "P_RES_2"),
    ]:
        queue_fmcn1476(hfss, x_e, y_e, d_y, l_obj, p_name, pools)

    l_thru_v, l_line_v, l_ref_v = [hfss.get_evaluated_value(n) * 1000.0 for n in ("L_thru", "L_line", "L_ref")]
    y_res_v, r_tab_v, pitch_v = [hfss.get_evaluated_value(n) * 1000.0 for n in ("y_top_res", "r_tab_out", "via_pitch")]
    def add_svia(vn, vx, vy):
        hfss.modeler.create_cylinder(orientation="Z", origin=[vx, vy, "-t_cu"], radius="via_dia/2", height="h + 2*t_cu", name=vn, material="copper")
        pools["gnd_metal"].append(vn)
    for pref, xc, y0, y1 in [
        ("THRU", "x_thru", -l_thru_v/2 + 2.2, l_thru_v/2 - 2.2), ("LINE", "x_line", -l_line_v/2 + 2.2, l_line_v/2 - 2.2),
        ("OPENA", "x_open", -y_res_v + 2.2, -y_res_v + l_ref_v + 0.5), ("OPENB", "x_open", y_res_v - l_ref_v - 0.5, y_res_v - 2.2),
        ("RES1", "x_res", -y_res_v + 2.2, -r_tab_v - 0.8), ("RES2", "x_res", r_tab_v + 0.8, y_res_v - 2.2),
    ]:
        n = max(1, int(abs(y1 - y0) / pitch_v))
        for i in range(n + 1):
            yv = y0 + (y1 - y0) * i / max(1, n)
            add_svia(f"SVia_{pref}_L_{i}", f"{xc} - (W/2 + gap_gnd + via_offset)", f"{yv:.4f}mm")
            add_svia(f"SVia_{pref}_R_{i}", f"{xc} + (W/2 + gap_gnd + via_offset)", f"{yv:.4f}mm")
    for k in range(24):
        ang = 2.0 * math.pi * k / 24.0
        if abs(math.cos(ang)) > 0.25:
            add_svia(f"SVia_RO_{k}", f"x_res + ({math.cos(ang):.5f})*(r_tab_out + gap_gnd + via_offset)", f"({math.sin(ang):.5f})*(r_tab_out + gap_gnd + via_offset)")
    add_svia("SVia_RC", "x_res", "0mm")
    for k in range(8):
        ang = 2.0 * math.pi * k / 8.0
        add_svia(f"SVia_RI_{k}", f"x_res + ({math.cos(ang):.5f})*(r_in - gap_gnd - via_offset)", f"({math.sin(ang):.5f})*(r_in - gap_gnd - via_offset)")

    # === ФАЗА 2: ПАКЕТНЫЕ БУЛЕВЫ ОПЕРАЦИИ И ПОРТЫ ===
    hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)
    hfss.modeler.subtract("TAB_RING", "TAB_IN", keep_originals=False)
    hfss.modeler.intersect(["TAB_BOX", "TAB_RING"], keep_originals=False)
    hfss.modeler.subtract("Cut_RingOut", "Cut_RingIn", keep_originals=False)
    pools["top_cuts"].append("Cut_RingOut")

    hfss.modeler.unite(pools["top_cuts"])
    hfss.modeler.subtract("GND_TOP", pools["top_cuts"][0], keep_originals=False)
    hfss.modeler.unite(pools["bot_cuts"])
    hfss.modeler.subtract("GND", pools["bot_cuts"][0], keep_originals=False)
    hfss.modeler.unite(pools["gnd_metal"])
    hfss.modeler.unite(pools["all_holes"])
    hfss.modeler.subtract(["Substrate", "GND"], pools["all_holes"][0], keep_originals=False)
    for grp in pools["sig_groups"].values():
        hfss.modeler.unite(grp)

    for barrel, boss, wcut, diel, pair, ppcb, pname, psheet, xe, ye, zp in pools["coax_ops"]:
        hfss.modeler.unite([barrel, boss])
        hfss.modeler.subtract(barrel, wcut, keep_originals=False)
        hfss.modeler.unite([pair, ppcb])
        hfss.modeler.subtract(barrel, diel, keep_originals=True)
        hfss.modeler.subtract(diel, pair, keep_originals=True)
        hfss.oboundary.AssignWavePort([
            "NAME:" + pname, "Objects:=", [psheet], "NumModes:=", 1, "UseLineModeAlignment:=", False,
            "DoDeembed:=", False, "RenormalizeAllTerminals:=", False,
            "Modes:=", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True, "IntLine:=", ["NAME:IntLine", "Start:=", [f"({xe}) + 0.635mm", ye, zp], "End:=", [f"({xe}) + 1.46mm", ye, zp]], "AlignmentGroup:=", 0, "CharImp:=", "Zpi"],
            "ShowReporterFilter:=", False, "ReporterFilter:=", [True], "UseAnalyticAlignment:=", False
        ])

    hfss.modeler.create_region(pad_value=["15mm", "15mm", "15mm", "15mm", "15mm", "0mm"], is_percentage=False, name="Region")
    hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")
    setup = hfss.create_setup("Setup_TRL")
    setup.props.update({"Frequency": "10GHz", "MaximumPasses": 16, "MaxDeltaS": 0.02})
    sweep = setup.add_sweep("Sweep_1_20GHz")
    sweep.props.update({"RangeType": "LinearCount", "RangeStart": "1GHz", "RangeEnd": "20GHz", "RangeCount": 191})
    hfss.save_project()
    print("Модель успешно сгенерирована (2-фазные булевы операции).")


if __name__ == "__main__":
    main()
'''

code = (PART_1 + PART_2).strip()
ast.parse(code)
old_lines = TARGET.read_text(encoding="utf-8").splitlines() if TARGET.exists() else []
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(code + "\n", encoding="utf-8")
new_lines = code.splitlines()
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {len(old_lines)}\n  Стало строк: {len(new_lines)} ({len(new_lines) - len(old_lines):+d})")
# === fixes/20261124_101000_refactor_two_phase_boolean.py ===
