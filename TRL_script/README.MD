
<div align="center">

# TRL Kit + кольцевой резонатор на FR4 для HFSS 2025

**Версия 3.5.6**

![HFSS](https://img.shields.io/badge/HFSS-2025.1-blue)
![PyAEDT](https://img.shields.io/badge/PyAEDT-1.8.0%20%2F%201.10-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Параметризованная генерация TRL-стандартов и кольцевого резонатора
для характеризации диэлектриков на подложке FR4 в Ansys HFSS 2025.

</div>

---

## О проекте

Скрипт на PyAEDT автоматически создаёт в HFSS 2025 единую печатную плату с калибровочными мерами и измерительным резонатором:

- **THRU** — линия 50 Ом длиной $L_\text{thru}$;
- **LINE** — линия длиной $L_\text{thru} + \Delta L$, где $\Delta L = \lambda_g/4$ на $f_0$;
- **OPEN_A / OPEN_B** — две разомкнутые линии длиной $L_\text{thru}/2$, коллинеарны, порты с противоположных концов;
- **RES** — кольцевой резонатор ($n=1$) с T-лапками и фидерами длиной $L_\text{thru}/2$ для слабой связи ($|S_{21}| \approx -25\ldots-35$ дБ).

Все структуры — на одной подложке FR4. Подложка и нижняя земля повторяют реальную плату (union ступенчатых блоков с мостиками), а не абстрактный bounding box. Модель **не содержит физических разъёмов** — используются идеальные микрополосковые Wave Ports на гранях PEC-стенок.

### Возможности

- **Полная параметризация** через переменные HFSS (`Design Properties`): $L_\text{line}$, $r_\text{mean}$, $r_\text{out}$, $r_\text{in}$, $r_\text{tab\_in}$, $r_\text{tab\_out}$, $y_\text{top\_res}$, координаты структур — всё пересчитывается при изменении $W$, $h$, $\varepsilon_r$, $f_0$.
- **TRL-длины связаны с $L_\text{thru}$** — обеспечивает корректный сдвиг reference plane.
- **Wave Port на грани PEC-стенки** — назначение напрямую на грань 3D-объекта через низкоуровневый `AssignWavePort(Faces)` (PyAEDT 1.8.0 не поддерживает через `wave_port`).
- **PEC-стенка с нахлёстом** — линия утоплена в PEC-стенку на 5 мкм, затем `unite` — единый объект, гальванический контакт.
- **PEC-стенка вычитается из GND_BOT** — устраняет пересечение в области $z \in [-t_\text{cu}, 0]$.
- **Open Region** — padding 15 мм на $\pm X$, $+Z$; 0.5 мм на $\pm Y$ (PEC-стенка внутри Region); 0 на $-Z$ (земля на границе).
- **Совместимость с PyAEDT 1.8.0 / 1.10 / AEDT 2025.1**.

---

## Что такое TRL и зачем это нужно

**TRL** (**T**hru — **R**eflect — **L**ine) — метод калибровки векторного анализатора цепей (VNA), избавляющий от паразитных параметров измерительного тракта (кабелей, разъёмов, тестовых фикстур).

### Суть метода

Вместо точных (и дорогих) мер «Open / Short / Load» используется три простых стандарта:

1. **Thru** — прямая линия передачи, соединяющая два порта. Опорная плоскость.
2. **Reflect** — разомкнутая (Open) или короткозамкнутая (Short) линия с известным коэффициентом отражения.
3. **Line** — отрезок линии с электрической длиной, отличающейся от Thru на четверть волны ($\lambda/4$). Фазовый сдвиг для математического решения.

### Преимущества

- **Высокая точность** на СВЧ/КВЧ — не требуется точная нагрузка 50 Ом.
- **Сдвиг Reference Plane** — перенос плоскости измерения с торца разъёма на любое расстояние внутри линии (например, к центру резонатора).
- **Учёт дисперсии и потерь** в фикстурах.

В проекте TRL-стандарты на одной плате; фидеры резонатора имеют длину $L_\text{thru}/2$, что позволяет использовать `deembed` и автоматически сдвинуть Reference Plane на плоскость T-лапок (TAB).

---

## Установка

### Требования

- Ansys Electronics Desktop 2025 R1 (HFSS).
- Python 3.10+ и PyAEDT 1.8.0+ (для запуска из внешнего интерпретатора).
- Либо встроенный CPython AEDT (для `Automation → Run PyAEDT Script`).

### Установка PyAEDT

```bash
pip install "pyaedt>=1.8.0"
```

Для запуска внутри AEDT: **`Tools → Toolkit → PersonalLib → Install PyAEDT`** (однократно).

---

## Быстрый старт

### Вариант 1 — внешний Python (рекомендуется)

```bash
python hfss_trl_kit.py
```

Скрипт запустит новую сессию AEDT, создаст проект `TRL_Calibration_FR4_Param.aedt` (дизайн `TRL_Kit`), построит все структуры, назначит 8 Wave Ports и сохранит проект.

### Вариант 2 — внутри AEDT

1. Открыть AEDT 2025 R1.
2. **`Automation → Run PyAEDT Script`**.
3. Выбрать `hfss_trl_kit.py`.

> **Внимание:** Не используйте `Tools → Run Script`. Этот механизм запускает IronPython 2.7 без PyAEDT → `Import exception`.

### После создания

1. Открыть проект, проверить `Modeler → Design Properties`.
2. `Modeler → Validation Check` (не должно быть ошибок).
3. `Analyze All`.
4. Экспорт S-параметров: `Results → Solution Data → Export → Touchstone` или `Tools → Calibration Wizard` (Type: TRL).

---

## TRL: связь длин и Reference Plane

Корректная TRL-калибровка и сдвиг опорной плоскости требуют, чтобы длины всех стандартов были производными от $L_\text{thru}$:

| Структура | Длина | Назначение |
|---|---|---|
| **THRU** | $L_\text{thru}$ | Базовая линия; reference plane в её центре ($y=0$) |
| **LINE** | $L_\text{thru} + \Delta L$ | $\Delta L = \lambda_g/4$ — четвертьволновый шаг для TRL |
| **OPEN_A / OPEN_B** | $L_\text{thru}/2$ | Плечи P1/P2 → центр; порты в плоскости LINE-портов |
| **Фидеры RES** | $L_\text{thru}/2$ | De-embedding сдвигает reference plane на плоскость TAB |

Зазор между открытыми концами OPEN_A и OPEN_B равен $L_\text{line} - L_\text{thru} = \Delta L \approx 17.1$ мм (при $f_0 = 2.4$ ГГц).

Для портов резонатора (`P1_RES`, `P2_RES`) предусмотрен параметр **`deembed = L_thru/2`** — сдвигает reference plane на плоскость T-лапок без постобработки.

### Физические формулы (HFSS-выражения)

Эффективная диэлектрическая проницаемость (Hammerstad–Jensen):

$$
\varepsilon_\text{eff} = \frac{\varepsilon_r + 1}{2} + \frac{\varepsilon_r - 1}{2\sqrt{1 + 12\,h/W}}
$$

Четвертьволновый шаг:

$$
\Delta L = \frac{\lambda_g}{4} = \frac{75\ \text{мм}}{f_{0,\text{ГГц}}\sqrt{\varepsilon_\text{eff}}}
$$

Средний радиус кольцевого резонатора ($n=1$):

$$
r_\text{mean} = \frac{300\ \text{мм}}{2\pi f_{0,\text{ГГц}}\sqrt{\varepsilon_\text{ring}}}
$$

---

## Структуры на плате

### Параметры по умолчанию

| Параметр | Значение | Комментарий |
|---|---|---|
| $h$ | 0.93 мм | FR4 |
| $W$ | 1.7 мм | 50 Ом на 10 ГГц |
| $t_\text{cu}$ | 0.035 мм | 1 oz |
| $\varepsilon_r$, $\tan\delta$ | 4.4, 0.02 | FR4 |
| $f_0$ | 10 ГГц | |
| $L_\text{thru}$ | 10 мм | |
| $L_\text{ref}$ | $L_\text{thru}/2$ = 5 мм | вычисляется |
| $L_\text{feed}$ | $L_\text{thru}/2$ = 5 мм | вычисляется |
| $W_\text{ring}$ | 0.4 мм | радиальная толщина кольца |
| $R_\text{tab}$ | 0.4 мм | радиальная толщина TAB |
| $W_\text{tab}$ | 1.7 мм | X-ширина TAB |
| `gap_couple` | 0.2 мм | зазор резонатор–TAB |
| `port_w` | 17 мм ($10W$) | ширина порта |
| `port_h` | 7.44 мм ($8h$) | высота порта |
| `pitch_trl` | 25 мм | шаг между TRL |
| `pitch_res` | 25 мм | шаг от OPEN до резонатора |

### Wave Ports на PEC-стенках

Каждый порт — это **грань PEC-стенки**, а не отдельный лист:

1. **PEC-стенка** — сплошной box `pec` толщиной $t_\text{cu}$, снаружи торца линии.
2. **Линия утоплена** в PEC на 5 мкм (`line_overlap = 0.005 мм`) — гарантия слияния.
3. **`subtract`** PEC-стенки из `GND_BOT` (устранение пересечения в $z \in [-t_\text{cu}, 0]$).
4. **`unite`** PEC-стенки с линией — единый объект.
5. **Поиск грани** по Y-координате центра (`find_face_at_y`) через `oeditor.GetFaceIDs` + `GetFaceCenter`.
6. **Назначение Wave Port** на грань через `hfss.oboundary.AssignWavePort(props)` с `Objects:=[], Faces:=[int(face_id)]`.
7. **Integration line** от полоска ($z=h$) к земле ($z=0$), `renormalize=False`.

### Open Region

```python
hfss.modeler.create_region(
    pad_value=["15mm", "15mm", "0.5mm", "0.5mm", "15mm", "0mm"],
    is_percentage=False, name="Region"
)
```

| Направление | Padding | Причина |
|---|---|---|
| $+X$, $-X$, $+Z$ | 15 мм | $\approx \lambda_0/2$ на 10 ГГц |
| $+Y$, $-Y$ | 0.5 мм | место под PEC-стенку (внутри Region) |
| $-Z$ | 0 мм | земля на границе Region |

---

## Архитектура

```
.
├── hfss_trl_kit.py           # единый скрипт-генератор проекта
├── DEV_LOG.md                # журнал ошибок и уроков (DL-01 … DL-54)
├── memory_bank.md            # сводка состояния проекта
├── README.md                 # данный файл
└── Rules.md / role.md        # правила работы и роль
```

### Модули `hfss_trl_kit.py`

| Блок | Содержание |
|---|---|
| 1 | Параметры (мм, ГГц, порты, PEC) |
| 2 | Инициализация `Hfss`, материалы (FR4) |
| 3 | Переменные HFSS (сложные формулы — Python-числа) |
| 4 | Подложка и нижняя земля (union + мостики) |
| 5 | Металлизация TRL и резонатора |
| 6 | PEC-стенки + `unite` + `AssignWavePort(Faces)` |
| 7 | Open Region |
| 8 | Setup + Sweep |

---

## Разработка и совместимость

### Особенности PyAEDT 1.8.0 / 1.10

| Было | Стало |
|---|---|
| `projectname=...` | `project=...` |
| `new_desktop_session=...` | `new_desktop=...` |
| `position=..., dimensions=...` | `origin=..., sizes=...` |
| `GetVariableValue` / `hfss[name]` | `hfss.get_evaluated_value(name)` |
| `obj.face_centers` / `modeler.get_face_ids` | `hfss.modeler.oeditor.GetFaceIDs` / `GetFaceCenter` |
| `wave_port(assignment=face_id)` | `hfss.oboundary.AssignWavePort(props)` с `Faces` |

### Правила работы с HFSS API

1. **Сложные формулы** (с `sqrt`, `pi`) вычисляются в Python и передаются как готовые числа. HFSS-парсер плохо справляется с длинными вложенными выражениями.
2. **Логические операции** (`unite`, `intersect`, `subtract`) работают in-place на первом аргументе.
3. **Строки в `origin`/`sizes`** — HFSS-выражения; любая переменная в них должна быть объявлена в HFSS (`hfss["name"] = ...`).
4. **Унарный плюс** в начале HFSS-выражения запрещён (`"+L_thru/2"` → ошибка парсера).
5. **Wave Port на грань** — только через `AssignWavePort(props)`. `hfss.wave_port()` для face ID кладёт его в `Objects`, что не работает (нужно `Faces`).
6. **Поиск грани** — `oeditor.GetFaceIDs` + `GetFaceCenter` (с парсингом `str`/`list` и авто-конверсией СИ↔мм).

---

## Известные ограничения

- **`integration_line`** — числа. При изменении `pitch_trl`, `pitch_res`, `L_thru`, `L_line` или `y_top_res` в `Design Properties` порты **не сдвинутся** автоматически (перезапуск скрипта обязателен).
- **`deembed`** — число. При изменении `L_thru` перезапуск обязателен.
- **`GetFaceCenter`** — формат и единицы зависят от версии AEDT. Авто-конверсия покрывает типичные случаи; при экзотическом формате смотрите `[debug]` в логе.
- **FR4 без дисперсии.** Для $f > 5$ ГГц рекомендуется Wideband Debye.
- **Кольцо — $n=1$.** Для $n=2$ на 10 ГГц: $f_2 \approx 20$ ГГц, шире пик (ниже $Q$ из-за $\tan\delta$ FR4).

---

## Roadmap

- [ ] Автоэкспорт `.s2p` после `Analyze`.
- [ ] Optimetrics-свип при фиксированном `L_thru`.
- [ ] Дисперсионная модель FR4 (Wideband Debye).
- [ ] Автоматизация `Calibration Wizard` через PyAEDT (если API позволяет).
- [ ] Опционально: ветка с физическими разъёмами (G14SFB001) для верификации «симуляция vs измерение».

---

## Лицензия

MIT License.

## Ссылки

- Hammerstad E., Jensen O. *Accurate Models for Microstrip Computer-Aided Design*, IEEE MTT-S Int. Microwave Symp. Dig., 1980.
- Pozar D.M. *Microwave Engineering*, 4th ed. — Wiley, 2011. §3.8 (microstrip), §4.5 (TRL).
- Balanis C.A. *Antenna Theory: Analysis and Design*, 4th ed. — Wiley, 2016. §14.2.
- Ansys. *HFSS User's Guide*, Release 2025 R1.
- Ansys. *PyAEDT Documentation*, v1.8.0. <https://aedt.docs.pyansys.com/>
