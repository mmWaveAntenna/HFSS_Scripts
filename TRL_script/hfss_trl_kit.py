# -*- coding: utf-8 -*-
"""TRL + кольцевой резонатор на FR4 для HFSS 2025 (v3.6.1).

Изменения:
* Исправлен порядок размеров в create_rectangle(orientation="XZ"):
  sizes=["port_h", "port_w"] (ZSize=port_h, XSize=port_w).
  Раньше было ["port_w", "port_h"], из-за чего порт был повернут на 90°.
* Порты полностью параметризованы (HFSS-выражения в sheet и IntLine).
* Размер порта уменьшен до 4W × 3h (6.8 × 2.79 мм) — без высших мод.
* PEC-cap (3D box pec) на 0.1 мм за портом, вычитается из GND_BOT.
* Wave Port на sheet через hfss.oboundary.AssignWavePort.
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

h_mm        = 0.93
W_mm        = 1.7
t_cu_mm     = 0.035
er_val      = 4.4
tan_d_val   = 0.02
L_thru_mm   = 10.0
f0_ghz      = 10.0
gap_mm      = 50.0

pitch_trl_mm = 25.0
pitch_res_mm = 25.0

W_ring_mm     = 0.4
R_tab_mm      = 0.4
W_tab_mm      = 1.7
gap_couple_mm = 0.2
overlap_mm    = 0.5
x_overlap_mm  = 1.0
gap_foil_mm   = 0.2

# Размеры портов (HFSS-выражения)
port_w_expr = "4*W"   # 6.8 мм
port_h_expr = "3*h"   # 2.79 мм
port_gap_mm = 0.1     # зазор PEC-cap от порта

# x_margin — на основе численного port_w (для габаритов подложки)
port_w_mm = 4.0 * W_mm
x_margin_mm = (port_w_mm - W_mm) / 2.0 + 1.0

# --- Предвычисления ---
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

# Порт — HFSS-выражения
hfss["port_w"]   = port_w_expr
hfss["port_h"]   = port_h_expr
hfss["t_cap"]    = "t_cu"
hfss["port_gap"] = "{}mm".format(port_gap_mm)

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
# 4. Подложка и нижняя земля
# ================================================================
sub_parts = []
gnd_bot_parts = []

def add_pcb_block(name_sub, name_gnd, x0, y0, dx, dy):
    hfss.modeler.create_box(origin=[x0, y0, "0mm"], sizes=[dx, dy, "h"], name=name_sub, material="FR4_Custom")
    sub_parts.append(name_sub)
    hfss.modeler.create_box(origin=[x0, y0, "-t_cu"], sizes=[dx, dy, "t_cu"], name=name_gnd, material="copper")
    gnd_bot_parts.append(name_gnd)

add_pcb_block("Substrate_FR4", "GND_BOT", "x_thru - W/2 - x_margin", "-L_thru/2", "W + 2*x_margin", "L_thru")
add_pcb_block("Sub_LINE", "GND_LINE", "x_line - W/2 - x_margin", "-L_line/2", "W + 2*x_margin", "L_line")
add_pcb_block("Sub_OPEN", "GND_OPEN", "x_open - W/2 - x_margin", "-L_line/2", "W + 2*x_margin", "L_line")
add_pcb_block("Sub_RES", "GND_RES", "x_res - r_tab_out - x_margin", "-y_top_res", "2*(r_tab_out + x_margin)", "2*y_top_res")

hfss.modeler.create_box(origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2", "0mm"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_thru", "h"], name="Bridge_1", material="FR4_Custom")
sub_parts.append("Bridge_1")
hfss.modeler.create_box(origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2", "-t_cu"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_thru", "t_cu"], name="GND_Bridge_1", material="copper")
gnd_bot_parts.append("GND_Bridge_1")

hfss.modeler.create_box(origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2", "0mm"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "h"], name="Bridge_2", material="FR4_Custom")
sub_parts.append("Bridge_2")
hfss.modeler.create_box(origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2", "-t_cu"], sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "t_cu"], name="GND_Bridge_2", material="copper")
gnd_bot_parts.append("GND_Bridge_2")

hfss.modeler.create_box(origin=["x_open + W/2 + x_margin - x_overlap", "-L_line/2", "0mm"], sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "h"], name="Bridge_3", material="FR4_Custom")
sub_parts.append("Bridge_3")
hfss.modeler.create_box(origin=["x_open + W/2 + x_margin - x_overlap", "-L_line/2", "-t_cu"], sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "t_cu"], name="GND_Bridge_3", material="copper")
gnd_bot_parts.append("GND_Bridge_3")

hfss.modeler.unite(sub_parts)
res_gnd_bot = hfss.modeler.unite(gnd_bot_parts)
gnd_bot_name = res_gnd_bot if isinstance(res_gnd_bot, str) else gnd_bot_parts[0]


# ================================================================
# 5. Металлизация: TRL + резонатор
# ================================================================
hfss.modeler.create_box(origin=["x_thru - W/2", "-L_thru/2", "h"], sizes=["W", "L_thru", "t_cu"], name="THRU_Line", material="copper")
hfss.modeler.create_box(origin=["x_line - W/2", "-L_line/2", "h"], sizes=["W", "L_line", "t_cu"], name="LINE_Line", material="copper")
hfss.modeler.create_box(origin=["x_open - W/2", "-L_line/2", "h"], sizes=["W", "L_ref", "t_cu"], name="OPEN_A_Line", material="copper")
hfss.modeler.create_box(origin=["x_open - W/2", "L_line/2 - L_ref", "h"], sizes=["W", "L_ref", "t_cu"], name="OPEN_B_Line", material="copper")

hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_out", height="t_cu", name="RING_OUT", material="copper")
hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_in", height="t_cu", name="RING_IN", material="vacuum")
hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)

hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_out", height="t_cu", name="RING_TAB_OUT", material="copper")
hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_in", height="t_cu", name="RING_TAB_IN", material="vacuum")
hfss.modeler.subtract("RING_TAB_OUT", "RING_TAB_IN", keep_originals=False)

hfss.modeler.create_box(origin=["x_res - W_tab/2", "-r_tab_out - 1mm", "h"], sizes=["W_tab", "2*r_tab_out + 2mm", "t_cu"], name="TAB_BOX", material="copper")

res = hfss.modeler.intersect(["TAB_BOX", "RING_TAB_OUT"], keep_originals=False)
tabs_final = res if isinstance(res, str) else (res[0] if isinstance(res, (list, tuple)) else "TAB_BOX")

hfss.modeler.create_box(origin=["x_res - W/2", "r_tab_out - overlap", "h"], sizes=["W", "L_feed + overlap", "t_cu"], name="FEED_TOP", material="copper")
hfss.modeler.create_box(origin=["x_res - W/2", "-r_tab_out - L_feed", "h"], sizes=["W", "L_feed + overlap", "t_cu"], name="FEED_BOT", material="copper")
hfss.modeler.unite([tabs_final, "FEED_TOP", "FEED_BOT"])


# ================================================================
# 6. Параметризованные Wave Ports (HFSS-выражения)
# ================================================================
def create_port(name, x_expr, y_expr, direction):
    """Sheet-порт в XZ-plane + PEC-cap за ним.
    sizes=["port_h", "port_w"] — порядок Z, X (исправлено)."""
    sheet = hfss.modeler.create_rectangle(
        orientation="XZ",
        origin=["({}) - port_w/2".format(x_expr), y_expr, "0mm"],
        sizes=["port_h", "port_w"],
        name="PortSheet_{}".format(name)
    )

    # PEC-cap на 0.1 мм за портом
    if direction < 0:
        cap_y = "({}) - port_gap - t_cap".format(y_expr)
    else:
        cap_y = "({}) + port_gap".format(y_expr)

    cap = hfss.modeler.create_box(
        origin=["({}) - port_w/2".format(x_expr), cap_y, "-t_cu"],
        sizes=["port_w", "t_cap", "t_cu + port_h"],
        name="PEC_Cap_{}".format(name),
        material="pec"
    )

    # Вычитание PEC-cap из GND_BOT
    try:
        hfss.modeler.subtract(gnd_bot_name, cap.name, keep_originals=True)
    except Exception as e:
        print("[warn] subtract({}, PEC_Cap_{}) failed: {}".format(
            gnd_bot_name, name, e))

    # Wave Port на sheet через AssignWavePort (IntLine — выражения)
    port_name = "P_" + name
    props = [
        "NAME:" + port_name,
        "Objects:=", [sheet.name],
        "NumModes:=", 1,
        "UseLineModeAlignment:=", False,
        "DoDeembed:=", False,
        "RenormalizeAllTerminals:=", False,
        "Modes:=", [
            "NAME:Mode1",
            "ModeNum:=", 1,
            "UseIntLine:=", True,
            "IntLine:=", [
                "NAME:IntLine",
                "Start:=", [x_expr, y_expr, "h"],
                "End:=",   [x_expr, y_expr, "0mm"],
            ],
            "AlignmentGroup:=", 0,
            "CharImp:=", "Zpi"
        ],
        "ShowReporterFilter:=", False,
        "ReporterFilter:=", [True],
        "UseAnalyticAlignment:=", False
    ]

    try:
        hfss.oboundary.AssignWavePort(props)
    except Exception as e1:
        print("[warn] oboundary.AssignWavePort failed: {}".format(e1))
        try:
            hfss.modeler.oeditor.AssignWavePort(props)
        except Exception as e2:
            print("[error] oeditor.AssignWavePort failed: {}".format(e2))
            return

    print("[port {0:8s}] sheet={1}, x_expr={2}, y_expr={3}".format(
        name, sheet.name, x_expr, y_expr))


create_port("THRU_1", "x_thru", "-L_thru/2", -1)
create_port("THRU_2", "x_thru", "L_thru/2",  +1)

create_port("LINE_1", "x_line", "-L_line/2", -1)
create_port("LINE_2", "x_line", "L_line/2",  +1)

create_port("OPEN_A", "x_open", "-L_line/2", -1)
create_port("OPEN_B", "x_open", "L_line/2",  +1)

create_port("RES_1",  "x_res",  "-y_top_res", -1)
create_port("RES_2",  "x_res",  "y_top_res",  +1)


# ================================================================
# 7. Open Region
# ================================================================
hfss.modeler.create_region(
    pad_value=["15mm", "15mm", "0.5mm", "0.5mm", "15mm", "0mm"],
    is_percentage=False,
    name="Region"
)
hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")


# ================================================================
# 8. Setup + Sweep
# ================================================================
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
print("\nПроект сохранён (v3.6.1). Порты 6.8 × 2.79 мм, параметризованы.")


# === hfss_trl_kit.py ===