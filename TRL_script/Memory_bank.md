# Memory Bank — TRL + кольцевой резонатор на FR4 для HFSS 2025

## Состояние проекта
- Версия: 3.5.6
- Готово:
  - `hfss_trl_kit.py` — единый скрипт-генератор проекта `TRL_Calibration_FR4_Param` / `TRL_Kit`:
    - 3 TRL-стандарта (THRU, LINE, OPEN_A, OPEN_B) с зависимыми длинами;
    - кольцевой резонатор с TAB из кольца-заготовки;
    - 8 портов: **Wave Port на грани PEC-стенки** (face ID), не на листе;
    - PEC-стенка снаружи торца линии с нахлёстом 5 мкм, `unite` с линией, `subtract` из `GND_BOT`;
    - **Open Region** с padding `±X=15, ±Y=0.5, +Z=15, -Z=0` (PEC-стенка внутри Region);
    - параметры под 10 ГГц: `h=0.93`, `W=1.7`, FR4 (`εr=4.4`, `tanδ=0.02`);
    - ring/TAB: `W_ring=0.4`, `R_tab=0.4`, `W_tab=1.7`, `gap_couple=0.2`;
    - `pitch_trl=25`, `pitch_res=25`;
    - диагностический `print` для каждой грани (`[debug] face N: y=..., dy=...`).
  - `DEV_LOG.md` — DL-01 … DL-54 + приложение.
- В работе: финальная верификация v3.5.6 (`Validation Check` + `Analyze`).
- Не начато:
  - Автоэкспорт `.s2p` после Analyze.
  - Optimetrics-свип при фиксированном `L_thru`.
  - Дисперсионная модель FR4 (Wideband Debye).

## Файлы и их роли
| Файл | Роль | Статус |
|---|---|---|
| `hfss_trl_kit.py` | единый генератор проекта | ✅ v3.5.6 |
| `DEV_LOG.md` | журнал ошибок и уроков | ✅ |
| `memory_bank.md` | сводка состояния | ✅ |

## Ключевые решения
- **Разъёмы удалены (DL-50).** Модель содержит только плату (подложка + земля + линии + резонатор) и 8 микрополосковых портов.
- **Параметризация:**
  - **HFSS-выражения** для геометрии: `L_line`, `r_mean`, `r_out`, `r_in`, `r_tab_in`, `r_tab_out`, `y_top_res`, `x_thru`, `x_line`, `x_open`, `x_res`, `x_left`, `x_right`, `sub_w`, `y_top`, `sub_l`.
  - **Python-числа** для портов: `x_thru_val`, `x_line_val`, … и `integration_line` (API требует `float`).
- **Порты (v3.5.x):**
  - **PEC-стенка** `PEC_Wall_{name}` — сплошной box `pec` толщиной `t_cap=t_cu`, снаружи торца линии.
  - Линия утоплена в PEC на `line_overlap=0.005 мм` (5 мкм) — гарантия слияния при `unite`.
  - **`subtract(gnd_bot_name, PEC_Wall, keep_originals=True)`** — вычитание PEC из объединённой земли (устранение пересечения в `z ∈ [−t_cu, 0]`).
  - **`unite(line, PEC_Wall)`** — единый объект.
  - **Поиск грани:** `find_face_at_y` через `oeditor.GetFaceIDs` + `GetFaceCenter` (парсинг `str/list/tuple`, авто-конверсия СИ↔мм, fallback через `GetFaceVertexPositions`).
  - **Wave Port на грань** — `hfss.oboundary.AssignWavePort(props)` с `Objects:=[], Faces:=[int(face_id)]`. Fallback — `oeditor.AssignWavePort`.
  - `renormalize=False`.
- **Размеры:** `port_w = 10W = 17 мм`, `port_h = 8h = 7.44 мм`. Порт на грани PEC-стенки (внутри Region).
- **Region:** `pad_value=["15mm", "15mm", "0.5mm", "0.5mm", "15mm", "0mm"]`. PEC-стенка внутри Region.
- **Граничные условия:** явные `assign_perfecte_to_sheets` не нужны — HFSS назначает неявно для меди. `Rad_Region` на Region.

## Совместимость (PyAEDT 1.8.0 / 1.10 / AEDT 2025.1)
- `Hfss(project=, design=, new_desktop=)`
- Примитивы: `origin`, `sizes`; `create_cylinder`: `origin`, `radius`, `height`.
- `hfss.get_evaluated_value(name)` — чтение вычисленных значений.
- `integration_line` — только числа (`float`).
- **Wave Port на грань:** только через `hfss.oboundary.AssignWavePort(props)` (не `hfss.wave_port` — тот кладёт face_id в `Objects`).
- **Поиск граней:** только `hfss.modeler.oeditor.GetFaceIDs` / `GetFaceCenter` (в PyAEDT 1.8.0 нет `obj.face_centers` и `modeler.get_face_ids`).
- Запуск: `Automation → Run PyAEDT Script` или внешний CPython.

## Известные ограничения
- **`integration_line`** — числа. При изменении `pitch_trl`, `pitch_res`, `L_thru`, `L_line` или `y_top_res` в `Design Properties` порты **не сдвинутся** автоматически.
- **`deembed`** — число. При изменении `L_thru` перезапуск обязателен.
- **`GetFaceCenter`** — формат и единицы зависят от версии. Авто-конверсия в `_get_face_y` покрывает оба варианта, но при экзотическом формате возможен `warn`.
- **Нет модели разъёмов** — S-параметры идеальные.
- **FR4 без дисперсии.**
- **Кольцо — $n=1$.**

## TODO / backlog
- [ ] Проверить v3.5.6 (`Validation Check` + `Analyze` 1 проход).
- [ ] Проверить `|S21|` резонатора (цель −25…−35 дБ).
- [ ] Optimetrics-свип при фиксированном `L_thru`.
- [ ] Автоэкспорт `.s2p`.
- [ ] Wideband Debye для FR4.

## Последнее изменение
- Что: v3.5.6 — `PEC_Wall_{name}` вычитается из `GND_BOT` до `unite` с линией. Wave Port по-прежнему на грани PEC через `AssignWavePort(Faces)`.
- Где: `hfss_trl_kit.py`.
- Зачем: устранение пересечения PEC-стенки и `GND_BOT` в области `z ∈ [−t_cu, 0]` (PEC-стенка и земля занимают один и тот же объём).

# === memory_bank.md ===