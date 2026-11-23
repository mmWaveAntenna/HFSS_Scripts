# -*- coding: utf-8 -*-
"""Патч-скрипт исправления упрощённой модели разъёма FMCN1476 (PyAEDT 1.8.0 / AEDT 2025.1)."""

import ast
from datetime import datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TARGET_FILE = PROJECT_ROOT / "TRL_script" / "hfss_trl_fmcn1476.py"

FIXED_CODE = '''# -*- coding: utf-8 -*-
"""Упрощённый генератор TRL + кольцевой резонатор с вертикальными разъёмами FMCN1476 (2.92 мм)."""

try:
    from pyaedt import Hfss
except ImportError:
    from ansys.aedt.core import Hfss


def draw_fmcn1476(hfss, x_expr, y_expr, dir_y, port_name):
    """Отрисовка посадочного места (Top/Bottom PCB Pattern) и коаксиала 2.92 мм FMCN1476.
    dir_y = +1: линия идёт в +Y; dir_y = -1: линия идёт в -Y.
    """
    z_port = "h + t_cu + 7.5mm"

    # 1. Верхний копланарный полигон (10.50 x 6.24 мм) со смещением пина 1.95 мм от края со стороны линии
    pad_name = f"TopPad_{port_name}"
    if dir_y > 0:
        pad_y0 = f"({y_expr}) - 4.29mm"
        notch_y0 = f"({y_expr}) + 1.00mm"
        chan_y0 = f"({y_expr})"
    else:
        pad_y0 = f"({y_expr}) - 1.95mm"
        notch_y0 = f"({y_expr}) - 1.95mm"
        chan_y0 = f"({y_expr}) - 1.95mm"

    hfss.modeler.create_box(
        origin=[f"({x_expr}) - 5.25mm", pad_y0, "h"],
        sizes=["10.50mm", "6.24mm", "t_cu"],
        name=pad_name, material="copper"
    )

    # 2. Входной вырез (2.40 x 0.95 мм), канал вдоль полоска (W + 2*0.43 мм) и вырез вокруг пина (R 0.28 мм)
    notch_name = f"Notch_{port_name}"
    hfss.modeler.create_box(
        origin=[f"({x_expr}) - 1.20mm", notch_y0, "h - 0.01mm"],
        sizes=["2.40mm", "0.95mm", "t_cu + 0.02mm"],
        name=notch_name, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, notch_name, keep_originals=False)

    chan_name = f"Chan_{port_name}"
    hfss.modeler.create_box(
        origin=[f"({x_expr}) - W/2 - 0.43mm", chan_y0, "h - 0.01mm"],
        sizes=["W + 0.86mm", "1.95mm", "t_cu + 0.02mm"],
        name=chan_name, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, chan_name, keep_originals=False)

    pin_clear = f"PinClear_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h - 0.01mm"],
        radius="0.28mm", height="t_cu + 0.02mm", name=pin_clear, material="vacuum"
    )
    hfss.modeler.subtract(pad_name, pin_clear, keep_originals=False)

    # 3. Крепёжные отверстия (2-Ø 1.60 мм, шаг 7.16 мм по оси X)
    for side, sign in [("L", -1), ("R", 1)]:
        hole_x = f"({x_expr}) + ({sign}*3.58mm)"
        hole_name = f"MntHole_{port_name}_{side}"
        hfss.modeler.create_cylinder(
            orientation="Z", origin=[hole_x, y_expr, "-t_cu - 0.1mm"],
            radius="0.80mm", height="h + 2*t_cu + 0.2mm", name=hole_name, material="vacuum"
        )
        hfss.modeler.subtract(["Substrate", "GND", pad_name], hole_name, keep_originals=False)

    # 4. Переходные земляные via (Ø 0.25 мм)
    via_list = []
    for idx, (dx, dy) in enumerate([(-1.45, 0.55 * dir_y), (1.45, 0.55 * dir_y), (0.0, -0.95 * dir_y)]):
        via_name = f"Via_{port_name}_{idx}"
        hfss.modeler.create_cylinder(
            orientation="Z", origin=[f"({x_expr}) + ({dx}mm)", f"({y_expr}) + ({dy}mm)", "-t_cu"],
            radius="0.125mm", height="h + 2*t_cu", name=via_name, material="copper"
        )
        via_list.append(via_name)
    hfss.modeler.unite(["GND", pad_name] + via_list)

    # 5. Коаксиал 2.92 мм (внешний проводник Ø 2.92 мм -> R=1.46 мм, стенка 0.8 мм)
    barrel_name = f"Coax_Barrel_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu"],
        radius="2.26mm", height="7.5mm", name=barrel_name, material="pec"
    )
    diel_name = f"Coax_Diel_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "h + t_cu"],
        radius="1.46mm", height="7.5mm", name=diel_name, material="vacuum"
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

    # 6. Нижний антипад в GND (Ø 0.96 мм -> R=0.48 мм)
    antipad_name = f"AntiPad_{port_name}"
    hfss.modeler.create_cylinder(
        orientation="Z", origin=[x_expr, y_expr, "-t_cu - 0.05mm"],
        radius="0.48mm", height="t_cu + 0.10mm", name=antipad_name, material="vacuum"
    )
    hfss.modeler.subtract("GND", antipad_name, keep_originals=False)

    # 7. Волновой порт на торце коаксиала с PEC-крышкой сверху (DL-46, DL-57)
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

    # Параметры дизайна HFSS (DL-17, DL-41, DL-42)
    hfss["h"] = "0.93mm"
    hfss["W"] = "1.7mm"
    hfss["t_cu"] = "0.035mm"
    hfss["er"] = "4.4"
    hfss["f0_GHz"] = "10.0"
    hfss["L_thru"] = "10mm"
    hfss["L_ref"] = "L_thru/2"
    hfss["L_feed"] = "L_thru/2"
    hfss["eps_eff"] = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W)"
    hfss["dL"] = "75mm/(f0_GHz*sqrt(eps_eff))"
    hfss["L_line"] = "L_thru + dL"

    hfss["W_ring"] = "0.4mm"
    hfss["W_tab"] = "1.7mm"
    hfss["R_tab"] = "0.4mm"
    hfss["gap_couple"] = "0.2mm"
    hfss["eps_ring"] = "(er+1)/2 + (er-1)/2/sqrt(1+12*h/W_ring)"
    hfss["r_mean"] = "300mm/(2*pi*f0_GHz*sqrt(eps_ring))"
    hfss["r_out"] = "r_mean + W_ring/2"
    hfss["r_in"] = "r_mean - W_ring/2"
    hfss["r_tab_in"] = "r_out + gap_couple"
    hfss["r_tab_out"] = "r_tab_in + R_tab"
    hfss["y_top_res"] = "r_tab_out + L_feed"

    hfss["pitch_trl"] = "25mm"
    hfss["pitch_res"] = "25mm"
    hfss["x_thru"] = "0mm"
    hfss["x_line"] = "pitch_trl"
    hfss["x_open"] = "2*pitch_trl"
    hfss["x_res"] = "2*pitch_trl + pitch_res"

    # Подложка и нижняя земля
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 8mm", "-t_cu"],
        sizes=["x_res + 20mm", "2*y_top_res + 16mm", "t_cu"],
        name="GND", material="copper"
    )
    hfss.modeler.create_box(
        origin=["-10mm", "-y_top_res - 8mm", "0mm"],
        sizes=["x_res + 20mm", "2*y_top_res + 16mm", "h"],
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

    hfss.modeler.create_box(origin=["x_res - W/2", "r_tab_out - 0.5mm", "h"], sizes=["W", "L_feed + 0.5mm", "t_cu"], name="RES_Feed_2", material="copper")

    hfss.modeler.create_box(origin=["x_res - W/2", "-r_tab_out - L_feed", "h"], sizes=["W", "L_feed + 0.5mm", "t_cu"], name="RES_Feed_1", material="copper")
    hfss.modeler.unite(["TAB_BOX", "RES_Feed_1", "RES_Feed_2"])
    # Установка 8 разъёмов FMCN1476
    ports_data = [
        ("x_thru", "-L_thru/2", 1, "P_THRU_1"),
        ("x_thru", "L_thru/2", -1, "P_THRU_2"),
        ("x_line", "-L_line/2", 1, "P_LINE_1"),
        ("x_line", "L_line/2", -1, "P_LINE_2"),
        ("x_open", "-y_top_res", 1, "P_OPEN_A"),
        ("x_open", "y_top_res", -1, "P_OPEN_B"),
        ("x_res", "-y_top_res", 1, "P_RES_1"),
        ("x_res", "y_top_res", -1, "P_RES_2"),
    ]
    for x_e, y_e, d_y, p_name in ports_data:
        draw_fmcn1476(hfss, x_e, y_e, d_y, p_name)

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

    TARGET_FILE.write_text(FIXED_CODE.strip() + "\n", encoding="utf-8")
    diff = len(new_lines) - len(old_lines)
    sign = "+" if diff >= 0 else ""
    print(f"[{ts} MSK] === {TARGET_FILE} ===")
    print(f"  Было строк: {len(old_lines)}")
    print(f"  Стало строк: {len(new_lines)} ({sign}{diff})")
    print("  ✓ применено: исправлен футпринт FMCN1476, булевы операции коаксиала, AssignWavePort, добавлен резонатор, Region и Setup/Sweep.")


if __name__ == "__main__":
    apply_patch()


