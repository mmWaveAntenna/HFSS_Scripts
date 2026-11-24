# --- Часть 1/2 ---
from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent  / "DEV_LOG.md"

CHRONO_OLD = "| DL-63 | E | Обрыв длинных кодовых блоков в Markdown → разбиение скриптов на блоки ≤ 100 строк (`Rules.md` v2.1) |"
CHRONO_NEW = (
    "| DL-63 | E | Обрыв длинных кодовых блоков в Markdown → разбиение скриптов на блоки ≤ 100 строк (`Rules.md` v2.1) |\n"
    "| DL-64 | A/D | Верхний земляной экран `GND_TOP` (отступ `gap_gnd = 0.5 мм`), прошивка via и 2-фазные пакетные булевы операции |\n"
    "| DL-65 | D/E | Многократные фоновые сохранения AEDT и торможение Parasolid на `unite` 240+ via → `SetAutoSaveEnabled(False)` + батчевый `unite` |"
)

SEC_A_ANCHOR = "- **Урок:** строго разделять радиус контактного пада полоска (`0.28 мм`) и радиус выреза в земле (`0.50 мм`), проверять ориентацию крепёжных отверстий относительно направления линии и выносить размеры антипадов в переменные дизайна HFSS."
SEC_A_NEW = SEC_A_ANCHOR + """

### DL-64. Верхний земляной экран `GND_TOP` (`gap_gnd = 0.5 мм`), прошивка via и 2-фазные булевы операции
- **Когда:** доработка `TRL_script/hfss_trl_fmcn1476.py` для экранирования микрополосков и резонатора от поверхностных волн в верхнем слое.
- **Задача:** обложить верхний слой (`z = h`) сплошной землёй `GND_TOP` с параметризованным отступом `gap_gnd = 0.5 мм` вдоль линий (`THRU`, `LINE`, `OPEN_A/B`, фидеров `RES`), вокруг внешнего контура резонатора и вокруг земляного островка внутри кольца (`r_in - gap_gnd`), прошив всё земляными via (`via_dia = 0.25 мм`, `via_pitch = 1.2 мм`), а также упростить дерево истории 3D Modeler.
- **Реализация:**
  1. Введены переменные дизайна HFSS: `gap_gnd = "0.5mm"`, `via_dia = "0.25mm"`, `via_pitch = "1.2mm"`, `via_offset = "0.4mm"`.
  2. Скрипт перестроен по двухфазной схеме: **Фаза 1** — создание всех примитивов и регистрация в пулах (`gnd_metal`, `top_cuts`, `bot_cuts`, `all_holes`, `sig_groups`, `coax_ops`); **Фаза 2** — пакетное объединение и вычитание.
- **Урок:** разделение фаз генерации примитивов и булевых операций делает дерево истории HFSS компактным и предсказуемым."""
# --- Часть 2/2 ---
SEC_D_ANCHOR = "- **Урок:** для `create_rectangle(orientation=\"XZ\")` в PyAEDT 1.8.0 — порядок `[ZSize, XSize]`."
SEC_D_NEW = SEC_D_ANCHOR + """

### DL-65. Многократные фоновые сохранения AEDT и замедление Parasolid при `unite` 240+ via
- **Когда:** запуск 2-фазного `hfss_trl_fmcn1476.py` с ~240 переходными via.
- **Симптом:** в процессе генерации геометрии несколько раз запускался прогресс-бар сохранения проекта, а одиночный вызов `modeler.unite` на >200 цилиндрах занимал длительное время.
- **Первопричина:** срабатывание встроенного фонового автосохранения AEDT (`AutoSave`) при большом числе операций модификации модели и квадратичная сложность одиночного булева объединения (Parasolid) на сотнях мелких цилиндров.
- **Исправление:** отключение автосохранения на время генерации (`hfss.odesktop.SetAutoSaveEnabled(False)`) с возвратом перед `hfss.save_project()`, а также разбиение `unite` массива `gnd_metal` на батчи по 50 объектов (`[gnd_parts] + gnd_parts[i:i+50]`).
- **Урок:** при скриптовой генерации моделей с сотнями via отключать `AutoSave` на время работы скрипта и выполнять `unite` порциями по 40–50 примитивов."""

HIST_OLD = "| 3.8 | DL-62 (ориентация футпринта FMCN1476, пад R=0.28 / вырез R=0.50, 12 via, окно 1.50×0.55 мм, `bot_cut_dia`), DL-63 (разбиение кодовых блоков ≤ 100 строк) |"
HIST_NEW = (
    "| 3.8 | DL-62 (ориентация футпринта FMCN1476, пад R=0.28 / вырез R=0.50, 12 via, окно 1.50×0.55 мм, `bot_cut_dia`), DL-63 (разбиение кодовых блоков ≤ 100 строк) |\n"
    "| 3.9 | DL-64 (верхний экран `GND_TOP` с `gap_gnd = 0.5 мм`, прошивка via и 2-фазные булевы операции), DL-65 (`SetAutoSaveEnabled(False)` и батчевый `unite`) |"
)

def apply_patch():
    if not TARGET.exists():
        raise FileNotFoundError(f"Файл не найден: {TARGET}")
    text = TARGET.read_text(encoding="utf-8")
    old_count = len(text.splitlines())
    if "### DL-64." in text and "### DL-65." in text:
        print(f"[{ts} MSK] {TARGET.name}: изменений не требуется (идемпотентность).")
        return
    updated = (
        text.replace(CHRONO_OLD, CHRONO_NEW)
            .replace(SEC_A_ANCHOR, SEC_A_NEW)
            .replace(SEC_D_ANCHOR, SEC_D_NEW)
            .replace(HIST_OLD, HIST_NEW)
    )
    TARGET.write_text(updated, encoding="utf-8")
    new_count = len(updated.splitlines())
    print(f"[{ts} MSK] === {TARGET} ===")
    print(f"  Было строк: {old_count}")
    print(f"  Стало строк: {new_count} ({new_count - old_count:+d})")
    print("  ✓ применено: добавлены записи DL-64 и DL-65 (версия 3.9).")

if __name__ == "__main__":
    apply_patch()
# === fixes/20261124_103000_update_dev_log_dl64_dl65.py ===
