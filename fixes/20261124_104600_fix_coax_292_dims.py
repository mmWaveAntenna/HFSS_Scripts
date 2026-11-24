import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "TRL_script" / "hfss_trl_fmcn1476.py"

OLD_COAX = '''    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="1.46mm", height="6.95mm", name=diel_name, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=pin_air, material="copper")'''

NEW_COAX = '''    diel_name, pin_air, pin_pcb = f"Coax_Diel_{port_name}", f"Pin_Air_{port_name}", f"Pin_PCB_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.635mm", height="6.95mm", name=diel_name, material="vacuum")
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, "h + t_cu + 0.55mm"], radius="0.275mm", height="6.95mm", name=pin_air, material="copper")'''

OLD_PORT = '''    pec_cap, port_sheet = f"PEC_Cap_{port_name}", f"PortSheet_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, z_port], radius="2.26mm", height="0.2mm", name=pec_cap, material="pec")
    hfss.modeler.create_circle(orientation="XY", origin=[x_expr, y_expr, z_port], radius="1.46mm", name=port_sheet, is_covered=True)'''

NEW_PORT = '''    pec_cap, port_sheet = f"PEC_Cap_{port_name}", f"PortSheet_{port_name}"
    hfss.modeler.create_cylinder(orientation="Z", origin=[x_expr, y_expr, z_port], radius="2.26mm", height="0.2mm", name=pec_cap, material="pec")
    hfss.modeler.create_circle(orientation="XY", origin=[x_expr, y_expr, z_port], radius="0.635mm", name=port_sheet, is_covered=True)'''

OLD_INTLINE = '''"Start:=", [f"({xe}) + 0.635mm", ye, zp], "End:=", [f"({xe}) + 1.46mm", ye, zp]'''
NEW_INTLINE = '''"Start:=", [f"({xe}) + 0.275mm", ye, zp], "End:=", [f"({xe}) + 0.635mm", ye, zp]'''

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = (
    text.replace(OLD_COAX, NEW_COAX)
        .replace(OLD_PORT, NEW_PORT)
        .replace(OLD_INTLINE, NEW_INTLINE)
)
ast.parse(updated)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261124_104600_fix_coax_292_dims.py ===
