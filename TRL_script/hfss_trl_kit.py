# -*- coding: utf-8 -*-
"""TRL + кольцевой резонатор на FR4 для HFSS 2025 (v3.5.6).

Изменения:
* После создания PEC_Wall_{name} он вычитается из GND_BOT
  (устранение пересечения в области z ∈ [-t_cu, 0]).
* Wave Port назначается на грань PEC-стенки через
  hfss.oboundary.AssignWavePort (Objects:=[], Faces:=[int]).
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

port_w_mm       = 10.0 * W_mm
port_h_mm       = 8.0 * h_mm
t_cap_mm        = t_cu_mm
line_overlap_mm = 0.005

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

hfss["port_w"]       = "{}mm".format(port_w_mm)
hfss["port_h"]       = "{}mm".format(port_h_mm)
hfss["t_cap"]        = "{}mm".format(t_cap_mm)
hfss["line_overlap"] = "{}mm".format(line_overlap_mm)

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

# Мостики
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
# 6. Поиск грани + PEC-стенки + Wave Port через AssignWavePort (Faces)
# ================================================================
def _parse_coord(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.replace("mm", "").replace("(", "").replace(")", "").strip()
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _get_face_y(obj_name, fid):
    """Y-координата центра грани (мм) или None."""
    try:
        c = hfss.modeler.oeditor.GetFaceCenter(fid)
        if c is not None:
            if isinstance(c, str) and "," in c:
                parts = c.replace("mm", "").replace("(", "").replace(")", "").split(",")
                y = _parse_coord(parts[1]) if len(parts) >= 2 else None
            elif isinstance(c, (list, tuple)) and len(c) >= 2:
                y = _parse_coord(c[1])
            else:
                y = _parse_coord(c)
            if y is not None:
                return y
    except Exception as e:
        print("[debug] GetFaceCenter({}) failed: {}".format(fid, e))

    try:
        verts = hfss.modeler.oeditor.GetFaceVertexPositions(fid)
        if verts:
            ys = []
            for v in verts:
                if isinstance(v, str) and "," in v:
                    parts = v.replace("mm", "").replace("(", "").replace(")", "").split(",")
                    if len(parts) >= 2:
                        y = _parse_coord(parts[1])
                        if y is not None:
                            ys.append(y)
                elif isinstance(v, (list, tuple)) and len(v) >= 2:
                    y = _parse_coord(v[1])
                    if y is not None:
                        ys.append(y)
            if ys:
                return sum(ys) / len(ys)
    except Exception as e:
        print("[debug] GetFaceVertexPositions({}) failed: {}".format(fid, e))

    return None


def find_face_at_y(obj_name, target_y, tol_mm=0.5):
    """Face ID грани объекта, центр которой по Y ≈ target_y (мм)."""
    try:
        face_ids = hfss.modeler.oeditor.GetFaceIDs(obj_name)
    except Exception as e:
        print("[warn] GetFaceIDs('{}') failed: {}".format(obj_name, e))
        return None

    if not face_ids:
        print("[warn] GetFaceIDs('{}') returned empty".format(obj_name))
        return None

    print("[debug] {}: {} faces, target_y = {:.3f} mm".format(
        obj_name, len(face_ids), target_y))

    best_fid = None
    best_dy = None

    for fid in face_ids:
        fid_str = str(fid)
        y = _get_face_y(obj_name, fid_str)
        if y is None:
            continue

        y_mm = y
        if abs(y) < 1.0 and abs(target_y) > 1.0:
            y_mm = y * 1000.0
        elif abs(y) > 1000.0 and abs(target_y) < 1000.0:
            y_mm = y / 1000.0

        dy = abs(y_mm - target_y)
        print("[debug]   face {}: y={:.6f} (mm={:.6f}), dy={:.6f}".format(
            fid_str, y, y_mm, dy))

        if dy < tol_mm and (best_dy is None or dy < best_dy):
            best_fid = fid_str
            best_dy = dy

    if best_fid is not None:
        print("[debug] best face: {} (dy={:.6f})".format(best_fid, best_dy))
    else:
        print("[warn] no face within tol={:.3f} mm".format(tol_mm))

    return best_fid


def create_port(name, x_num, y_num, line_name, direction):
    """PEC-стенка -> вычитание из GND_BOT -> unite с линией -> Wave Port."""
    if direction < 0:
        cap_y_start = y_num - t_cap_mm
        cap_y_size  = t_cap_mm + line_overlap_mm
    else:
        cap_y_start = y_num - line_overlap_mm
        cap_y_size  = t_cap_mm + line_overlap_mm

    cap = hfss.modeler.create_box(
        origin=["{:.6f}mm".format(x_num - port_w_mm / 2.0),
                "{:.6f}mm".format(cap_y_start),
                "{:.6f}mm".format(-t_cu_mm)],
        sizes=["{:.6f}mm".format(port_w_mm),
               "{:.6f}mm".format(cap_y_size),
               "{:.6f}mm".format(port_h_mm + t_cu_mm)],
        name="PEC_Wall_{}".format(name),
        material="pec"
    )

    # Вычитаем PEC_Wall из GND_BOT (устраняем пересечение)
    try:
        hfss.modeler.subtract(gnd_bot_name, cap.name, keep_originals=True)
        print("[debug] PEC_Wall_{0} вычтен из {1}".format(name, gnd_bot_name))
    except Exception as e:
        print("[warn] subtract({0}, PEC_Wall_{1}) failed: {2}".format(
            gnd_bot_name, name, e))

    res = hfss.modeler.unite([line_name, cap.name])
    obj_name = res if isinstance(res, str) else line_name

    face_id = find_face_at_y(obj_name, y_num, tol_mm=0.5)
    if face_id is None:
        print("[error] порт {} НЕ создан: грань на y={:.6f} не найдена".format(name, y_num))
        return

    port_name = "P_{}".format(name)
    face_int = int(face_id) if str(face_id).isdigit() else face_id

    props = [
        "NAME:" + port_name,
        "Objects:=", [],
        "Faces:=", [face_int],
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
                "Start:=", [
                    "{:.6f}mm".format(x_num),
                    "{:.6f}mm".format(y_num),
                    "{:.6f}mm".format(h_mm)
                ],
                "End:=", [
                    "{:.6f}mm".format(x_num),
                    "{:.6f}mm".format(y_num),
                    "0mm"
                ]
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
        print("[warn] hfss.oboundary.AssignWavePort failed: {}, trying oeditor".format(e1))
        try:
            hfss.modeler.oeditor.AssignWavePort(props)
        except Exception as e2:
            print("[error] oeditor.AssignWavePort failed: {}".format(e2))
            return

    print("[port {0:8s}] face_id={1}, obj='{2}', X={3:.6f}, Y={4:.6f}, Z_top={5:.6f}"
          .format(name, face_id, obj_name, x_num, y_num, port_h_mm))


create_port("THRU_1",  x_thru_val, -L_thru_val / 2.0, "THRU_Line",  -1)
create_port("THRU_2",  x_thru_val, +L_thru_val / 2.0, "THRU_Line",  +1)

create_port("LINE_1",  x_line_val, -L_line_val / 2.0, "LINE_Line",  -1)
create_port("LINE_2",  x_line_val, +L_line_val / 2.0, "LINE_Line",  +1)

create_port("OPEN_A",  x_open_val, -L_line_val / 2.0, "OPEN_A_Line", -1)
create_port("OPEN_B",  x_open_val, +L_line_val / 2.0, "OPEN_B_Line", +1)

create_port("RES_1",   x_res_val, -y_top_res_val, tabs_final, -1)
create_port("RES_2",   x_res_val, +y_top_res_val, tabs_final, +1)


# ================================================================
# 7. Open Region (padding ±Y = 0.5 мм — PEC-стенка внутри Region)
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
print("\nПроект сохранён (v3.5.6). PEC-Wall вычитается из GND_BOT.")


# === hfss_trl_kit.py ===