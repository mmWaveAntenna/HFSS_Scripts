from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent  / "DEV_LOG.md"

BROKEN_ROWS = """| DL-66 | E | Стандарт ответа чата: точечные diff-патч-скрипты (`str.replace`) + лимит кодового блока ≤ 100 строк (`Rules.md` v2.2) |

---

| DL-67 | A | Ступенька пина в окне (`BossBore` Ø 1.27 мм), непрерывный канал `Notch`, нормы Резонит (≥ 200 мкм от края via) и 2-й резонатор (90°) |

---

| DL-68 | A/D | Постоянный шаг `via_pitch = 1.0 мм` при изменении радиуса/частоты через `min(start + k*pitch, end)` с запасом 2.5× |

---

| DL-69 | D | `variable 'r_via_out' does not exist` при объявлении зависимой переменной до `r_out` / `r_in` |"""

FIXED_ROWS = """| DL-66 | E | Стандарт ответа чата: точечные diff-патч-скрипты (`str.replace`) + лимит кодового блока ≤ 100 строк (`Rules.md` v2.2) |

| DL-67 | A | Ступенька пина в окне (`BossBore` Ø 1.27 мм), непрерывный канал `Notch`, нормы Резонит (≥ 200 мкм от края via) и 2-й резонатор (90°) |
| DL-68 | A/D | Постоянный шаг `via_pitch = 1.0 мм` при изменении радиуса/частоты через `min(start + k*pitch, end)` с запасом 2.5× |
| DL-69 | D | `variable 'r_via_out' does not exist` при объявлении зависимой переменной до `r_out` / `r_in` |"""

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
if BROKEN_ROWS in text:
    updated = text.replace(BROKEN_ROWS, FIXED_ROWS, 1)
    TARGET.write_text(updated, encoding="utf-8")
    new_count = len(updated.splitlines())
    print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
else:
    print(f"[{ts} MSK] Таблица уже в едином формате.")
# === fixes/20261124_134000_clean_devlog_table.py ===
