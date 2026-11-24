# --- Часть 1/2 ---
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
ROOT = Path(__file__).resolve().parent.parent
README_FILE = ROOT  / "README.md"
MEM_FILE = ROOT  / "Memory_bank.md"

README_VER_OLD = "**Версия 3.6.1**"
README_VER_NEW = "**Версия 3.7**"

README_ANCHOR = """4. Экспортировать S-параметры: `Results → Solution Data → Export → Touchstone` или выполнить деэмбеддинг в `Tools → Calibration Wizard` (Type: TRL)."""

README_8722ES = README_ANCHOR + """

---

## Методика TRL-калибровки на VNA Agilent 8722ES (1 стандарт LINE)

Для платы на FR4 ($h = 0.115$ мм, $W = 0.2$ мм, $L_\\text{thru} = 10$ мм, $\\Delta L = 4.20$ мм, $L_\\text{ref} = L_\\text{feed} = 5$ мм, $\\varepsilon_\\text{eff} \\approx 3.19$) опорная плоскость (reference plane) задаётся в **центре `THRU`** (совпадает с плоскостью T-лапок резонатора `TAB`). Рабочее фазовое окно $20^\\circ \\le \\Delta\\varphi \\le 160^\\circ$ для одной меры `LINE` охватывает диапазон **2.22 – 17.78 ГГц**.

### 1. Настройка полосы и приёмника VNA
1. **`PRESET`** → **`START`** `2.5 GHz`, **`STOP`** `17.5 GHz`.
2. **`MENU` → `NUMBER OF POINTS`** → `401` (или `801`); **`AVG` → `IF BW`** → `1 kHz`; **`POWER`** → `-5 dBm`.

### 2. Создание User Cal Kit (`CAL → CAL KIT → SELECT CAL KIT → USER KIT → MODIFY CAL KIT`)
1. **`STD 1` (`THRU`, тип `DELAY / THRU`):** `OFFSET DELAY = 0 ps`, `OFFSET Z0 = 50 Ohm`, `OFFSET LOSS = 0`.
2. **`STD 2` (`OPEN`, тип `OPEN`):** `OFFSET DELAY = 0 ps` (торец `OPEN` длиной $L_\\text{thru}/2$ лежит в опорной плоскости), `OFFSET Z0 = 50 Ohm`, `MIN FREQ = 2.2 GHz`, `MAX FREQ = 18 GHz`.
3. **`STD 3` (`LINE`, тип `DELAY / THRU`):** задержка $\\tau_{\\Delta L} = \\Delta L\\sqrt{\\varepsilon_\\text{eff}}/c \\approx \\mathbf{25.0\\text{ ps}}$, `OFFSET Z0 = 50 Ohm`, `MIN FREQ = 2.25 GHz`, `MAX FREQ = 17.7 GHz`.
4. **`SPECIFY CLASS → MORE → TRL / LRM`:** назначить `THRU` → `STD 1`, `S11 REFLECT` / `S22 REFLECT` → `STD 2`, `LINE / MATCH` → `STD 3`. Сохранить через **`KIT DONE` → `SAVE USER KIT`**.

### 3. Измерение стандартов и верификация (`CAL → CALIBRATE MENU → TRL 2-PORT`)
1. **`THRU`:** подключить кабели Порта 1 и Порта 2 к `P_THRU_1` и `P_THRU_2`.
2. **`REFLECT`:** подключить Порт 1 к `P_OPEN_A`, Порт 2 к `P_OPEN_B` (`S11 REFLECT`, `S22 REFLECT`).
3. **`LINE`:** подключить кабели к `P_LINE_1` и `P_LINE_2` (`LINE / MATCH`).
4. **`ISOLATION → OMIT ISOLATION`**, затем **`DONE TRL 2-PORT`** (на экране загорится **`Cor`**).
5. **Контроль:** на `THRU` должно быть $\\angle S_{21} = 0.0^\\circ \\pm 0.5^\\circ$, $|S_{11}| < -35$ дБ; на `OPEN` — $\\angle S_{11} \\approx 0^\\circ$. После проверки подключить **`P_RES_1` / `P_RES_2`** для прямого измерения $f_0$ и $Q_L$ резонатора."""

# --- Часть 2/2 ---
MEM_VER_OLD = "- Версия: `hfss_trl_kit.py` v3.6.1 / `hfss_trl_fmcn1476.py` (упрощённая ветка v2.1) / `Rules.md` v2.1 / `DEV_LOG.md` v3.8"
MEM_VER_NEW = "- Версия: `hfss_trl_kit.py` v3.6.1 / `hfss_trl_fmcn1476.py` v2.3 (экран `GND_TOP`, 2-фазные булевы операции, via Резонит) / `Rules.md` v2.2 / `DEV_LOG.md` v3.10 / `README.md` v3.7"

MEM_LAST_OLD = "- Что: выверена геометрия упрощённой модели `TRL_script/hfss_trl_fmcn1476.py` по чертежу FMCN1476 (`h = 0.115 мм`, `W = 0.2 мм`, `TopPad` `10.50 × 6.24 мм`, крепёж по X, пад `R = 0.28 мм`, вырез `R = 0.50 мм`, 12 via, окно втулки `1.50 × 0.55 мм`, параметризованный `bot_cut_dia`); обновлены `Rules.md` (v2.1), `DEV_LOG.md` (v3.8, `DL-60`…`DL-63`) и `Memory_bank.md`."
MEM_LAST_NEW = "- Что: в `TRL_script/hfss_trl_fmcn1476.py` добавлен верхний земляной экран `GND_TOP` (`gap_gnd = 0.5 мм`), прошивка `via` по нормам Резонит (≥ 200 мкм от края отверстия до края меди, включая 4 торцевых via на `OPEN_A/B`), коаксиал 2.92 мм (`1.27 / 0.55 мм`) со ступенькой пина `0.35 → 0.55 мм` в окне втулки (`BossBore`), 2-фазные булевы операции и `hfss.autosave_disable()`; в `README.md` (v3.7) добавлена методика TRL-калибровки для Agilent 8722ES; обновлены `Rules.md` (v2.2), `DEV_LOG.md` (v3.10) и `Memory_bank.md`."

def patch_doc(path, pairs, label):
    if not path.exists():
        print(f"[{ts} MSK] Пропущен (не найден): {path}")
        return
    text = path.read_text(encoding="utf-8")
    old_n = len(text.splitlines())
    updated = text
    for old_s, new_s in pairs:
        if new_s not in updated:
            updated = updated.replace(old_s, new_s)
    if updated == text:
        print(f"[{ts} MSK] {path.name}: изменений не требуется ({label}).")
        return
    path.write_text(updated, encoding="utf-8")
    new_n = len(updated.splitlines())
    print(f"[{ts} MSK] === {path} ===\n  Было строк: {old_n}\n  Стало строк: {new_n} ({new_n - old_n:+d}) [{label}]")

if __name__ == "__main__":
    patch_doc(README_FILE, [(README_VER_OLD, README_VER_NEW), (README_ANCHOR, README_8722ES)], "README.md v3.7")
    patch_doc(MEM_FILE, [(MEM_VER_OLD, MEM_VER_NEW), (MEM_LAST_OLD, MEM_LAST_NEW)], "Memory_bank.md")
# === fixes/20261124_122700_update_readme_and_mem.py ===
