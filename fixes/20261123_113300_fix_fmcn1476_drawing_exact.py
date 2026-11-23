# -*- coding: utf-8 -*-
"""Патч-скрипт обновления упрощённой модели FMCN1476 по чертежу (h=0.115 мм, W=0.2 мм, 6 via, окно 1.50x0.55 мм)."""

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TARGET_FILE = PROJECT_ROOT / "TRL_script" / "hfss_trl_fmcn1476.py"

FIXED_CODE = '''# -*- coding: utf-8 -*-
"""Упрощённый генератор TRL + кольцевой резонатор с вертикальными разъёмами FMCN1476 (2.92 мм).

Параметры стека и футпринта согласованы с чертежом Fairview Microwave FMCN1476:
- Подложка FR4: h = 0.115 мм, микрополосок 50 Ом: W = 0.2 мм.
- Верхний земляной полигон (Recommended Top PCB Pattern): 6.24 мм (поперёк линии) x 10.50 мм (вдоль оси винтов).
- Входной вырез: 2.40 мм (глубина) x 0.95 мм (ширина) + канал 1.00 мм шириной W + 2*0.43 мм.
- Контактный пад микрополоска: R = 0.28 мм; вырез в верхней земле вокруг пада: R = 0.50 мм.
- 6 переходных земляных via (Ø 0.25 мм) по контуру канала и вокруг выреза пина.
- Боковое окно в нижней металлической втулке (Ø 3.50 мм): ширина 1.50 мм x высота 0.55 мм (по DETAIL A).
"""

try:
    from pyaedt import Hfss
except ImportError:
    from ansys.aedt.core import Hfss


def draw_fmcn1476(hfss, x_expr, y_expr, dir_y, line_obj_name, port_name):
    """Отрисовка посадочного места и упрощённого разъёма FMCN1476 (2.92 мм).
    dir_y = +1: порт на -Y краю, микрополосок уходит в +Y;
    dir_y = -1: порт на +Y краю, микрополосок уходит в -Y.
    """
    z_port = "h + t_cu + 7.5mm"

    # 1. Верхний копланарный полигон (6.24 мм по X x 10.50 мм по Y)
    # Центр пина сдвинут на 3.40 мм (2.40 мм вырез + 1.00 мм канал) от края полигона со стороны линии
    pad_name = f"TopPad_{port_name}"
    if dir_y > 0:
        pad_y0 = f"({y_expr}) - 7.10mm"
        notch_y0 = f"({y_expr}) + 1.00mm"
        chan_y0 = f"({y_expr})"
    else:
        pad_y0 = f"({y_expr}) - 3.40mm"
        notch_y0 = f"({y_expr}) - 3.40mm"
        chan_y0 = f"({y_expr}) - 1.00mm"

    hfss.modeler.create_box(
        origin=[f"({x_expr}) - 3.12mm", pad_y0, "h"],
        sizes=["6.24mm", "10.50mm", "t_cu"],
        name=pad_name, material="copper"
    )

    # 2. Вырезы в верхнем земляном полигоне (по чертежу Top PCB Pattern)
    # Входной вырез: 0.95 мм (по X) x 2.40 мм (по Y)
    notch_name = f"Notch_{port_name}"
    hfss.modeler.create_box(
        origin=[f"({x_expr}) - 0.475mm", notch_y0, "h - 0.01mm"],
        sizes=["0.95mm", "2.40mm", "t_cu + 0.02mm"],
        name=notch_name, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, notch_name, keep_originals=False)

    # Узкий канал вдоль полоска длиной 1.00 мм с зазором 0.43 мм на сторону (ширина W + 0.86 мм)
    chan_name = f"Chan_{port_name}"
    hfss.modeler.create_box(
        origin=[f"({x_expr}) - W/2 - 0.43mm", chan_y0, "h - 0.01mm"],
        sizes=["W + 0.86mm", "1.00mm", "t_cu + 0.02mm"],
        name=chan_name, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, chan_name, keep_originals=False)

    # Круглый вырез в верхней земле вокруг пада пина: R = 0.50 мм
    pin_clear = f"PinClear_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h - 0.01mm"],
        radius="0.50mm", height="t_cu + 0.02mm", name=pin_clear, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, pin_clear, keep_originals=False)

    # Контактный пад на конце микрополоска (R = 0.28 мм), объединённый с линией
    line_pad = f"LinePad_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h"],
        radius="0.28mm", height="t_cu", name=line_pad, material="copper"
    )
    hfss.modeler.unite([line_obj_name, line_pad])

    # 3. Крепёжные отверстия 2-Ø 1.60 мм с шагом 7.16 мм вдоль оси Y (±3.58 мм от центра пина)
    for side, sign in [("A", -1), ("B", 1)]:
        hole_y = f"({y_expr}) + ({sign}*3.58mm)"
        hole_name = f"MntHole_{port_name}_{side}"
        hfss.modeler.create_cylinder(
            orientation="Z", origin=[x_expr, hole_y, "-t_cu - 0.1mm"],
            radius="0.80mm", height="h + 2*t_cu + 0.2mm", name=hole_name, material="vacuum"
        )
        hfss.modeler.subtract(["Substrate", "GND", pad_name], hole_name, keep_originals=False)

    # 4. 6 переходных земляных via (Ø 0.25 мм -> R = 0.125 мм) вокруг канала и выреза пина
    via_coords = [
        (-0.80,  0.85 * dir_y),
        ( 0.80,  0.85 * dir_y),
        (-0.80,  0.15 * dir_y),
        ( 0.80,  0.15 * dir_y),
        (-0.55, -0.60 * dir_y),
        ( 0.55, -0.60 * dir_y),
    ]
    via_list = []
    for idx, (dx, dy) in enumerate(via_coords):
        via_name = f"Via_{port_name}_{idx}"
        hfss.modeler.create_cylinder(
            orientation="Z", origin=[f"({x_expr}) + ({dx}mm)", f"({y_expr}) + ({dy}mm)", "-t_cu"],
            radius="0.125mm", height="h + 2*t_cu", name=via_name, material="copper"
        )
        via_list.append(via_name)
    hfss.modeler.unite(["GND", pad_name] + via_list)

    # 5. Нижняя металлическая втулка (Ø 3.50 мм -> R = 1.75 мм) с боковым окном 1.50 x 0.55 мм (DETAIL A)
    boss_name = f"Coax_Boss_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu"],
        radius="1.75mm", height="0.60mm", name=boss_name, material="pec"
    )
    win_y0 = f"({y_expr})" if dir_y > 0 else f"({y_expr}) - 1.90mm"
    win_cut = f"BossWindow_{port_name}"
    hfss.modeler.create_box(
        origin=[f"({x_expr}) - 0.75mm", win_y0, "h + t_cu - 0.01mm"],
        sizes=["1.50mm", "1.90mm", "0.56mm"],
        name=win_cut, material="vacuum"
    )
    hfss.modeler.subtract(boss_name, win_cut, keep_originals=False)

    # 6. Коаксиал 2.92 мм (внутренний Ø 2.92 мм -> R = 1.46 мм) и ступенчатый пин (DETAIL A)
    barrel_name = f"Coax_Barrel_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"],
        radius="2.26mm", height="6.95mm", name=barrel_name, material="pec"
    )
    hfss.modeler.unite([barrel_name, boss_name])

    diel_name = f"Coax_Diel_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"],
        radius="1.46mm", height="6.95mm", name=diel_name, material="vacuum"
    )
    pin_air = f"Pin_Air_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"],
        radius="0.635mm", height="6.95mm", name=pin_air, material="copper"
    )
    pin_pcb = f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu - 0.015mm"],
        radius="0.175mm", height="0.58mm", name=pin_pcb, material="copper"
    )
    hfss.modeler.unite([pin_air, pin_pcb])

    # Булевы вычитания строго по DL-45
    hfss.modeler.subtract(barrel_name, diel_name, keep_originals=True)
    hfss.modeler.subtract(diel_name, pin_air, keep_originals=True)

    # 7. Нижний круглый антипад в GND (Ø 0.96 мм -> R = 0.48 мм)
    antipad_name = f"AntiPad_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "-t_cu - 0.05mm"],
        radius="0.48mm", height="t_cu + 0.10mm", name=antipad_name, material="vacuum"
    )
    hfss.modeler.subtract("GND", antipad_name, keep_originals=False)

    # 8. Волновой порт на торце коаксиала с PEC-крышкой сверху (DL-46, DL-57)
    pec_cap = f"PEC_Cap_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, z_port],
        radius="2.26mm", height="0.2mm", name=pec_cap, material="pec"
    )
    port_sheet = f"PortSheet_{port_name}"
    hfss.modeler.create_circle(
        orientation="XY", origin=[x_expr, y_expr, z_port],
        radius="1.46mm", name=port_sheet, is_covered=True
    )

    props = [
        "NAME:" + port_name,
        "Objects:=", [port_sheet],
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
                "Start:=", [f"({x_expr}) + 0.635mm", y_expr, z_port],
                "End:=", [f"({x_expr}) + 1.46mm", y_expr, z_port],
            ],
            "AlignmentGroup:=", 0,
            "CharImp:=", "Zpi"
        ],
        "ShowReporterFilter:=", False,
        "ReporterFilter:=", [True],
        "UseAnalyticAlignment:=", False
    ]
    hfss.oboundary.AssignWavePort(props)


def main():
    hfss = Hfss(project="TRL_Calibration_FR4_FMCN1476", design="TRL_Kit",
                solution_type="DrivenModal", new_desktop=True)
    hfss.modeler.model_units = "mm"

    # Параметры стека FR4 0.115 мм (W = 0.2 мм для 50 Ом) и TRL
    hfss["h"] = "0.115mm"
    hfss["W"] = "0.2mm"
    hfss["t_cu"] = "0.035mm"
    hfss["er"] = "4.4"
    hfss["f0_GHz"] = "10.0"
    hfss["L_thru"] = "10mm"
    hfss["L_ref"] = "L_thru/2"
    hfss["L_feed"] = "L_thru/2"
    hfss["eps_eff"] = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"
    hfss["dL"] = "75mm/(f0_GHz*sqrt(eps_eff))"
    hfss["L_line"] = "L_thru + dL"

    # Параметры кольцевого резонатора (n=1)
    hfss["W_ring"] = "0.2mm"
    hfss["W_tab"] = "0.6mm"
    hfss["R_tab"] = "0.2mm"
    hfss["gap_couple"] = "0.15mm"
    hfss["eps_ring"] = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"
    hfss["r_mean"] = "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"
    hfss["r_out"] = "r_mean + W_ring/2"
    hfss["r_in"] = "r_mean - W_ring/2"
    hfss["r_tab_in"] = "r_out + gap_couple"
    hfss["r_tab_out"] = "r_tab_in + R_tab"
    hfss["y_top_res"] = "r_tab_out + L_feed"

    hfss["pitch_trl"] = "20mm"
    hfss["pitch_res"] = "20mm"
    hfss["x_thru"] = "0mm"
    hfss["x_line"] = "pitch_trl"
    hfss["x_open"] = "2*pitch_trl"

    hfss["x_res"] = "2*pitch_trl + pitch_res"

    # Подложка и нижняя земля
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 10mm", "-t_cu"],
        sizes=["x_res + 20mm", "2*y_top_res + 20mm", "t_cu"],
        name="GND", material="copper"
    )
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 10mm", "0mm"],
        sizes=["x_res + 20mm", "2*y_top_res + 20mm", "h"],
        name="Substrate", material="FR4_epoxy"
    )

    # Микрополосковые линии TRL (OPEN выровнен по Y с RES по DL-58)
    hfss.modeler.create_box(origin=["x_thru - W/2", "-L_thru/2", "h"], sizes=["W", "L_thru", "t_cu"], name="THRU_Line", material="copper")
    hfss.modeler.create_box(origin=["x_line - W/2", "-L_line/2", "h"], sizes=["W", "L_line", "t_cu"], name="LINE_Line", material="copper")
    hfss.modeler.create_box(origin=["x_open - W/2", "-y_top_res", "h"], sizes=["W", "L_ref", "t_cu"], name="OPEN_A", material="copper")
    hfss.modeler.create_box(origin=["x_open - W/2", "y_top_res - L_ref", "h"], sizes=["W", "L_ref", "t_cu"], name="OPEN_B", material="copper")

    # Кольцевой резонатор (n=1) с T-лапками и фидерами
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_out", height="t_cu", name="RING_OUT", material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_in", height="t_cu", name="RING_IN", material="vacuum")
    hfss.modeler.subtract("RING_OUT", "RING_IN", keep_originals=False)

    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_out", height="t_cu", name="TAB_RING", material="copper")
    hfss.modeler.create_cylinder(orientation="Z", origin=["x_res", "0mm", "h"], radius="r_tab_in", height="t_cu", name="TAB_IN", material="vacuum")
    hfss.modeler.subtract("TAB_RING", "TAB_IN", keep_originals=False)
    hfss.modeler.create_box(origin=["x_res - W_tab/2", "-r_tab_out - 1mm", "h"], sizes=["W_tab", "2*r_tab_out + 2mm", "t_cu"], name="TAB_BOX", material="copper")
    hfss.modeler.intersect(["TAB_BOX", "TAB_RING"], keep_originals=False)

    hfss.modeler.create_box(origin=["x_res - W/2", "r_tab_out - 0.3mm", "h"], sizes=["W", "L_feed + 0.3mm", "t_cu"], name="RES_Feed_2", material="copper")
    hfss.modeler.create_box(origin=["x_res - W/2", "-r_tab_out - L_feed", "h"], sizes=["W", "L_feed + 0.3mm", "t_cu"], name="RES_Feed_1", material="copper")
    hfss.modeler.unite(["TAB_BOX", "RES_Feed_1", "RES_Feed_2"])

    # Установка 8 разъёмов FMCN1476 (с привязкой к объектам линий для объединения падов)
    ports_data = [
        ("x_thru", "-L_thru/2", 1, "THRU_Line", "P_THRU_1"),
        ("x_thru", "L_thru/2", -1, "THRU_Line", "P_THRU_2"),
        ("x_line", "-L_line/2", 1, "LINE_Line", "P_LINE_1"),
        ("x_line", "L_line/2", -1, "LINE_Line", "P_LINE_2"),
        ("x_open", "-y_top_res", 1, "OPEN_A", "P_OPEN_A"),
        ("x_open", "y_top_res", -1, "OPEN_B", "P_OPEN_B"),
        ("x_res", "-y_top_res", 1, "TAB_BOX", "P_RES_1"),
        ("x_res", "y_top_res", -1, "TAB_BOX", "P_RES_2"),
    ]
    for x_e, y_e, d_y, line_obj, p_name in ports_data:
        draw_fmcn1476(hfss, x_e, y_e, d_y, line_obj, p_name)

    # Open Region + Radiation Boundary
    hfss.modeler.create_region(pad_value=["15mm", "15mm", "15mm", "15mm", "15mm", "0mm"], is_percentage=False, name="Region")
    hfss.assign_radiation_boundary_to_objects("Region", name="Rad_Region")

    # Setup + Sweep
    setup = hfss.create_setup("Setup_TRL")
    setup.props["Frequency"] = "10GHz"
    setup.props["MaximumPasses"] = 16
    setup.props["MaxDeltaS"] = 0.02
    sweep = setup.add_sweep("Sweep_1_20GHz")
    sweep.props["RangeType"] = "LinearCount"
    sweep.props["RangeStart"] = "1GHz"
    sweep.props["RangeEnd"] = "20GHz"
    sweep.props["RangeCount"] = 191

    hfss.save_project()
    print("Модель успешно сгенерирована.")


if __name__ == "__main__":
    main()
'''


def apply_patch():
    old_lines = TARGET_FILE.read_text(encoding="utf-8").splitlines() if TARGET_FILE.exists() else []
    new_lines = FIXED_CODE.strip().splitlines()

    ast.parse(FIXED_CODE)

    if old_lines == new_lines:
        print(f"[{ts} MSK] {TARGET_FILE.name}: изменений не требуется (идемпотентность).")
        return

    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    TARGET_FILE.write_text(FIXED_CODE.strip() + "\n", encoding="utf-8")
    diff = len(new_lines) - len(old_lines)
    sign = "+" if diff >= 0 else ""
    print(f"[{ts} MSK] === {TARGET_FILE} ===")
    print(f"  Было строк: {len(old_lines)}")
    print(f"  Стало строк: {len(new_lines)} ({sign}{diff})")
    print("  ✓ применено: h=0.115 мм, W=0.2 мм, пад R=0.28 мм, вырез PinClear R=0.50 мм, 6 via, окно втулки 1.50x0.55 мм.")


if __name__ == "__main__":
    apply_patch()
