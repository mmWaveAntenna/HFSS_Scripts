import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

RES2_PHASE1 = '''    # Второй кольцевой резонатор (питание под углом 90°: -Y и +X)
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

ANCHOR = "    l_thru_v, l_line_v, l_ref_v ="
text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
assert ANCHOR in text, "Якорь l_thru_v не найден!"
if 'name="RING2_OUT"' not in text:
    updated = text.replace(ANCHOR, RES2_PHASE1 + ANCHOR, 1)
    ast.parse(updated)
    TARGET.write_text(updated, encoding="utf-8")
    new_count = len(updated.splitlines())
    print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
else:
    print(f"[{ts} MSK] {TARGET.name}: RING2_OUT уже присутствует в Фазе 1.")
# === fixes/20261124_131500_fix_res2_phase1_creation.py ===
