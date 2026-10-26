# Memory Bank — TRL + кольцевой резонатор на FR4 для HFSS 2025

## Состояние проекта
- Версия: 3.6.1
- Готово:
  - `hfss_trl_kit.py` — единый скрипт-генератор проекта `TRL_Calibration_FR4_Param` / `TRL_Kit`:
    - 3 TRL-стандарта (THRU, LINE, OPEN_A, OPEN_B) с зависимыми длинами;
    - кольцевой резонатор с TAB из кольца-заготовки;
    - **8 параметризованных sheet-портов** (HFSS-выражения в `origin`, `sizes`, `IntLine`);
    - размер порта **4W × 3h = 6.8 × 2.79 мм** — без высших мод (отсечка TE₁₀ 12.2 ГГц > 10 ГГц);
    - **PEC-cap** (3D box `pec`) вплотную к порту (`port_gap = 0`);
    - `subtract(PEC_cap, GND_BOT)` для гальванической задней стенки;
    - **`sizes=["port_h", "port_w"]`** в `create_rectangle(orientation="XZ")` (порядок Z, X);
    - **Open Region** с `pad_value=["15mm","15mm","0.5mm","0.5mm","15mm","0mm"]`;
    - параметры под 10 ГГц: `h=0.93`, `W=1.7`, FR4;
    - ring/TAB: `W_ring=0.4`, `R_tab=0.4`, `W_tab=1.7`, `gap_couple=0.2`;
    - `pitch_trl=25`, `pitch_res=25`.
  - `DEV_LOG.md` — DL-01 … DL-57 + приложение.
- В работе: финальная проверка v3.6.1 (`Validation Check` + `Analyze` 1 проход).
- Не начато:
  - Автоэкспорт `.s2p` после Analyze.
  - Optimetrics-свип при фиксированном `L_thru`.
  - Дисперсионная модель FR4 (Wideband Debye).

## Файлы и их роли
| Файл | Роль | Статус |
|---|---|---|
| `hfss_trl_kit.py` | единый генератор проекта | ✅ v3.6.1 |
| `DEV_LOG.md` | журнал ошибок и уроков | ✅ |
| `memory_bank.md` | сводка состояния | ✅ |

## Ключевые решения
- **Порты полностью параметризованы (DL-55):** все координаты sheet и `IntLine` — HFSS-выражения (`"x_thru"`, `"-L_thru/2"`, `"h"`, `"0mm"`). При изменении `pitch_trl`, `L_thru`, `L_line`, `y_top_res` в `Design Properties` порты сдвигаются вместе с моделью.
- **Размер порта (DL-55):** `4W × 3h = 6.8 × 2.79 мм` (< λ₀/2 = 15 мм) — без высших мод (TE₁₀ отсечка 12.2 ГГц > 10 ГГц).
- **Порядок `sizes` в `create_rectangle(orientation="XZ")` (DL-56):** `[ZSize, XSize]`, т.е. `["port_h", "port_w"]`.
- **PEC-cap вплотную к порту (DL-57):** `port_gap = 0`. При `port_gap > 0` между портом и стенкой остаётся вакуумная «мёртвая зона», волна не возбуждается.
- **`subtract(PEC_cap, GND_BOT)`** — устранение пересечения PEC-стенки и `GND_BOT` в `z ∈ [−t_cu, 0]`.
- **PEC-cap — 3D box (`pec`), не sheet.** Гальваническая задняя стенка порта.
- **Open Region:** `pad_value=["15mm","15mm","0.5mm","0.5mm","15mm","0mm"]`. Padding `0.5 мм` на ±Y — место под PEC-стенку (внутри Region). `0` на −Z — земля на границе.
- **Параметризация HFSS-переменных:**
  - **HFSS-выражения** для геометрии: `L_line`, `r_mean`, `r_out`, `r_in`, `r_tab_in`, `r_tab_out`, `y_top_res`, `x_thru`, `x_line`, `x_open`, `x_res`, `x_left`, `x_right`, `sub_w`, `y_top`, `sub_l`, `port_w`, `port_h`, `t_cap`, `port_gap`.
  - **Python-числа** для `integration_line`-резерва и внутренних проверок.
- **`AssignWavePort(props)` вместо `wave_port()` (DL-53):** `hfss.oboundary.AssignWavePort(props)` с `Objects:=[sheet.name]`. `hfss.wave_port()` не используется, т.к. в 1.8.0 неправильно обрабатывает `IntLine` с выражениями.
- **`IntLine` — HFSS-выражения:** `Start=["x_thru", "-L_thru/2", "h"]`, `End=["x_thru", "-L_thru/2", "0mm"]`.
- **`renormalize=False`** — сохранение физического импеданса.
- **Топология:** подложка + нижняя земля — union ступенчатых блоков + мостики. GND повторяет контур подложки.

## Совместимость (PyAEDT 1.8.0 / 1.10 / AEDT 2025.1)
- `Hfss(project=, design=, new_desktop=)`
- Примитивы: `origin`, `sizes`; `create_cylinder`: `origin`, `radius`, `height`.
- `hfss.get_evaluated_value(name)` — чтение вычисленных значений.
- **`create_rectangle(orientation="XZ", sizes=[ZSize, XSize])`** — порядок `[Z, X]` (DL-56).
- **`hfss.oboundary.AssignWavePort(props)`** — единственный рабочий способ назначить порт на sheet с `IntLine`-выражениями.
- **`IntLine` в `AssignWavePort`** — строки-выражения HFSS (`"x_thru"`, `"h"`, `"0mm"`), а не числа.
- Запуск: `Automation → Run PyAEDT Script` или внешний CPython.

## Известные ограничения
- **`port_gap = 0`** — обязательно. Иначе `Analyze` не возбуждает моду (DL-57).
- **PEC-cap — отдельный объект** (не `unite` с линией). Гальванический контакт — через `subtract(PEC_cap, GND_BOT)` и физическое касание в плоскости порта.
- **При изменении `W` или `h`** — порты (`port_w`, `port_h`) пересчитываются автоматически (HFSS-выражения), но `x_margin_mm` (для габаритов подложки) — Python-число, требует перезапуска.
- **`deembed`** — число (не реализован в v3.6.1). При изменении `L_thru` — перезапуск.
- **FR4 без дисперсии.** Для $f > 5$ ГГц — Wideband Debye.
- **Кольцо — $n=1$.** Для $n=2$ на 10 ГГц: $f_2 \approx 20$ ГГц.

## TODO / backlog
- [ ] Проверить v3.6.1: `Validation Check` + `Analyze` (1 проход).
- [ ] Проверить, что при смене `pitch_trl` / `L_thru` / `L_line` / `y_top_res` порты сдвигаются.
- [ ] Проверить, что нет высших мод (S-параметры гладкие, `|S11|` разумный).
- [ ] Проверить `|S21|` резонатора (цель −25…−35 дБ).
- [ ] Optimetrics-свип при фиксированном `L_thru`.
- [ ] Автоэкспорт `.s2p`.
- [ ] Wideband Debye для FR4.
- [ ] `deembed = L_thru/2` для портов RES (если нужно сместить reference plane).

## Последнее изменение
- Что: v3.6.1 — `port_gap = 0` (PEC-cap вплотную к порту), `sizes=["port_h", "port_w"]` (исправлен порядок Z/X), порты полностью параметризованы через HFSS-выражения.
- Где: `hfss_trl_kit.py`, `DEV_LOG.md` (DL-55, DL-56, DL-57).
- Зачем: устранение высших мод (порт 6.8 × 2.79 < λ₀/2), полная параметризация портов (двигаются с моделью), корректное возбуждение моды (PEC-стенка вплотную к порту).

# === memory_bank.md ===