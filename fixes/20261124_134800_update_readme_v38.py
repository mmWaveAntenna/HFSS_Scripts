# --- Часть 1/2 ---
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent  / "README.md"

VER_OLD = "**Версия 3.7**"
VER_NEW = "**Версия 3.8**"

PROJ_OLD = "- **RES** — кольцевой резонатор ($n=1$) с T-лапками и фидерами длиной $L_\\text{thru}/2$ для слабой связи ($|S_{21}| \\approx -25\\ldots-35$ дБ)."
PROJ_NEW = (
    PROJ_OLD + "\n"
    "- **RES2** *(в `hfss_trl_fmcn1476.py` v2.5)* — второй кольцевой резонатор ($n=1$) с ортогональными фидерами под углом **90°** (`-Y` и `+X`) для выделения анизотропии диэлектрика FR4.\n\n"
    "Для верификации с реальными вертикальными разъёмами **Fairview Microwave FMCN1476 (2.92 мм)** используется отдельный производственный генератор `hfss_trl_fmcn1476.py` (v2.5, 10 портов, стек FR4 $h = 0.115$ мм, $W = 0.2$ мм, сплошной верхний экран `GND_TOP` с отступом `gap_gnd = 0.5 мм` и прошивкой via по технологическим нормам **Резонит** $\\ge 200$ мкм от края отверстия до края меди)."
)

STEP_5_OLD = "5. **Контроль:** на `THRU` должно быть $\\angle S_{21} = 0.0^\\circ \\pm 0.5^\\circ$, $|S_{11}| < -35$ дБ; на `OPEN` — $\\angle S_{11} \\approx 0^\\circ$. После проверки подключить **`P_RES_1` / `P_RES_2`** для прямого измерения $f_0$ и $Q_L$ резонатора."
STEP_5_NEW = "5. **Контроль:** на `THRU` должно быть $\\angle S_{21} = 0.0^\\circ \\pm 0.5^\\circ$, $|S_{11}| < -35$ дБ; на `OPEN` — $\\angle S_{11} \\approx 0^\\circ$. После проверки подключить **`P_RES_1` / `P_RES_2`** (резонатор 180°) или **`P_RES2_1` / `P_RES2_2`** (ортогональный резонатор 90°) для прямого измерения $f_0$, расщепления мод и $Q_L$."
# --- Часть 2/2 ---
ARCH_OLD = """```
TRL_script/
├── hfss_trl_kit.py             # единый генератор проекта с идеальными портами (v3.6.1)
├── TRL_Res_Prod.py             # ветка с физическими коаксиальными разъёмами (FMCN1476 / G14SFB001)
├── Conn_FMCN1476               # справочные данные разъёма FMCN1476
├── DEV_LOG.md                  # журнал ошибок и уроков (DL-01 … DL-58)
├── Memory_bank.md              # сводка состояния проекта
├── README.md                   # данный файл
├── Rules.md                    # правила работы над проектом (v2.0)
└── role.md / RF-Antenna-HFSS-Agent.md
```"""

ARCH_NEW = """```
TRL_script/
├── hfss_trl_kit.py             # базовый генератор TRL + резонатор с идеальными sheet-портами (v3.6.1)
├── hfss_trl_fmcn1476.py        # производственный генератор TRL + 2 резонатора (180° и 90°), FMCN1476, GND_TOP (v2.5)
├── TRL_Res_Prod.py             # архивная ветка с торцевыми разъёмами 1.85 мм
├── DEV_LOG.md                  # append-only журнал ошибок и уроков (DL-01 … DL-69, v3.11)
├── Memory_bank.md              # сводка состояния проекта
├── README.md                   # данный файл (v3.8)
└── role.md / RF-Antenna-HFSS-Agent.md
fixes/                          # идемпотентные diff-патч-скрипты (МСК, блоки <= 100 строк)
Rules.md                        # правила разработки и формат diff-патчей (v2.2)
```"""

def apply_patch():
    if not TARGET.exists():
        raise FileNotFoundError(f"Файл не найден: {TARGET}")
    text = TARGET.read_text(encoding="utf-8")
    old_count = len(text.splitlines())
    if VER_NEW in text:
        print(f"[{ts} MSK] {TARGET.name}: изменений не требуется (идемпотентность).")
        return
    for anchor in (VER_OLD, PROJ_OLD, STEP_5_OLD, ARCH_OLD):
        assert anchor in text, f"Не найден якорь: {anchor[:60]}..."
    updated = (
        text.replace(VER_OLD, VER_NEW, 1)
            .replace(PROJ_OLD, PROJ_NEW, 1)
            .replace(STEP_5_OLD, STEP_5_NEW, 1)
            .replace(ARCH_OLD, ARCH_NEW, 1)
    )
    TARGET.write_text(updated, encoding="utf-8")
    new_count = len(updated.splitlines())
    print(f"[{ts} MSK] === {TARGET} ===")
    print(f"  Было строк: {old_count}")
    print(f"  Стало строк: {new_count} ({new_count - old_count:+d})")
    print("  ✓ применено: README.md обновлён до версии 3.8.")

if __name__ == "__main__":
    apply_patch()
# === fixes/20261124_134800_update_readme_v38.py ===
