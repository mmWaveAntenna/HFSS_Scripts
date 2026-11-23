from datetime import datetime, timedelta, timezone
from pathlib import Path

MSK = timezone(timedelta(hours=3))
ts = datetime.now(MSK).strftime("%Y%m%d_%H%M%S")
TARGET = Path(__file__).resolve().parent.parent / "Rules.md"

OLD_HEADER = """**Версия:** 2.0
**Область:** процесс + инженерные соглашения (Ansys HFSS 2025.1 / PyAEDT 1.8.0+)
**Изменение в 2.0:** полная адаптация правил под проект TRL-калибровки и кольцевого резонатора в HFSS/PyAEDT; удалены правила GUI (PySide6) из прошлого проекта; добавлены ограничения PyAEDT/AEDT API (DL-01 … DL-58)."""

NEW_HEADER = """**Версия:** 2.1
**Область:** процесс + инженерные соглашения (Ansys HFSS 2025.1 / PyAEDT 1.8.0+)
**Изменение в 2.1:** добавлено правило разбиения длинных скриптов на кодовые блоки по ≤ 100 строк (защита от обрыва Markdown при копировании)."""

OLD_SECTION = """### 2.2. Формат ответа с кодом
- Код — в блоках с указанием языка: ` ```python `.
- **Один модуль = один отдельный кодовый блок.**
- **Путь к файлу — комментарием в конце модуля**: `# === path/to/file.py ===`.
- Заголовок перед блоком **не ставится**.
- Между блоками — одна пустая строка.
- После кода — краткое резюме изменений (таблица «было → стало» или список)."""

NEW_SECTION = """### 2.2. Формат ответа с кодом
- Код — в блоках с указанием языка: ` ```python `.
- **Лимит длины блока (≤ 100 строк):** если модуль или патч-скрипт длиннее 100 строк, разбивать его на последовательные кодовые блоки (`# --- Часть 1/N ---`, `# --- Часть 2/N ---` в первой строке блока), чтобы парсер Markdown не обрывал разметку при копировании.
- **Путь к файлу — комментарием в конце последнего блока модуля**: `# === path/to/file.py ===`.
- Между блоками — одна пустая строка.
- После кода — краткое резюме изменений (таблица «было → стало» или список)."""

text = TARGET.read_text(encoding="utf-8")
old_count = len(text.splitlines())
updated = text.replace(OLD_HEADER, NEW_HEADER).replace(OLD_SECTION, NEW_SECTION)
TARGET.write_text(updated, encoding="utf-8")
new_count = len(updated.splitlines())
print(f"[{ts} MSK] === {TARGET} ===\n  Было строк: {old_count}\n  Стало строк: {new_count} ({new_count - old_count:+d})")
# === fixes/20261123_120500_update_rules_chunking.py ===
