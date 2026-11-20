# -*- coding: utf-8 -*-
"""TRL + кольцевой резонатор с коаксиальными разъёмами (TRL_Res_Prod.py, v1.4).

Изменения:
* Технологический отступ gap_foil (0.2 мм) добавлен для ВСЕЙ меди:
  - GND (нижний слой) — по всему контуру;
  - TopPad (верхний слой) — по Y;
  - Сигнальные линии (THRU, LINE, OPEN_A/B) и фидеры резонатора (FEED_TOP/BOT)
    — со стороны коннектора. Открытые концы и зона TAB не инсетятся.
* Пины разъёмов перекрывают линии на 1 мм (контакт сохранён).
* conn_ext убран, разъёмы ровно на торцах линий.
* OPEN-линии и разъёмы выровнены по Y с RES (±y_top_res).
"""

import math

try:
    from pyaedt import Hfss
except ImportError:
    from ansys.aedt.core import Hfss


# ================================================================
# 1. Параметры
# ================================================================
PROJECT_NAME = "TRL_Calibration_FR4_Param"
DESIGN_NAME  = "TRL_Kit"

h_mm        = 1.6
W_mm        = 3.0
t_cu_mm     = 0.035
er_val      = 4.4
tan_d_val   = 0.02
L_thru_mm   = 10.0
f0_ghz      = 2.4
gap_mm      = 50.0

pitch_trl_mm = 45.0
pitch_res_mm = 35.0

W_ring_mm     = 2.0
R_tab_mm      = 2.0
W_tab_mm      = 4.0
gap_couple_mm = 0.3
overlap_mm    = 0.5
x_overlap_mm  = 1.0
gap_foil_mm   = 0.2

x_margin_mm = (W_mm + 10.0) / 2.0 + 2.0

# --- Посадочное место разъема (G14SFB001, 1.85 мм) ---
conn_pin_offset = 4.24
conn_ins_depth  = 5.08
conn_slot_w     = 2.0
conn_slot_l     = 1.4
conn_hole_pitch = 9.53
conn_hole_x     = 3.0
conn_gnd_gap    = 6.35
conn_flange_w   = 12.7
conn_height     = 9.53
leg_width       = (conn_flange_w - conn_gnd_gap) / 2.0
leg_height      = 2.5
pad_size_y      = 5.58

# --- Коаксиал (G14SFB001) ---
r_pin_tip   = 0.13 / 2.0
r_pin_coax  = 0.23 / 2.0
r_diel      = 0.75 / 2.0
r_outer     = 1.85 / 2.0
L_coax_mm   = 150.0 / f0_ghz
pin_z_overlap = 0.008

# --- Python-предвычисления ---
L_thru_val    = L_thru_mm
eps_eff_val   = (er_val + 1)/2 + (er_val - 1)/2/math.sqrt(1 + 12*h_mm/W_mm)
dL_val        = 75.0 / (f0_ghz * math.sqrt(eps_eff_val))
L_line_val    = L_thru_mm + dL_val

eps_ring_val  = (er_val + 1)/2 + (er_val - 1)/2/math.sqrt(1 + 12*h_mm/W_ring_mm)
r_mean_val    = 300.0 / (2 * math.pi * f0_ghz * math.sqrt(eps_ring_val))
r_out_val     = r_mean_val + W_ring_mm/2
r_tab_in_val  = r_out_val + gap_couple_mm
r_tab_out_val = r_tab_in_val + R_tab_mm
y_top_res_val = r_tab_out_val + (L_thru_mm/2)

x_thru_val = -pitch_trl_mm
x_line_val = 0.0
x_open_val = pitch_trl_mm
x_res_val  = pitch_trl_mm + pitch_res_mm


# ================================================================
# 2. Инициализация
# ================================================================
hfss = Hfss(project=PROJECT_NAME, design=DESIGN_NAME,
            solution_type="DrivenModal", new_desktop=True)
hfss.modeler.model_units = "mm"


# ================================================================
# 3. Материалы и переменные
# ================================================================
if "FR4_Custom" not in hfss.materials.material_keys:
    fr4 = hfss.materials.add_material("FR4_Custom")
    fr4.permittivity = er_val
    fr4.dielectric_loss_tangent = tan_d_val

if "PTFE" not in hfss.materials.material_keys:
    ptfe = hfss.materials.add_material("PTFE")
    ptfe.permittivity = 2.1
    ptfe.dielectric_loss_tangent = 0.0002

hfss["h"]         = "{}mm".format(h_mm)
hfss["W"]         = "{}mm".format(W_mm)
hfss["t_cu"]      = "{}mm".format(t_cu_mm)
hfss["er"]        = "{}".format(er_val)
hfss["f0_GHz"]    = "{}".format(f0_ghz)
hfss["L_thru"]    = "{}mm".format(L_thru_mm)
hfss["gap"]       = "{}mm".format(gap_mm)
hfss["x_margin"]  = "{}mm".format(x_margin_mm)
hfss["x_overlap"] = "{}mm".format(x_overlap_mm)
hfss["gap_foil"]  = "{}mm".format(gap_foil_mm)
hfss["pitch_trl"] = "{}mm".format(pitch_trl_mm)
hfss["pitch_res"] = "{}mm".format(pitch_res_mm)

hfss["W_ring"]     = "{}mm".format(W_ring_mm)
hfss["W_tab"]      = "{}mm".format(W_tab_mm)
hfss["R_tab"]      = "{}mm".format(R_tab_mm)
hfss["gap_couple"] = "{}mm".format(gap_couple_mm)
hfss["overlap"]    = "{}mm".format(overlap_mm)

# Разъем
hfss["conn_ins_depth"] = "{}mm".format(conn_ins_depth)
hfss["conn_gnd_gap"]   = "{}mm".format(conn_gnd_gap)
hfss["conn_flange_w"]  = "{}mm".format(conn_flange_w)
hfss["conn_hole_pitch"]= "{}mm".format(conn_hole_pitch)
hfss["conn_slot_w"]    = "{}mm".format(conn_slot_w)
hfss["conn_slot_l"]    = "{}mm".format(conn_slot_l)
hfss["conn_hole_x"]    = "{}mm".format(conn_hole_x)
hfss["conn_height"]    = "{}mm".format(conn_height)
hfss["leg_width"]      = "{}mm".format(leg_width)
hfss["leg_height"]     = "{}mm".format(leg_height)
hfss["pad_size_y"]     = "{}mm".format(pad_size_y)

# Радиусы коаксиала
hfss["r_outer"]    = "{}mm".format(r_outer)
hfss["r_diel"]     = "{}mm".format(r_diel)
hfss["r_pin_coax"] = "{}mm".format(r_pin_coax)
hfss["L_coax"]     = "{}mm".format(L_coax_mm)

hfss["z_coax"] = "h + t_cu - {}mm + r_pin_coax".format(pin_z_overlap)

hfss["L_ref"]  = "L_thru/2"
hfss["L_feed"] = "L_thru/2"

hfss["eps_eff"] = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"
hfss["dL"]      = "75mm/(f0_GHz*sqrt(eps_eff))"
hfss["L_line"]  = "L_thru + dL"

hfss["eps_ring"]  = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"
hfss["r_mean"]    = "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"
hfss["r_out"]     = "r_mean + W_ring/2"
hfss["r_in"]      = "r_mean - W_ring/2"
hfss["r_tab_in"]  = "r_out + gap_couple"
hfss["r_tab_out"] = "r_tab_in + R_tab"
hfss["y_top_res"] = "r_tab_out + L_feed"

hfss["x_thru"]  = "-pitch_trl"
hfss["x_line"]  = "0mm"
hfss["x_open"]  = "pitch_trl"
hfss["x_res"]   = "pitch_trl + pitch_res"

hfss["x_left"]  = "-pitch_trl - W/2 - x_margin"
hfss["x_right"] = "(pitch_trl + pitch_res) + r_tab_out + x_margin"
hfss["sub_w"]   = "x_right - x_left"
hfss["y_top"]   = "max(L_line/2, y_top_res)"
hfss["sub_l"]   = "2*y_top"


# ================================================================
# 4. Подложка и нижняя земля (GND с inset gap_foil)
# ================================================================
sub_parts = []
gnd_bot_parts = []

def add_pcb_block(name_sub, name_gnd, x0, y0, dx, dy):
    # Подложка — полный размер
    hfss.modeler.create_box(origin=[x0, y0, "0mm"], sizes=[dx, dy, "h"], name=name_sub, material="FR4_Custom")
    sub_parts.append(name_sub)
    # GND — inset на gap_foil по всему контуру
    hfss.modeler.create_box(
        origin=["({}) + gap_foil".format(x0), "({}) + gap_foil".format(y0), "-t_cu"],
        sizes=["max(({}) - 2*gap_foil, 0.1mm)".format(dx), "max(({}) - 2*gap_foil, 0.1mm)".format(dy), "t_cu"],
        name=name_gnd, material="copper")
    gnd_bot_parts.append(name_gnd)

add_pcb_block("Substrate_FR4", "GND_BOT", "x_thru - W/2 - x_margin", "-L_thru/2", "W + 2*x_margin", "L_thru")
add_pcb_block("Sub_LINE", "GND_LINE", "x_line - W/2 - x_margin", "-L_line/2", "W + 2*x_margin", "L_line")
add_pcb_block("Sub_OPEN", "GND_OPEN", "x_open - W/2 - x_margin", "-y_top_res", "W + 2*x_margin", "2*y_top_res")
add_pcb_block("Sub_RES", "GND_RES", "x_res - r_tab_out - x_margin", "-y_top_res", "2*(r_tab_out + x_margin)", "2*y_top_res")

# Мостики (GND_Bridge с inset gap_foil по Y)
hfss.modeler.create_box(origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2", "0mm"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_thru", "h"], name="Bridge_1", material="FR4_Custom")
sub_parts.append("Bridge_1")
hfss.modeler.create_box(
    origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2 + gap_foil", "-t_cu"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "max(L_thru - 2*gap_foil, 0.1mm)", "t_cu"],
    name="GND_Bridge_1", material="copper")
gnd_bot_parts.append("GND_Bridge_1")

hfss.modeler.create_box(origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2", "0mm"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "h"], name="Bridge_2", material="FR4_Custom")
sub_parts.append("Bridge_2")
hfss.modeler.create_box(
    origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2 + gap_foil", "-t_cu"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "max(L_line - 2*gap_foil, 0.1mm)", "t_cu"],
    name="GND_Bridge_2", material="copper")
gnd_bot_parts.append("GND_Bridge_2")

hfss.modeler.create_box(origin=["x_open + W/2 + x_margin - x_overlap", "-y_top_res", "0mm"], sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "2*y_top_res", "h"], name="Bridge_3", material="FR4_Custom")
sub_parts.append("Bridge_3")
hfss.modeler.create_box(
    origin=["x_open + W/2 + x_margin - x_overlap", "-y_top_res + gap_foil", "-t_cu"],
    sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "max(2*y_top_res - 2*gap_foil, 0.1mm)", "t_cu"],
    name="GND_Bridge_3", material="copper")
gnd_bot_parts.append("GND_Bridge_3")

res_sub = hfss.modeler.unite(sub_parts)
substrate_name = res_sub if isinstance(res_sub, str) else sub_parts[0]
res_gnd_bot = hfss.modeler.unite(gnd_bot_parts)
gnd_bot_name = res_gnd_bot if isinstance(res_gnd_bot, str) else gnd_bot_parts[0]


# ================================================================
# 4b. Посадочные места TopPad + овальные пазы
# ================================================================
ports_info = [
    ("x_thru", x_thru_val, "-L_thru/2", -1),
    ("x_thru", x_thru_val, "L_thru/2", +1),
    ("x_line", x_line_val, "-L_line/2", -1),
    ("x_line", x_line_val, "L_line/2", +1),
    ("x_open", x_open_val, "-y_top_res", -1),
    ("x_open", x_open_val, "y_top_res", +1),
    ("x_res", x_res_val, "-y_top_res", -1),
    ("x_res", x_res_val, "y_top_res", +1),
]

top_pads = []
hole_parts = []

for i, (x_expr, x_num, y_edge_expr, d) in enumerate(ports_info):
    if d < 0:
        y0_expr = "({}) + gap_foil".format(y_edge_expr)
    else:
        y0_expr = "({}) - gap_foil - pad_size_y".format(y_edge_expr)

    pad_L = hfss.modeler.create_box(
        origin=["({}) - conn_flange_w/2".format(x_expr), y0_expr, "h"],
        sizes=["leg_width", "pad_size_y", "t_cu"],
        name="TopPad_{}_L".format(i), material="copper")
    top_pads.append(pad_L.name)
    pad_R = hfss.modeler.create_box(
        origin=["({}) + conn_gnd_gap/2".format(x_expr), y0_expr, "h"],
        sizes=["leg_width", "pad_size_y", "t_cu"],
        name="TopPad_{}_R".format(i), material="copper")
    top_pads.append(pad_R.name)

    y_hole_expr = "({}) + conn_hole_x".format(y_edge_expr) if d < 0 else "({}) - conn_hole_x".format(y_edge_expr)
    for j, dx_expr in enumerate(["-conn_hole_pitch/2", "conn_hole_pitch/2"]):
        x_center = "({}) + ({})".format(x_expr, dx_expr)
        y_center = y_hole_expr

        c1 = hfss.modeler.create_cylinder(
            orientation="Z",
            origin=[x_center, "({}) - (conn_slot_l/2)".format(y_center), "-1mm"],
            radius="conn_slot_w/2", height="h + 2mm",
            name="Slot_{}_{}_C1".format(i, j), material="vacuum")
        c2 = hfss.modeler.create_cylinder(
            orientation="Z",
            origin=[x_center, "({}) + (conn_slot_l/2)".format(y_center), "-1mm"],
            radius="conn_slot_w/2", height="h + 2mm",
            name="Slot_{}_{}_C2".format(i, j), material="vacuum")
        b = hfss.modeler.create_box(
            origin=["({}) - (conn_slot_w/2)".format(x_center),
                    "({}) - (conn_slot_l/2)".format(y_center), "-1mm"],
            sizes=["conn_slot_w", "conn_slot_l", "h + 2mm"],
            name="Slot_{}_{}_B".format(i, j), material="vacuum")

        res = hfss.modeler.unite([c1.name, c2.name, b.name])
        slot_name = res if isinstance(res, str) else c1.name
        hole_parts.append(slot_name)

res_pad = hfss.modeler.unite(top_pads)
top_pad_name = res_pad if isinstance(res_pad, str) else top_pads[0]

hfss.modeler.subtract(top_pad_name, hole_parts, keep_originals=True)
hfss.modeler.subtract(substrate_name, hole_parts, keep_originals=True)
hfss.modeler.subtract(gnd_bot_name, hole_parts, keep_originals=False)


# ================================================================
# 5. Металлизация: TRL + резонатор (линии с gap_foil со стороны коннектора)
# ================================================================
# THRU: инсет gap_foil с обеих сторон
hfss.modeler.create_box(
    origin=["x_thru - W/2", "-L_thru/2 + gap_foil", "h"],
    sizes=["W", "L_thru - 2*gap_foil", "t_cu"],
    name="THRU_Line", material="copper")

# LINE: инсет gap_foil с обеих сторон
hfss.modeler.create_box(
    origin=["x_line - W/2", "-L_line/2 + gap_foil", "h"],
    sizes=["W", "L_line - 2*gap_foil", "t_cu"],
    name="LINE_Line", material="copper")

# OPEN_A: инсет gap_foil снизу (со стороны коннектора)
hfss.modeler.create_box(
    origin=["x_open - W/2", "-y_top_res + gap_foil", "h"],
    sizes=["W", "L_ref - gap_foil", "t_cu"],
    name="OPEN_A_Line", material="copper")

# OPEN_B: инсет gap_foil сверху (со стороны коннектора)
hfss.modeler.create_box(
    origin=["x_open - W/2", "y_top_res - L_ref", "h"],
    sizes=["W", "L_ref - gap_foil", "t_cu"],
    name="OPEN_B_Line", material="copper")

# Кольцо
hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_out", height="t_cu", name="RING_OUT", material="copper")
hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_in", height="t_cu", name="RING_IN", material="vacuum")
hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)

hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_out", height="t_cu", name="RING_TAB_OUT", material="copper")
hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_in", height="t_cu", name="RING_TAB_IN", material="vacuum")
hfss.modeler.subtract("RING_TAB_OUT", "RING_TAB_IN", keep_originals=False)

hfss.modeler.create_box(origin=["x_res - W_tab/2", "-r_tab_out - 1mm", "h"], sizes=["W_tab", "2*r_tab_out + 2mm", "t_cu"], name="TAB_BOX", material="copper")

res = hfss.modeler.intersect(["TAB_BOX", "RING_TAB_OUT"], keep_originals=False)
tabs_final = res if isinstance(res, str) else (res[0] if isinstance(res, (list, tuple)) else "TAB_BOX")

# FEED_TOP: инсет gap_foil сверху (со стороны коннектора)
hfss.modeler.create_box(
    origin=["x_res - W/2", "r_tab_out - overlap", "h"],
    sizes=["W", "L_feed + overlap - gap_foil", "t_cu"],
    name="FEED_TOP", material="copper")

# FEED_BOT: инсет gap_foil снизу (со стороны коннектора)
hfss.modeler.create_box(
    origin=["x_res - W/2", "-y_top_res + gap_foil", "h"],
    sizes=["W", "L_feed + overlap - gap_foil", "t_cu"],
    name="FEED_BOT", material="copper")

hfss.modeler.unite([tabs_final, "FEED_TOP", "FEED_BOT"])


# ================================================================
# 6. Коаксиальные разъёмы (Y = торец линии)
# ================================================================
def draw_coax_and_port(name, line_name, x_expr, x_num, y_edge_expr, y_edge_num, direction):
    if direction < 0:
        y_line_edge_expr = "({}) + gap_foil".format(y_edge_expr)
        pin_origin_y = "({}) - L_coax".format(y_edge_expr)
        pin_height = "L_coax + gap_foil + 1mm"
        coax_origin_y = "({}) - L_coax".format(y_edge_expr)
        y_outer_expr = "({}) - L_coax".format(y_edge_expr)

        wall_y_start = "({}) - conn_ins_depth".format(y_edge_expr)
        leg_y_start = "({}) - conn_ins_depth".format(y_edge_expr)
        cap_origin_y = "({}) - t_cu".format(y_outer_expr)
    else:
        y_line_edge_expr = "({}) - gap_foil".format(y_edge_expr)
        pin_origin_y = "({}) - 1mm".format(y_line_edge_expr)
        pin_height = "L_coax + gap_foil + 1mm"
        coax_origin_y = y_edge_expr
        y_outer_expr = "({}) + L_coax".format(y_edge_expr)

        wall_y_start = y_edge_expr
        leg_y_start = "({}) - conn_ins_depth".format(y_edge_expr)
        cap_origin_y = y_outer_expr

    pin = hfss.modeler.create_cylinder(orientation="Y", origin=[x_expr, pin_origin_y, "z_coax"], radius=r_pin_coax, height=pin_height, name="CoaxPin_{}".format(name), material="copper")
    coax_diel = hfss.modeler.create_cylinder(orientation="Y", origin=[x_expr, coax_origin_y, "z_coax"], radius=r_diel, height="L_coax", name="CoaxDiel_{}".format(name), material="PTFE")
    coax_outer = hfss.modeler.create_cylinder(orientation="Y", origin=[x_expr, coax_origin_y, "z_coax"], radius=r_outer, height="L_coax", name="CoaxOuter_{}".format(name), material="copper")

    cap = hfss.modeler.create_cylinder(orientation="Y", origin=[x_expr, cap_origin_y, "z_coax"], radius=r_outer, height="t_cu", name="PEC_Cap_{}".format(name), material="pec")
    hfss.modeler.subtract(cap.name, coax_diel.name, keep_originals=True)

    wall = hfss.modeler.create_box(
        origin=["({}) - conn_flange_w/2".format(x_expr), wall_y_start, "0mm"],
        sizes=["conn_flange_w", "conn_ins_depth", "conn_height"],
        name="Wall_{}".format(name), material="copper")
    hfss.modeler.subtract([coax_outer.name, wall.name], coax_diel.name, keep_originals=True)

    leg_y_size = "2*conn_ins_depth"
    leg_L = hfss.modeler.create_box(
        origin=["({}) - conn_flange_w/2".format(x_expr), leg_y_start, "h"],
        sizes=["leg_width", leg_y_size, "leg_height"],
        name="Leg_{}_L".format(name), material="copper")
    leg_R = hfss.modeler.create_box(
        origin=["({}) + conn_gnd_gap/2".format(x_expr), leg_y_start, "h"],
        sizes=["leg_width", leg_y_size, "leg_height"],
        name="Leg_{}_R".format(name), material="copper")

    port_y_num = y_edge_num + direction * L_coax_mm
    port_sheet = hfss.modeler.create_circle(orientation="XZ", origin=[x_expr, y_outer_expr, "z_coax"], radius=r_diel, name="PortSheet_{}".format(name))

    z_coax_num = h_mm + t_cu_mm - pin_z_overlap + r_pin_coax

    hfss.wave_port(
        assignment=port_sheet.name,
        integration_line=[[x_num, port_y_num, z_coax_num], [x_num, port_y_num, z_coax_num + r_diel]],
        name="P_{}".format(name),
        renormalize=False
    )

    return pin.name, cap.name, coax_diel.name, coax_outer.name, wall.name, leg_L.name, leg_R.name


p1_thru = draw_coax_and_port("THRU_1", "THRU_Line", "x_thru", x_thru_val, "-L_thru/2", -L_thru_val/2, -1)
p2_thru = draw_coax_and_port("THRU_2", "THRU_Line", "x_thru", x_thru_val, "L_thru/2", +L_thru_val/2, +1)

p1_line = draw_coax_and_port("LINE_1", "LINE_Line", "x_line", x_line_val, "-L_line/2", -L_line_val/2, -1)
p2_line = draw_coax_and_port("LINE_2", "LINE_Line", "x_line", x_line_val, "L_line/2", +L_line_val/2, +1)

p_open_a = draw_coax_and_port("OPEN_A", "OPEN_A_Line", "x_open", x_open_val, "-y_top_res", -y_top_res_val, -1)
p_open_b = draw_coax_and_port("OPEN_B", "OPEN_B_Line", "x_open", x_open_val, "y_top_res", +y_top_res_val, +1)

p1_res = draw_coax_and_port("RES_1", tabs_final, "x_res", x_res_val, "-y_top_res", -y_top_res_val, -1)
p2_res = draw_coax_and_port("RES_2", tabs_final, "x_res", x_res_val, "y_top_res", +y_top_res_val, +1)


# ================================================================
# 7. Объединение
# ================================================================
sig_parts = ["THRU_Line", "LINE_Line", "OPEN_A_Line", "OPEN_B_Line", tabs_final]
for p in [p1_thru, p2_thru, p1_line, p2_line, p_open_a, p_open_b, p1_res, p2_res]:
    sig_parts.extend([p[0]])
hfss.modeler.unite(sig_parts)

gnd_parts = [top_pad_name]
for p in [p1_thru, p2_thru, p1_line, p2_line, p_open_a, p_open_b, p1_res, p2_res]:
    gnd_parts.extend([p[3], p[4], p[5], p[6]])
hfss.modeler.unite(gnd_parts)


# ================================================================
# 8. Open Region + Setup + Sweep
# ================================================================
hfss.modeler.create_region(
    pad_value=["15mm", "15mm", "0.5mm", "0.5mm", "15mm", "0mm"],
    is_percentage=False,
    name="Region"
)
hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")

setup = hfss.create_setup("Setup_TRL")
setup.props["Frequency"] = "{}GHz".format(f0_ghz)
setup.props["MaximumPasses"] = 20
setup.props["MaxDeltaS"] = 0.02

sweep = setup.add_sweep("Sweep_1_15GHz")
sweep.props["RangeType"] = "LinearCount"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeEnd"] = "15GHz"
sweep.props["RangeCount"] = 141

hfss.save_project()
print("\nПроект сохранён (TRL_Res_Prod.py v1.4). gap_foil учтён для всей меди, включая линии.")


# === TRL_Res_Prod.py ===