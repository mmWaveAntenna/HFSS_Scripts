# -*- coding: utf-8 -*-
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
    if dir_y > 0:
        notch_y0, chan_y0 = f"({y_expr}) + 1.00mm", f"({y_expr})"
    else:
        notch_y0, chan_y0 = f"({y_expr}) - 1.95mm", f"({y_expr}) - 1.00mm"

    # Входной вырез Notch продолжается с той же шириной зазора от полоска (W + 2*gap_gnd)
    for cname, orig, sz in [
        (f"Notch_{port_name}", [f"({x_expr}) - W/2 - gap_gnd", notch_y0, "h - 0.01mm"], ["W + 2*gap_gnd", "0.95mm", "t_cu + 0.02mm"]),
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

    # Отступ центра via от края меди >= 0.35 мм (край отверстия Ø 0.25 мм -> >= 225 мкм по нормам Резонит)
    via_coords = [(-0.95, 1.45*dir_y), (0.95, 1.45*dir_y), (-0.95, 0.90*dir_y), (0.95, 0.90*dir_y), (-0.95, 0.35*dir_y), (0.95, 0.35*dir_y)]
    for deg in (-15.0, -45.0, -75.0, -105.0, -135.0, -165.0):
        rad = math.radians(deg)
        via_coords.append((round(0.90 * math.cos(rad), 4), round(0.90 * math.sin(rad) * dir_y, 4)))
    for idx, (dx, dy) in enumerate(via_coords):
        vname = f"Via_{port_name}_{idx}"
        hfss.modeler.create_cylinder(orientation="Z", origin=[f"({x_expr}) + ({dx}mm)", f"({y_expr}) + ({dy}mm)", "-t_cu"], radius="via_dia/2", height="h + 2*t_cu", name=vname, material="copper")
        pools["gnd_metal"].append(vname)

    boss_name, barrel_name, win_cut, boss_bore = f"Coax_Boss_{port_name}", f"Coax_Barrel_{port_name}", f"BossWindow_{port_name}", f"BossBore_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu"], radius="1.75mm", height="0.60mm", name=boss_name, material="pec")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="2.26mm", height="6.95mm", name=barrel_name, material="pec")
    win_y0 = f"({y_expr})" if dir_y > 0 else f"({y_expr}) - 1.90mm"
    hfss.modeler.create_box(origin=[f"({x_expr}) - 0.75mm", win_y0, "h + t_cu - 0.01mm"], sizes=["1.50mm", "1.90mm", "0.56mm"], name=win_cut, material="vacuum")
    # Центральный цилиндрический вырез Ø 1.27 мм (R = 0.635 мм) во втулке вокруг пина (исключает КЗ задней стенки втулки на пин)
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.01mm"], radius="0.635mm", height="0.57mm", name=boss_bore, material="vacuum")
    hfss.modeler.unite([win_cut, boss_bore])

    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=diel_name, material="vacuum")
    # Ступенька пина на высоте 0.28 мм — видна внутри бокового окна высотой 0.55 мм (DETAIL A)
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.28mm"], radius="0.275mm", height="7.22mm", name=pin_air, material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"], radius="0.175mm", height="0.31mm", name=pin_pcb, material="copper")

    antipad_name = f"AntiPad_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "-t_cu - 0.05mm"], radius="bot_cut_dia/2", height="t_cu + 0.10mm", name=antipad_name, material="vacuum")
    pools["bot_cuts"].append(antipad_name)

    pec_cap, port_sheet = f"PEC_Cap_{port_name}", f"PortSheet_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, z_port], radius="2.26mm", height="0.2mm", name=pec_cap, material="pec")
    hfss.modeler.create_circle(orientation="XY", origin=[x_expr, y_expr, z_port], radius="0.635mm", name=port_sheet, is_covered=True)
    pools["coax_ops"].append((barrel_name, boss_name, win_cut, diel_name, pin_air, pin_pcb, port_name, port_sheet, x_expr, y_expr, z_port))


def queue_fmcn1476_x_plus(hfss, x_expr, y_expr, line_obj, port_name, pools):
    """Разъём FMCN1476 на правом (+X) торце фидера (линия уходит в -X)."""
    z_port = "h + t_cu + 7.5mm"
    for cname, orig, sz in [
        (f"Notch_{port_name}", [f"({x_expr}) - 1.95mm", f"({y_expr}) - W/2 - gap_gnd", "h - 0.01mm"], ["0.95mm", "W + 2*gap_gnd", "t_cu + 0.02mm"]),
        (f"Chan_{port_name}", [f"({x_expr}) - 1.00mm", f"({y_expr}) - W/2 - 0.43mm", "h - 0.01mm"], ["1.00mm", "W + 0.86mm", "t_cu + 0.02mm"]),
    ]:
        hfss.modeler.create_box(origin=orig, sizes=sz, name=cname, material="vacuum")
        pools["top_cuts"].append(cname)

    pin_clear = f"PinClear_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h - 0.01mm"], radius="0.50mm", height="t_cu + 0.02mm", name=pin_clear, material="vacuum")
    pools["top_cuts"].append(pin_clear)

    line_pad = f"LinePad_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h"], radius="0.28mm", height="t_cu", name=line_pad, material="copper")
    pools["sig_groups"][line_obj].append(line_pad)

    for side, sign in [("B", -1), ("T", 1)]:
        hname = f"MntHole_{port_name}_{side}"
        hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, f"({y_expr}) + ({sign}*3.58mm)", "-t_cu - 0.1mm"], radius="0.80mm", height="h + 2*t_cu + 0.2mm", name=hname, material="vacuum")
        pools["all_holes"].append(hname)

    via_coords = [(-1.45, -0.95), (-1.45, 0.95), (-0.90, -0.95), (-0.90, 0.95), (-0.35, -0.95), (-0.35, 0.95)]
    for deg in (-15.0, -45.0, -75.0, -105.0, -135.0, -165.0):
        rad = math.radians(deg)
        via_coords.append((round(-0.90 * math.sin(rad), 4), round(0.90 * math.cos(rad), 4)))
    for idx, (dx, dy) in enumerate(via_coords):
        vname = f"Via_{port_name}_{idx}"
        hfss.modeler.create_cylinder(orientation="Z", origin=[f"({x_expr}) + ({dx}mm)", f"({y_expr}) + ({dy}mm)", "-t_cu"], radius="via_dia/2", height="h + 2*t_cu", name=vname, material="copper")
        pools["gnd_metal"].append(vname)

    boss, barrel, wcut, bbore = f"Coax_Boss_{port_name}", f"Coax_Barrel_{port_name}", f"BossWindow_{port_name}", f"BossBore_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu"], radius="1.75mm", height="0.60mm", name=boss, material="pec")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="2.26mm", height="6.95mm", name=barrel, material="pec")
    hfss.modeler.create_box(origin=[f"({x_expr}) - 1.90mm", f"({y_expr}) - 0.75mm", "h + t_cu - 0.01mm"], sizes=["1.90mm", "1.50mm", "0.56mm"], name=wcut, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.01mm"], radius="0.635mm", height="0.57mm", name=bbore, material="vacuum")
    hfss.modeler.unite([wcut, bbore])

    diel, pair, ppcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=diel, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.28mm"], radius="0.275mm", height="7.22mm", name=pair, material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"], radius="0.175mm", height="0.31mm", name=ppcb, material="copper")

    ap = f"AntiPad_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "-t_cu - 0.05mm"], radius="bot_cut_dia/2", height="t_cu + 0.10mm", name=ap, material="vacuum")
    pools["bot_cuts"].append(ap)
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, z_port], radius="2.26mm", height="0.2mm", name=f"PEC_Cap_{port_name}", material="pec")
    psheet = f"PortSheet_{port_name}"
    hfss.modeler.create_circle(orientation="XY", origin=[x_expr, y_expr, z_port], radius="0.635mm", name=psheet, is_covered=True)
    pools["coax_ops"].append((barrel, boss, wcut, diel, pair, ppcb, port_name, psheet, x_expr, y_expr, z_port))


def main():
    hfss = Hfss(project="TRL_Calibration_FR4_FMCN1476", design="TRL_Kit", solution_type="DrivenModal", new_desktop=True)
    hfss.modeler.model_units = "mm"
    try:
        hfss.autosave_disable()
    except Exception:
        pass

    for k, v in [
        ("h", "0.115mm"), ("W", "0.2mm"), ("t_cu", "0.035mm"), ("er", "4.4"), ("f0_GHz", "10.0"),
        ("L_thru", "10mm"), ("L_ref", "L_thru/2"), ("L_feed", "L_thru/2"), ("bot_cut_dia", "0.96mm"),
        ("gap_gnd", "0.5mm"), ("via_dia", "0.25mm"), ("via_pitch", "1.0mm"), ("via_offset", "0.4mm"),
        ("eps_eff", "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"), ("dL", "75mm/(f0_GHz*sqrt(eps_eff))"), ("L_line", "L_thru + dL"),
        ("W_ring", "0.2mm"), ("W_tab", "0.6mm"), ("R_tab", "0.2mm"), ("gap_couple", "0.15mm"),
        ("eps_ring", "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"), ("r_mean", "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"),
        ("r_out", "r_mean + W_ring/2"), ("r_in", "r_mean - W_ring/2"),
        ("r_via_out", "r_out + gap_gnd + via_offset"),
        ("r_via_in", "max(r_in - gap_gnd - via_offset, 0.25mm)"),
        ("phi_guard", "asin(min((W/2 + gap_gnd + via_offset) / r_via_out, 0.95))"), ("r_tab_in", "r_out + gap_couple"),
        ("r_tab_out", "r_tab_in + R_tab"), ("y_top_res", "r_tab_out + L_feed"),
        ("pitch_trl", "20mm"), ("pitch_res", "20mm"), ("x_thru", "0mm"), ("x_line", "pitch_trl"),
        ("x_open", "2*pitch_trl"), ("x_res", "2*pitch_trl + pitch_res"), ("x_res2", "2*pitch_trl + 2*pitch_res"),
    ]:
        hfss[k] = v

    # === ФАЗА 1: СОЗДАНИЕ ВСЕХ ПРИМИТИВОВ ===
    pools = {
        "gnd_metal": ["GND", "GND_TOP"], "top_cuts": [], "bot_cuts": [], "all_holes": [], "coax_ops": [],
        "sig_groups": {"THRU_Line": ["THRU_Line"], "LINE_Line": ["LINE_Line"], "OPEN_A": ["OPEN_A"], "OPEN_B": ["OPEN_B"], "TAB_BOX": ["TAB_BOX", "RES_Feed_1", "RES_Feed_2"]},
    }
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "-t_cu"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "t_cu"], name="GND", material="copper")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "0mm"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "h"], name="Substrate", material="FR4_epoxy")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "h"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "t_cu"], name="GND_TOP", material="copper")

    for name, x0, y0, dy in [
        ("THRU_Line", "x_thru - W/2", "-L_thru/2", "L_thru"), ("LINE_Line", "x_line - W/2", "-L_line/2", "L_line"),
        ("OPEN_A", "x_open - W/2", "-y_top_res", "L_ref"), ("OPEN_B", "x_open - W/2", "y_top_res - L_ref", "L_ref"),
        ("RES_Feed_2", "x_res - W/2", "r_tab_out - 0.05mm", "L_feed + 0.05mm"), ("RES_Feed_1", "x_res - W/2", "-r_tab_out - L_feed", "L_feed + 0.05mm"),
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
        ("Cut_RES_1", "x_res - W/2 - gap_gnd", "-y_top_res", "W + 2*gap_gnd", "L_feed + gap_gnd"),
        ("Cut_RES_2", "x_res - W/2 - gap_gnd", "r_tab_out - gap_gnd", "W + 2*gap_gnd", "L_feed + gap_gnd"),
    ]:
        hfss.modeler.create_box(origin=[x0, y0, "h - 0.01mm"], sizes=[dx, dy, "t_cu + 0.02mm"], name=cname, material="vacuum")
        pools["top_cuts"].append(cname)
    # Облегающий вырез отдельно вокруг кольца (r_out + gap_gnd) и отдельно вокруг T-лапок (r_tab_out + gap_gnd)
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_RingOut", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_RingIn", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_TabArc", material="vacuum")
    hfss.modeler.create_box(origin=["x_res - W_tab/2 - gap_gnd", "-r_tab_out - gap_gnd - 0.5mm", "h - 0.01mm"], sizes=["W_tab + 2*gap_gnd", "2*(r_tab_out + gap_gnd) + 1.0mm", "t_cu + 0.02mm"], name="Cut_TabBox", material="vacuum")

    for x_e, y_e, d_y, l_obj, p_name in [
        ("x_thru", "-L_thru/2", 1, "THRU_Line", "P_THRU_1"), ("x_thru", "L_thru/2", -1, "THRU_Line", "P_THRU_2"),
        ("x_line", "-L_line/2", 1, "LINE_Line", "P_LINE_1"), ("x_line", "L_line/2", -1, "LINE_Line", "P_LINE_2"),
        ("x_open", "-y_top_res", 1, "OPEN_A", "P_OPEN_A"), ("x_open", "y_top_res", -1, "OPEN_B", "P_OPEN_B"),
        ("x_res", "-y_top_res", 1, "TAB_BOX", "P_RES_1"), ("x_res", "y_top_res", -1, "TAB_BOX", "P_RES_2"),
    ]:
        queue_fmcn1476(hfss, x_e, y_e, d_y, l_obj, p_name, pools)

    # Второй кольцевой резонатор (питание под углом 90°: -Y и +X)
    pools["sig_groups"]["TAB2_BOT"] = ["TAB2_BOT", "RES2_Feed_1"]
    pools["sig_groups"]["TAB2_RIGHT"] = ["TAB2_RIGHT", "RES2_Feed_2"]
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h"], radius="r_out", height="t_cu", name="RING2_OUT", material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h"], radius="r_in", height="t_cu", name="RING2_IN", material="vacuum")
    for tname, orig, sz in [
        ("TAB2_BOT", ["x_res2 - W_tab/2", "-r_tab_out - 0.5mm", "h"], ["W_tab", "r_tab_out + 0.5mm", "t_cu"]),
        ("TAB2_RIGHT", ["x_res2", "-W_tab/2", "h"], ["r_tab_out + 0.5mm", "W_tab", "t_cu"]),
    ]:
        hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h"], radius="r_tab_out", height="t_cu", name=tname + "_RO", material="copper")
        hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h"], radius="r_tab_in", height="t_cu", name=tname + "_RI", material="vacuum")
        hfss.modeler.create_box(origin=orig, sizes=sz, name=tname, material="copper")
    hfss.modeler.create_box(origin=["x_res2 - W/2", "-r_tab_out - L_feed", "h"], sizes=["W", "L_feed + 0.05mm", "t_cu"], name="RES2_Feed_1", material="copper")
    hfss.modeler.create_box(origin=["x_res2 + r_tab_out - 0.05mm", "-W/2", "h"], sizes=["L_feed + 0.05mm", "W", "t_cu"], name="RES2_Feed_2", material="copper")

    for cname, orig, sz in [
        ("Cut_RES2_1", ["x_res2 - W/2 - gap_gnd", "-y_top_res", "h - 0.01mm"], ["W + 2*gap_gnd", "L_feed + gap_gnd", "t_cu + 0.02mm"]),
        ("Cut_RES2_2", ["x_res2 + r_tab_out - gap_gnd", "-W/2 - gap_gnd", "h - 0.01mm"], ["L_feed + gap_gnd", "W + 2*gap_gnd", "t_cu + 0.02mm"]),
    ]:
        hfss.modeler.create_box(origin=orig, sizes=sz, name=cname, material="vacuum")
        pools["top_cuts"].append(cname)
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h - 0.01mm"], radius="r_out + gap_gnd", height="t_cu + 0.02mm", name="Cut_Ring2Out", material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h - 0.01mm"], radius="max(r_in - gap_gnd, 0.2mm)", height="t_cu + 0.02mm", name="Cut_Ring2In", material="vacuum")
    for tcut, orig, sz in [
        ("Cut_Tab2B", ["x_res2 - W_tab/2 - gap_gnd", "-r_tab_out - gap_gnd - 0.5mm", "h - 0.01mm"], ["W_tab + 2*gap_gnd", "r_tab_out + gap_gnd + 0.5mm", "t_cu + 0.02mm"]),
        ("Cut_Tab2R", ["x_res2", "-W_tab/2 - gap_gnd", "h - 0.01mm"], ["r_tab_out + gap_gnd + 0.5mm", "W_tab + 2*gap_gnd", "t_cu + 0.02mm"]),
    ]:
        hfss.modeler.create_cylinder(orientation="Z", origin=["x_res2", "0mm", "h - 0.01mm"], radius="r_tab_out + gap_gnd", height="t_cu + 0.02mm", name=tcut + "_A", material="vacuum")
        hfss.modeler.create_box(origin=orig, sizes=sz, name=tcut, material="vacuum")

    queue_fmcn1476(hfss, "x_res2", "-y_top_res", 1, "TAB2_BOT", "P_RES2_1", pools)
    queue_fmcn1476_x_plus(hfss, "x_res2 + y_top_res", "0mm", "TAB2_RIGHT", "P_RES2_2", pools)

    l_thru_v, l_line_v, l_ref_v = [hfss.get_evaluated_value(n) * 1000.0 for n in ("L_thru", "L_line", "L_ref")]
    y_res_v, r_tab_v, pitch_v = [hfss.get_evaluated_value(n) * 1000.0 for n in ("y_top_res", "r_tab_out", "via_pitch")]
    def add_svia(vn, vx, vy):
        hfss.modeler.create_cylinder(orientation="Z", origin=[vx, vy, "-t_cu"], radius="via_dia/2", height="h + 2*t_cu", name=vn, material="copper")
        pools["gnd_metal"].append(vn)
    # Параметрическая расстановка via вдоль всех линий (двигаются за L_line, r_tab_out, y_top_res при смене f0_GHz)
    # Постоянный шаг via_pitch (1.0 мм) при изменении f0_GHz / радиуса (запас 2.5x через min(..., end))
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

    # === ФАЗА 2: ПАКЕТНЫЕ БУЛЕВЫ ОПЕРАЦИИ И ПОРТЫ ===
    hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)
    hfss.modeler.subtract("TAB_RING", "TAB_IN", keep_originals=False)
    hfss.modeler.intersect(["TAB_BOX", "TAB_RING"], keep_originals=False)
    hfss.modeler.intersect(["Cut_TabBox", "Cut_TabArc"], keep_originals=False)
    hfss.modeler.unite(["Cut_RingOut", "Cut_TabBox"])
    hfss.modeler.subtract("Cut_RingOut", "Cut_RingIn", keep_originals=False)
    pools["top_cuts"].append("Cut_RingOut")

    hfss.modeler.subtract("RING2_OUT", "RING2_IN", keep_originals=False)
    for tname in ("TAB2_BOT", "TAB2_RIGHT"):
        hfss.modeler.subtract(tname + "_RO", tname + "_RI", keep_originals=False)
        hfss.modeler.intersect([tname, tname + "_RO"], keep_originals=False)
    for tcut in ("Cut_Tab2B", "Cut_Tab2R"):
        hfss.modeler.intersect([tcut, tcut + "_A"], keep_originals=False)
    hfss.modeler.unite(["Cut_Ring2Out", "Cut_Tab2B", "Cut_Tab2R"])
    hfss.modeler.subtract("Cut_Ring2Out", "Cut_Ring2In", keep_originals=False)
    pools["top_cuts"].append("Cut_Ring2Out")
    hfss.modeler.unite(pools["top_cuts"])
    hfss.modeler.subtract("GND_TOP", pools["top_cuts"][0], keep_originals=False)
    hfss.modeler.unite(pools["bot_cuts"])
    hfss.modeler.subtract("GND", pools["bot_cuts"][0], keep_originals=False)
    gnd_parts = pools["gnd_metal"]
    for i in range(1, len(gnd_parts), 50):
        hfss.modeler.unite([gnd_parts[0]] + gnd_parts[i:i + 50])
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
            "Modes:=", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True, "IntLine:=", ["NAME:IntLine", "Start:=", [f"({xe}) + 0.275mm", ye, zp], "End:=", [f"({xe}) + 0.635mm", ye, zp]], "AlignmentGroup:=", 0, "CharImp:=", "Zpi"],
            "ShowReporterFilter:=", False, "ReporterFilter:=", [True], "UseAnalyticAlignment:=", False
        ])

    hfss.modeler.create_region(pad_value=["15mm", "15mm", "15mm", "15mm", "15mm", "0mm"], is_percentage=False, name="Region")
    hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")
    setup = hfss.create_setup("Setup_TRL")
    setup.props.update({"Frequency": "10GHz", "MaximumPasses": 16, "MaxDeltaS": 0.02})
    sweep = setup.add_sweep("Sweep_1_20GHz")
    sweep.props.update({"RangeType": "LinearCount", "RangeStart": "1GHz", "RangeEnd": "20GHz", "RangeCount": 191})
    try:
        hfss.autosave_enable()
    except Exception:
        pass
    hfss.save_project()
    print("Модель успешно сгенерирована (2-фазные булевы операции).")


if __name__ == "__main__":
    main()
