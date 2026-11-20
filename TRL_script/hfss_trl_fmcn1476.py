# -*- coding: utf-8 -*-
"""TRL + кольцевой резонатор на FR4 с вертикальными ВЧ-разъёмами Fairview Microwave FMCN1476 (v2.0.0).

Геометрия разъёма и посадочного места (Recommended Top/Bottom PCB Pattern)
построена строго по официальному чертежу Fairview Microwave FMCN1476 (Rev 06/04/18):
* Фланец крепления: диаметр Ø 9.90 мм со срезанными лысками шириной 5.64 мм,
  два крепёжных отверстия 2-Ø 1.60 мм (под винты M1.6x0.35) с шагом 7.16 мм.
* Верхнее посадочное место (Recommended Top PCB Pattern):
  - габарит заземляющего полигона под фланец: 6.24 × 10.50 мм (вырез/выемка шириной 2.40 мм под подводящую линию);
  - согласующий вырез в земле вокруг микрополоска: ширина 0.43 мм до зазора 0.95 мм от края полигона;
  - округлый вырез земли вокруг центрального пина: R 0.28 мм, сдвиг от выреза 1.00 мм;
  - переходные земляные отверстия (via): Ø 0.25 мм по периметру выреза и дуге вокруг пина.
* Нижний слой (Recommended Bottom PCB Pattern):
  - круглый антипад (Bottom Conductor cut out): Ø 0.96 мм (радиус 0.48 мм) строго под центральным пином.
* Контактный пин (DETAIL A): диаметр Ø 0.35 мм (радиус 0.175 мм), выступание над базой 0.05 мм,
  ступенчатый переход в воздушный коаксиал 2.92 мм (Ø 1.27 / 2.92 мм).
* Учтены правила проекта: развязка открытых концов OPEN (DL-58), строгий порядок булевых
  вычитаний в коаксиале (DL-45), волновые порты с renormalize=False (DL-46).
"""

import math

try:
    from pyaedt import Hfss
except ImportError:
    from ansys.aedt.core import Hfss


# ================================================================
# 1. Параметры платы, TRL, резонатора и разъёма FMCN1476 (по чертежу)
# ================================================================
PROJECT_NAME = "TRL_Calibration_FR4_FMCN1476"
DESIGN_NAME  = "TRL_Kit_FMCN1476"

# Подложка FR4 и микрополосок 50 Ом
h_mm        = 0.93
W_mm        = 1.7
t_cu_mm     = 0.035
er_val      = 4.4
tan_d_val   = 0.02
L_thru_mm   = 10.0
f0_ghz      = 10.0

pitch_trl_mm = 25.0
pitch_res_mm = 25.0
x_overlap_mm = 1.0

# Кольцевой резонатор (n = 1)
W_ring_mm     = 0.4
R_tab_mm      = 0.4
W_tab_mm      = 1.7
gap_couple_mm = 0.2
overlap_mm    = 0.5

# --- Точные размеры разъёма FMCN1476 из чертежа (мм) ---
# Корпус и фланец (сверху и сбоку)
fm_total_len_mm   = 11.21   # полная высота разъёма над платой (0.441 in)
fm_thread_start_mm = 1.72   # начало резьбовой/коаксиальной части (11.21 - 9.49 = 1.72 мм)
fm_flange_dia_mm  = 9.90    # наружный диаметр круглого фланца (Ø 0.390 in)
fm_flange_flat_mm = 5.64    # ширина фланца по лыскам (0.222 in)
fm_flange_h_mm    = 1.65    # толщина основания фланца над платой (11.21 - 9.49 - 0.07)
fm_boss_dia_mm    = 3.50    # диаметр выступающей втулки у основания (Ø 0.138 in)
fm_boss_h_mm      = 0.07    # высота выступа втулки (0.003 in)
fm_hole_pitch_mm  = 7.16    # шаг крепёжных винтов M1.6 (0.282 in)
fm_hole_dia_mm    = 1.60    # диаметр крепёжных отверстий в ПП (2-Ø 0.06 Thru)

# Деталь А (DETAIL A) и коаксиал 2.92 мм
fm_pin_tip_dia_mm = 0.35    # диаметр контактного пина на плате (Ø 0.014 in)
fm_pin_step_dia_mm = 1.27   # диаметр центрального проводника внутри коаксиала 2.92 мм (Ø 0.050 in)
fm_diel_dia_mm    = 2.92    # внутренний диаметр внешнего проводника 2.92 мм
fm_slot_w_mm      = 1.50    # ширина паза/окна в основании втулки над линией (0.059 in)
pin_pen_mm        = 0.015   # заглубление пина в медный слой линии для контакта (DL-30)

# Посадочное место на печатной плате (Recommended Top & Bottom PCB Pattern)
pad_top_w_mm      = 10.50   # поперечный размер верхнего полигона земли (0.41 in)
pad_top_l_mm      = 6.24    # продольный размер верхнего полигона земли (0.25 in)
pad_notch_w_mm    = 2.40    # ширина входного выреза в верхнем полигоне (0.09 in)
pad_notch_l_mm    = 0.95    # глубина входного выреза в верхнем полигоне (0.04 in)
pad_gap_line_mm   = 0.43    # зазор с каждой стороны микрополоска в канале полигона (0.02 in)
pad_pin_cut_r_mm  = 0.28    # радиус выреза вокруг центрального пина на верхнем слое (R 0.01 in)
pad_pin_off_mm    = 1.00    # сдвиг центра пина от конца входного выреза (0.04 in)
bottom_cut_dia_mm = 0.96    # диаметр круглого выреза в нижней земле (Ø 0.04 Bottom Conductor cut out)
via_dia_mm        = 0.25    # диаметр земляных переходных отверстий (Ø 0.01 via)

# Поля подложки под установку фланца FMCN1476
conn_y_ext_mm     = 4.50
x_margin_mm       = (pad_top_w_mm - W_mm) / 2.0 + 1.0


# ================================================================
# 2. Инициализация HFSS 2025
# ================================================================
hfss = Hfss(project=PROJECT_NAME, design=DESIGN_NAME,
            solution_type="DrivenModal", new_desktop=True)
hfss.modeler.model_units = "mm"


# ================================================================
# 3. Материалы и переменные дизайна HFSS
# ================================================================
if "FR4_Custom" not in hfss.materials.material_keys:
    fr4 = hfss.materials.add_material("FR4_Custom")
    fr4.permittivity = er_val
    fr4.dielectric_loss_tangent = tan_d_val

# Параметры платы и СВЧ-структур
hfss["h"]          = "{}mm".format(h_mm)
hfss["W"]          = "{}mm".format(W_mm)
hfss["t_cu"]       = "{}mm".format(t_cu_mm)
hfss["er"]         = "{}".format(er_val)
hfss["f0_GHz"]     = "{}".format(f0_ghz)
hfss["L_thru"]     = "{}mm".format(L_thru_mm)
hfss["x_margin"]   = "{}mm".format(x_margin_mm)
hfss["x_overlap"]  = "{}mm".format(x_overlap_mm)
hfss["pitch_trl"]  = "{}mm".format(pitch_trl_mm)
hfss["pitch_res"]  = "{}mm".format(pitch_res_mm)

hfss["W_ring"]     = "{}mm".format(W_ring_mm)
hfss["W_tab"]      = "{}mm".format(W_tab_mm)
hfss["R_tab"]      = "{}mm".format(R_tab_mm)
hfss["gap_couple"] = "{}mm".format(gap_couple_mm)
hfss["overlap"]    = "{}mm".format(overlap_mm)

# Переменные разъёма FMCN1476 (строго по чертежу)
hfss["fm_total_h"]    = "{}mm".format(fm_total_len_mm)
hfss["fm_flange_r"]   = "{}mm".format(fm_flange_dia_mm / 2.0)
hfss["fm_flange_w"]   = "{}mm".format(fm_flange_flat_mm)
hfss["fm_flange_h"]   = "{}mm".format(fm_flange_h_mm)
hfss["fm_boss_r"]     = "{}mm".format(fm_boss_dia_mm / 2.0)
hfss["fm_boss_h"]     = "{}mm".format(fm_boss_h_mm)
hfss["fm_hole_pitch"] = "{}mm".format(fm_hole_pitch_mm)
hfss["fm_hole_r"]     = "{}mm".format(fm_hole_dia_mm / 2.0)

hfss["r_pin_tip"]     = "{}mm".format(fm_pin_tip_dia_mm / 2.0)
hfss["r_pin_coax"]    = "{}mm".format(fm_pin_step_dia_mm / 2.0)
hfss["r_outer_coax"]  = "{}mm".format(fm_diel_dia_mm / 2.0)
hfss["fm_slot_w"]     = "{}mm".format(fm_slot_w_mm)
hfss["pin_pen"]       = "{}mm".format(pin_pen_mm)

# Переменные посадочного места (Top & Bottom PCB Pattern)
hfss["pad_top_w"]     = "{}mm".format(pad_top_w_mm)
hfss["pad_top_l"]     = "{}mm".format(pad_top_l_mm)
hfss["pad_notch_w"]   = "{}mm".format(pad_notch_w_mm)
hfss["pad_notch_l"]   = "{}mm".format(pad_notch_l_mm)
hfss["pad_gap_line"]  = "{}mm".format(pad_gap_line_mm)
hfss["pad_pin_cut_r"] = "{}mm".format(pad_pin_cut_r_mm)
hfss["pad_pin_off"]   = "{}mm".format(pad_pin_off_mm)
hfss["bot_cut_r"]     = "{}mm".format(bottom_cut_dia_mm / 2.0)
hfss["via_r"]         = "{}mm".format(via_dia_mm / 2.0)
hfss["c_y_ext"]       = "{}mm".format(conn_y_ext_mm)

# Зависимые формулы TRL и резонатора
hfss["L_ref"]     = "L_thru/2"
hfss["L_feed"]    = "L_thru/2"
hfss["eps_eff"]   = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"
hfss["dL"]        = "75mm/(f0_GHz*sqrt(eps_eff))"
hfss["L_line"]    = "L_thru + dL"

hfss["eps_ring"]  = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"
hfss["r_mean"]    = "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"
hfss["r_out"]     = "r_mean + W_ring/2"
hfss["r_in"]      = "r_mean - W_ring/2"
hfss["r_tab_in"]  = "r_out + gap_couple"
hfss["r_tab_out"] = "r_tab_in + R_tab"
hfss["y_top_res"] = "r_tab_out + L_feed"

# Координаты центров структур по X
hfss["x_thru"]  = "-pitch_trl"
hfss["x_line"]  = "0mm"
hfss["x_open"]  = "pitch_trl"
hfss["x_res"]   = "pitch_trl + pitch_res"


# ================================================================
# 4. Подложка FR4 и нижняя земля (контур платы + перемычки)
# ================================================================
sub_parts = []
gnd_bot_parts = []


def add_pcb_block(name_sub, name_gnd, x0, y0, dx, dy):
    hfss.modeler.create_box(
        origin=[x0, y0, "0mm"], sizes=[dx, dy, "h"],
        name=name_sub, material="FR4_Custom"
    )
    sub_parts.append(name_sub)
    hfss.modeler.create_box(
        origin=[x0, y0, "-t_cu"], sizes=[dx, dy, "t_cu"],
        name=name_gnd, material="copper"
    )
    gnd_bot_parts.append(name_gnd)


add_pcb_block(
    "Substrate_FR4", "GND_BOT",
    "x_thru - W/2 - x_margin", "-L_thru/2 - c_y_ext",
    "W + 2*x_margin", "L_thru + 2*c_y_ext"
)
add_pcb_block(
    "Sub_LINE", "GND_LINE",
    "x_line - W/2 - x_margin", "-L_line/2 - c_y_ext",
    "W + 2*x_margin", "L_line + 2*c_y_ext"
)
# OPEN выровнен по Y с RES для максимальной развязки открытых концов (DL-58)
add_pcb_block(
    "Sub_OPEN", "GND_OPEN",
    "x_open - W/2 - x_margin", "-y_top_res - c_y_ext",
    "W + 2*x_margin", "2*y_top_res + 2*c_y_ext"
)
add_pcb_block(
    "Sub_RES", "GND_RES",
    "x_res - r_tab_out - x_margin", "-y_top_res - c_y_ext",
    "2*(r_tab_out + x_margin)", "2*y_top_res + 2*c_y_ext"
)

# Перемычки между блоками
hfss.modeler.create_box(
    origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2", "0mm"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_thru", "h"],
    name="Bridge_1", material="FR4_Custom"
)
sub_parts.append("Bridge_1")
hfss.modeler.create_box(
    origin=["x_thru + W/2 + x_margin - x_overlap", "-L_thru/2", "-t_cu"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_thru", "t_cu"],
    name="GND_Bridge_1", material="copper"
)
gnd_bot_parts.append("GND_Bridge_1")

hfss.modeler.create_box(
    origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2", "0mm"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "h"],
    name="Bridge_2", material="FR4_Custom"
)
sub_parts.append("Bridge_2")
hfss.modeler.create_box(
    origin=["x_line + W/2 + x_margin - x_overlap", "-L_line/2", "-t_cu"],
    sizes=["max(pitch_trl - W - 2*x_margin + 2*x_overlap, 0.1mm)", "L_line", "t_cu"],
    name="GND_Bridge_2", material="copper"
)
gnd_bot_parts.append("GND_Bridge_2")

hfss.modeler.create_box(
    origin=["x_open + W/2 + x_margin - x_overlap", "-y_top_res", "0mm"],
    sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "2*y_top_res", "h"],
    name="Bridge_3", material="FR4_Custom"
)
sub_parts.append("Bridge_3")
hfss.modeler.create_box(
    origin=["x_open + W/2 + x_margin - x_overlap", "-y_top_res", "-t_cu"],
    sizes=["max(pitch_res - r_tab_out - W/2 - 2*x_margin + 2*x_overlap, 0.1mm)", "2*y_top_res", "t_cu"],
    name="GND_Bridge_3", material="copper"
)
gnd_bot_parts.append("GND_Bridge_3")

res_sub = hfss.modeler.unite(sub_parts)
sub_name = res_sub if isinstance(res_sub, str) else sub_parts[0]

res_gnd = hfss.modeler.unite(gnd_bot_parts)
gnd_bot_name = res_gnd if isinstance(res_gnd, str) else gnd_bot_parts[0]


# ================================================================
# 5. Металлизация: TRL + кольцевой резонатор
# ================================================================
hfss.modeler.create_box(
    origin=["x_thru - W/2", "-L_thru/2", "h"],
    sizes=["W", "L_thru", "t_cu"], name="THRU_Line", material="copper"
)
hfss.modeler.create_box(
    origin=["x_line - W/2", "-L_line/2", "h"],
    sizes=["W", "L_line", "t_cu"], name="LINE_Line", material="copper"
)
hfss.modeler.create_box(
    origin=["x_open - W/2", "-y_top_res", "h"],
    sizes=["W", "L_ref", "t_cu"], name="OPEN_A_Line", material="copper"
)
hfss.modeler.create_box(
    origin=["x_open - W/2", "y_top_res - L_ref", "h"],
    sizes=["W", "L_ref", "t_cu"], name="OPEN_B_Line", material="copper"
)

# Кольцо резонатора
hfss.modeler.create_cylinder(
    orientation="Z", origin=["x_res", "0mm", "h"],
    radius="r_out", height="t_cu", name="RING_OUT", material="copper"
)
hfss.modeler.create_cylinder(
    orientation="Z", origin=["x_res", "0mm", "h"],
    radius="r_in", height="t_cu", name="RING_IN", material="vacuum"
)
hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)

# T-лапки и фидеры резонатора
hfss.modeler.create_cylinder(
    orientation="Z", origin=["x_res", "0mm", "h"],
    radius="r_tab_out", height="t_cu", name="RING_TAB_OUT", material="copper"
)
hfss.modeler.create_cylinder(
    orientation="Z", origin=["x_res", "0mm", "h"],
    radius="r_tab_in", height="t_cu", name="RING_TAB_IN", material="vacuum"
)
hfss.modeler.subtract("RING_TAB_OUT", "RING_TAB_IN", keep_originals=False)

hfss.modeler.create_box(
    origin=["x_res - W_tab/2", "-r_tab_out - 1mm", "h"],
    sizes=["W_tab", "2*r_tab_out + 2mm", "t_cu"], name="TAB_BOX", material="copper"
)
res_tab = hfss.modeler.intersect(["TAB_BOX", "RING_TAB_OUT"], keep_originals=False)
tabs_final = res_tab if isinstance(res_tab, str) else "TAB_BOX"

hfss.modeler.create_box(
    origin=["x_res - W/2", "r_tab_out - overlap", "h"],
    sizes=["W", "L_feed + overlap", "t_cu"], name="FEED_TOP", material="copper"
)
hfss.modeler.create_box(
    origin=["x_res - W/2", "-r_tab_out - L_feed", "h"],
    sizes=["W", "L_feed + overlap", "t_cu"], name="FEED_BOT", material="copper"
)
res_res = hfss.modeler.unite([tabs_final, "FEED_TOP", "FEED_BOT"])
res_feed_name = res_res if isinstance(res_res, str) else tabs_final


# ================================================================
# 6. Построитель FMCN1476 (Recommended Top/Bottom PCB Pattern + 3D корпус)
# ================================================================
def build_fmcn1476_connector(name, x_expr, y_expr, dir_sign):
    """Создаёт 3D-модель разъёма Fairview Microwave FMCN1476 (2.92 мм Vertical Launch)
    и рекомендуемый футпринт (Recommended Top & Bottom PCB Pattern) по чертежу:
    - dir_sign = -1 для нижнего края (линия уходит в +Y);
    - dir_sign = +1 для верхнего края (линия уходит в -Y).
    """
    z_top_port = "h + fm_total_h"

    # ------------------------------------------------------------
    # 6.1. Верхний заземляющий полигон (Recommended Top PCB Pattern)
    # ------------------------------------------------------------
    # Полигон 10.50 × 6.24 мм смещён так, чтобы входной вырез (глубиной 0.95 мм + 1.00 мм до пина)
    # открывался в сторону микрополосковой линии (dir_sign).
    # Центр пина находится на расстоянии (pad_notch_l + pad_pin_off = 1.95 мм) от края полигона со стороны линии.
    if dir_sign < 0:
        poly_y0 = "({}) - (pad_top_l - pad_notch_l - pad_pin_off)".format(y_expr)
        notch_y0 = "({}) + pad_pin_off".format(y_expr)
        chan_y0 = "({})".format(y_expr)
    else:
        poly_y0 = "({}) - (pad_notch_l + pad_pin_off)".format(y_expr)
        notch_y0 = "({}) - pad_pin_off - pad_notch_l".format(y_expr)
        chan_y0 = "({}) - (pad_notch_l + pad_pin_off)".format(y_expr)

    top_gnd = hfss.modeler.create_box(
        origin=["({}) - pad_top_w/2".format(x_expr), poly_y0, "h"],
        sizes=["pad_top_w", "pad_top_l", "t_cu"],
        name="TopGnd_{}".format(name),
        material="copper"
    )

    # Входной вырез шириной 2.40 мм и глубиной 0.95 мм со стороны линии
    notch_cut = hfss.modeler.create_box(
        origin=["({}) - pad_notch_w/2".format(x_expr), notch_y0, "h - 0.01mm"],
        sizes=["pad_notch_w", "pad_notch_l", "t_cu + 0.02mm"],
        name="TopNotch_{}".format(name),
        material="vacuum"
    )
    hfss.modeler.subtract(top_gnd.name, notch_cut.name, keep_originals=False)

    # Узкий канал вокруг микрополоска шириной (W + 2*0.43 мм) до центра пина
    chan_cut = hfss.modeler.create_box(
        origin=["({}) - W/2 - pad_gap_line".format(x_expr), chan_y0, "h - 0.01mm"],
        sizes=["W + 2*pad_gap_line", "pad_notch_l + pad_pin_off", "t_cu + 0.02mm"],
        name="TopChan_{}".format(name),
        material="vacuum"
    )
    hfss.modeler.subtract(top_gnd.name, chan_cut.name, keep_originals=False)

    # Круглый вырез R = 0.28 мм вокруг центрального пина на верхнем слое
    pin_clear = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h - 0.01mm"],
        radius="pad_pin_cut_r",
        height="t_cu + 0.02mm",
        name="TopPinClear_{}".format(name),
        material="vacuum"
    )
    hfss.modeler.subtract(top_gnd.name, pin_clear.name, keep_originals=False)

    # ------------------------------------------------------------
    # 6.2. Нижний круглый вырез в GND_BOT (Bottom Conductor cut out Ø 0.96 мм)
    # ------------------------------------------------------------
    bot_cut = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "-t_cu - 0.02mm"],
        radius="bot_cut_r",
        height="t_cu + 0.04mm",
        name="BotCutOut_{}".format(name),
        material="vacuum"
    )
    hfss.modeler.subtract(gnd_bot_name, bot_cut.name, keep_originals=False)

    # ------------------------------------------------------------
    # 6.3. Металлический корпус/фланец FMCN1476 со срезанными лысками (9.90 / 5.64 мм)
    # ------------------------------------------------------------
    flange_cyl = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu"],
        radius="fm_flange_r",
        height="fm_flange_h",
        name="Flange_{}".format(name),
        material="stainless steel"
    )
    flange_flat_box = hfss.modeler.create_box(
        origin=["({}) - fm_flange_r - 1mm".format(x_expr), "({}) - fm_flange_w/2".format(y_expr), "h + t_cu"],
        sizes=["2*fm_flange_r + 2mm", "fm_flange_w", "fm_flange_h"],
        name="FlangeFlat_{}".format(name),
        material="stainless steel"
    )
    hfss.modeler.intersect([flange_cyl.name, flange_flat_box.name], keep_originals=False)

    # Нижняя цилиндрическая втулка фланца (Ø 3.50 мм) с пазом шириной 1.50 мм над линией
    boss = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu - fm_boss_h"],
        radius="fm_boss_r",
        height="fm_boss_h + 0.05mm",
        name="Boss_{}".format(name),
        material="stainless steel"
    )
    hfss.modeler.unite([flange_cyl.name, boss.name])

    # Паз шириной 1.50 мм в нижней части корпуса со стороны линии (чтобы не закоротить микрополосок)
    if dir_sign < 0:
        slot_y0 = "({}) - 0.2mm".format(y_expr)
    else:
        slot_y0 = "({}) - fm_flange_r - 0.5mm".format(y_expr)

    body_slot = hfss.modeler.create_box(
        origin=["({}) - fm_slot_w/2".format(x_expr), slot_y0, "h"],
        sizes=["fm_slot_w", "fm_flange_r + 0.7mm", "t_cu + 0.35mm"],
        name="BodySlot_{}".format(name),
        material="vacuum"
    )
    hfss.modeler.subtract(flange_cyl.name, body_slot.name, keep_originals=False)

    # Внешний цилиндр коаксиальной части 2.92 мм (до высоты 11.21 мм)
    coax_body = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu + fm_flange_h"],
        radius="r_outer_coax + 1.2mm",
        height="fm_total_h - t_cu - fm_flange_h",
        name="CoaxOuter_{}".format(name),
        material="stainless steel"
    )
    hfss.modeler.unite([flange_cyl.name, coax_body.name])

    # ------------------------------------------------------------
    # 6.4. Воздушный диэлектрик коаксиала и ступенчатый пин (DETAIL A)
    # ------------------------------------------------------------
    # Воздушная полость коаксиала
    coax_diel = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu + 0.05mm"],
        radius="r_outer_coax",
        height="fm_total_h - t_cu - 0.05mm",
        name="CoaxDiel_{}".format(name),
        material="vacuum"
    )

    # Тонкий контактный кончик пина Ø 0.35 мм (DETAIL A), заглублённый в медь на pin_pen (DL-30)
    pin_tip = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu - pin_pen"],
        radius="r_pin_tip",
        height="0.60mm + pin_pen",
        name="PinTip_{}".format(name),
        material="beryllium copper"
    )
    # Основной центральный проводник 2.92 мм Ø 1.27 мм
    pin_main = hfss.modeler.create_cylinder(
        orientation="Z",
        origin=[x_expr, y_expr, "h + t_cu + 0.55mm"],
        radius="r_pin_coax",
        height="fm_total_h - t_cu - 0.55mm",
        name="PinMain_{}".format(name),
        material="beryllium copper"
    )
    hfss.modeler.unite([pin_tip.name, pin_main.name])

    # Строгий порядок булевых вычитаний в коаксиале (DL-45):
    # 1. Вычитаем сплошной диэлектрик из металлического корпуса
    hfss.modeler.subtract(flange_cyl.name, coax_diel.name, keep_originals=True)
    # 2. Вычитаем центральный пин из диэлектрика
    hfss.modeler.subtract(coax_diel.name, pin_tip.name, keep_originals=True)

    # ------------------------------------------------------------
    # 6.5. Крепёжные отверстия 2-Ø 1.60 мм (шаг 7.16 мм) и земляные via Ø 0.25 мм
    # ------------------------------------------------------------
    for side, sign in [("L", -1.0), ("R", 1.0)]:
        hole_x = "({}) + ({})*fm_hole_pitch/2".format(x_expr, sign)
        hole = hfss.modeler.create_cylinder(
            orientation="Z",
            origin=[hole_x, y_expr, "-t_cu - 0.1mm"],
            radius="fm_hole_r",
            height="h + 2*t_cu + 0.2mm",
            name="MountHole_{}_{}".format(name, side),
            material="vacuum"
        )
        hfss.modeler.subtract([sub_name, gnd_bot_name, top_gnd.name], hole.name, keep_originals=False)

    # Переходные земляные столбики (via Ø 0.25 мм) вокруг согласующего канала
    via_offsets = [
        (-1.45,  0.55 * dir_sign),
        ( 1.45,  0.55 * dir_sign),
        (-1.05, -0.55 * dir_sign),
        ( 1.05, -0.55 * dir_sign),
        ( 0.00, -0.95 * dir_sign),
    ]
    via_list = []
    for idx, (dx_v, dy_v) in enumerate(via_offsets):
        vx = "({}) + ({}mm)".format(x_expr, dx_v)
        vy = "({}) + ({}mm)".format(y_expr, dy_v)
        v_cyl = hfss.modeler.create_cylinder(
            orientation="Z",
            origin=[vx, vy, "-t_cu"],
            radius="via_r",
            height="h + 2*t_cu",
            name="Via_{}_{}".format(name, idx),
            material="copper"
        )
        via_list.append(v_cyl.name)
    hfss.modeler.unite([gnd_bot_name, top_gnd.name] + via_list)

    # ------------------------------------------------------------
    # 6.6. Волновой порт на верхнем торце коаксиала 2.92 мм (renormalize=False, DL-46)
    # ------------------------------------------------------------
    port_sheet = hfss.modeler.create_circle(
        orientation="XY",
        origin=[x_expr, y_expr, z_top_port],
        radius="r_outer_coax",
        name="PortSheet_{}".format(name),
        is_covered=True
    )

    port_name = "P_" + name
    props = [
        "NAME:" + port_name,
        "Objects:=", [port_sheet.name],
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
                "Start:=", ["({}) + r_pin_coax".format(x_expr), y_expr, z_top_port],
                "End:=",   ["({}) + r_outer_coax".format(x_expr), y_expr, z_top_port],
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
        hfss.modeler.oeditor.AssignWavePort(props)

    print("[FMCN1476 {0:8s}] x={1}, y={2}, dir={3:+d}".format(
        name, x_expr, y_expr, dir_sign))


# Установка 8 разъёмов FMCN1476 по чертежу на опорные плоскости структур
build_fmcn1476_connector("THRU_1", "x_thru", "-L_thru/2", -1)
build_fmcn1476_connector("THRU_2", "x_thru", "L_thru/2",  +1)

build_fmcn1476_connector("LINE_1", "x_line", "-L_line/2", -1)
build_fmcn1476_connector("LINE_2", "x_line", "L_line/2",  +1)

build_fmcn1476_connector("OPEN_A", "x_open", "-y_top_res", -1)
build_fmcn1476_connector("OPEN_B", "x_open", "y_top_res",  +1)

build_fmcn1476_connector("RES_1",  "x_res",  "-y_top_res", -1)
build_fmcn1476_connector("RES_2",  "x_res",  "y_top_res",  +1)


# ================================================================
# 7. Open Region (с учётом высоты разъёмов FMCN1476 по +Z)
# ================================================================
hfss.modeler.create_region(
    pad_value=["15mm", "15mm", "15mm", "15mm", "15mm", "0mm"],
    is_percentage=False,
    name="Region"
)
hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")


# ================================================================
# 8. Setup + Sweep
# ================================================================
setup = hfss.create_setup("Setup_TRL_FMCN1476")
setup.props["Frequency"] = "{}GHz".format(f0_ghz)
setup.props["MaximumPasses"] = 18
setup.props["MaxDeltaS"] = 0.02

sweep = setup.add_sweep("Sweep_1_20GHz")
sweep.props["RangeType"] = "LinearCount"
sweep.props["RangeStart"] = "1GHz"
sweep.props["RangeEnd"] = "20GHz"
sweep.props["RangeCount"] = 191

hfss.save_project()
print("\nПроект сохранён: {}.aedt (разъёмы FMCN1476 по чертежу Fairview Microwave).".format(PROJECT_NAME))


# === hfss_trl_fmcn1476.py ===
