# --- Часть 1/2 ---
import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

HELPER_90 = '''
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
'''
# --- Часть 2/2 ---
OLD_COORDS = '''        ("x_open", "2*pitch_trl"), ("x_res", "2*pitch_trl + pitch_res"),'''
NEW_COORDS = '''        ("x_open", "2*pitch_trl"), ("x_res", "2*pitch_trl + pitch_res"), ("x_res2", "2*pitch_trl + 2*pitch_res"),'''

OLD_BOARD = '''    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "-t_cu"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"], name="GND", material="copper")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "0mm"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "h"], name="Substrate", material="FR4_epoxy")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "h"], sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"], name="GND_TOP", material="copper")'''

NEW_BOARD = '''    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "-t_cu"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "t_cu"], name="GND", material="copper")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "0mm"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "h"], name="Substrate", material="FR4_epoxy")
    hfss.modeler.create_box(origin=["-10mm", "-y_top_res - 10mm", "h"], sizes=["x_res2 + y_top_res + 18mm", "2*y_top_res + 20mm", "t_cu"], name="GND_TOP", material="copper")'''

RES2_GEO = '''
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
'''

RES2_VIAS_AND_BOOL = '''
    # Прошивка via второго резонатора (90°)
    n_f2 = max(1, int(abs((y_res_v - 2.1) - (r_tab_v + 0.6)) / pitch_v))
    for i in range(n_f2 + 1):
        dv = (r_tab_v + 0.6) + ((y_res_v - 2.1) - (r_tab_v + 0.6)) * i / max(1, n_f2)
        add_svia(f"SVia_R2B_L_{i}", "x_res2 - (W/2 + gap_gnd + via_offset)", f"-{dv:.4f}mm")
        add_svia(f"SVia_R2B_R_{i}", "x_res2 + (W/2 + gap_gnd + via_offset)", f"-{dv:.4f}mm")
        add_svia(f"SVia_R2R_B_{i}", f"x_res2 + {dv:.4f}mm", "-(W/2 + gap_gnd + via_offset)")
        add_svia(f"SVia_R2R_T_{i}", f"x_res2 + {dv:.4f}mm", "+(W/2 + gap_gnd + via_offset)")
    for k in range(40):
        ang = 2.0 * math.pi * k / 40.0
        ca, sa = math.cos(ang), math.sin(ang)
        if not ((sa < -0.92 and abs(ca) < 0.38) or (ca > 0.92 and abs(sa) < 0.38)):
            add_svia(f"SVia_R2O_{k}", f"x_res2 + ({ca:.5f})*(r_out + gap_gnd + via_offset)", f"({sa:.5f})*(r_out + gap_gnd + via_offset)")
    add_svia("SVia_R2C", "x_res2", "0mm")
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        add_svia(f"SVia_R2I_{k}", f"x_res2 + ({math.cos(ang):.5f})*(r_in - gap_gnd - via_offset)", f"({math.sin(ang):.5f})*(r_in - gap_gnd - via_offset)")
'''

RES2_BOOL_OPS = '''    hfss.modeler.subtract("RING2_OUT", "RING2_IN", keep_originals=False)
    for tname in ("TAB2_BOT", "TAB2_RIGHT"):
        hfss.modeler.subtract(tname + "_RO", tname + "_RI", keep_originals=False)
        hfss.modeler.intersect([tname, tname + "_RO"], keep_originals=False)
    for tcut in ("Cut_Tab2B", "Cut_Tab2R"):
        hfss.modeler.intersect([tcut, tcut + "_A"], keep_originals=False)
    hfss.modeler.unite(["Cut_Ring2Out", "Cut_Tab2B", "Cut_Tab2R"])
    hfss.modeler.subtract("Cut_Ring2Out", "Cut_Ring2In", keep_originals=False)
    pools["top_cuts"].append("Cut_Ring2Out")
'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace("def main():", HELPER_90 + "\n\ndef main():", 1)
        .replace(OLD_COORDS, NEW_COORDS, 1)
        .replace(OLD_BOARD, NEW_BOARD, 1)
        .replace("    # === ФАЗА 2: ПАКЕТНЫЕ БУЛЕВЫ ОПЕРАЦИИ И ПОРТЫ ===", RES2_GEO + RES2_VIAS_AND_BOOL + "\n    # === ФАЗА 2: ПАКЕТНЫЕ БУЛЕВЫ ОПЕРАЦИИ И ПОРТЫ ===", 1)
        .replace('    hfss.modeler.unite(pools["top_cuts"])', RES2_BOOL_OPS + '    hfss.modeler.unite(pools["top_cuts"])', 1)
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_123100_add_orthogonal_resonator_90deg.py ===
