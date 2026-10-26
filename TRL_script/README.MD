<div align="center">

# TRL Kit + кольцевой резонатор на FR4 для HFSS 2025

**Версия 2.2.9**

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
- **OPEN_A / OPEN_B** — две разомкнутые линии длиной $L_\text{thru}/2$ каждая, коллинеарны, порты с противоположных концов;
- **RES** — кольцевой резонатор ($n=1$) с T-лапками и фидерами длиной $L_\text{thru}/2$ для слабой связи ($|S_{21}| \approx -25\ldots-35$ дБ);
- **Модели разъемов G14SFB001 (1.85 мм)** — физическая внутренняя часть коаксиала, металлическая стенка и лапки, сидящие на посадочных местах.

Все структуры — на одной подложке FR4. Подложка и нижняя земля повторяют реальную плату (union ступенчатых блоков с мостиками), а не абстрактный bounding box.

### Возможности

- **Полная параметризация через переменные HFSS** (`Design Properties`): $\varepsilon_\text{eff}$, $\Delta L$, $L_\text{line}$, $L_\text{ref}$, $L_\text{feed}$, $r_\text{mean}$, $r_\text{out}$, $r_\text{in}$, $r_\text{tab\_in}$, $r_\text{tab\_out}$, $y_\text{top\_res}$, габариты подложки — всё пересчитывается при изменении $W$, $h$, $\varepsilon_r$, $f_0$.
- **TRL-длины связаны с $L_\text{thru}$** — обеспечивает корректный сдвиг reference plane.
- **Физическая модель перехода на коаксиал** — пин разъема смещен по Z так, чтобы пересекаться с микрополоском на 8 мкм, обеспечивая гальваническую связь.
- **Топология TopPad**: на верхнем слое нет сплошной заливки земли. Создаются локальные площадки (длиной 5.58 мм) под лапки разъемов.
- **Монтажные пазы**: овальные (obround) пазы (2.0 × 1.4 мм) с центром на расстоянии 3.0 мм от края платы, ориентированы вдоль оси Y для компенсации технологических погрешностей.
- **Технологический зазор `gap_foil`** (0.2 мм) — вся медь (линии, пады, TopPad) отступает от края платы.
- **8 Wave Ports** на торцах коаксиалов (строго симметрично).
- **Частотная развёртка** 1–6 ГГц (LinearCount, 101 точка).
- **Совместимость с PyAEDT 1.8.0 / 1.10.dev0 / AEDT 2025.1**.

---

## Установка

### Требования

- Ansys Electronics Desktop 2025 R1 (HFSS).
- Python 3.10+ и PyAEDT 1.8.0+ — для запуска из внешнего интерпретатора.
- Либо встроенный CPython AEDT — для `Run PyAEDT Script`.

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

Скрипт запустит новую сессию AEDT, создаст проект `TRL_Calibration_FR4_Param.aedt` и дизайн `TRL_Kit`, построит все структуры, назначит 8 портов, добавит setup и sweep, сохранит проект.

### Вариант 2 — внутри AEDT

1. Открыть AEDT 2025 R1.
2. **`Automation → Run PyAEDT Script`** (либо `Tools → Toolkit → PersonalLib → Run PyAEDT Script`).
3. Выбрать `hfss_trl_kit.py`.

> Не использовать `Tools → Run Script` — там IronPython 2.7 без PyAEDT → `Import exception: no module`.

### После создания

1. Открыть проект, проверить `Modeler → Design Properties`.
2. `Analyze All`.
3. Экспорт S-параметров: `Results → Solution Data → Export → Touchstone` или `Tools → Calibration Wizard` (Type: TRL).

---

## TRL: связь длин и reference plane

Корректная TRL-калибровка и сдвиг reference plane требуют, чтобы длины всех стандартов были производными от $L_\text{thru}$:

| Структура | Длина | Назначение |
|---|---|---|
| **THRU** | $L_\text{thru}$ | базовая линия; reference plane после калибровки — в её центре (y=0) |
| **LINE** | $L_\text{thru} + \Delta L$ | $\Delta L = \lambda_g/4$ — четвертьволновый шаг для TRL |
| **OPEN_A** | $L_\text{thru}/2$ | плечо P1 → центр; порт в плоскости LINE-порта (y = $-L_\text{line}/2$) |
| **OPEN_B** | $L_\text{thru}/2$ | плечо P2 → центр; порт в плоскости LINE-порта (y = $+L_\text{line}/2$) |
| **Фидеры RES** | $L_\text{thru}/2$ | de-embedding сдвигает reference plane резонатора на плоскость TAB |

Зазор между открытыми концами OPEN_A и OPEN_B равен $L_\text{line} - L_\text{thru} = \Delta L \approx 17.1$ мм (при $f_0 = 2.4$ ГГц) — достаточно для независимых REFLECT-стандартов без дополнительного `gap_open`.

### Сдвиг reference plane

- **После TRL-калибровки** reference plane совпадает с плоскостями портов (`±L_\text{thru}/2` для THRU, `±L_\text{line}/2` для LINE, `±L_\text{line}/2` для OPEN-портов). Сдвиг на $L_\text{thru}/2$ приводит к центру THRU (y=0).
- **Для резонатора** `deembed = L_\text{thru}/2` при создании портов `P1_RES` / `P2_RES` автоматически сдвигает reference plane на плоскость TAB.

---

## Структуры на плате

### Параметры по умолчанию

| Параметр | Значение | Комментарий |
|---|---|---|
| $h$ | 1.6 мм | FR4 |
| $W$ | 3.0 мм | 50 Ом |
| $t_\text{cu}$ | 0.035 мм | 1 oz |
| $\varepsilon_r$, $\tan\delta$ | 4.4, 0.02 | FR4 |
| $L_\text{thru}$ | 10 мм | |
| $L_\text{ref}$ | $L_\text{thru}/2$ = 5 мм | вычисляется |
| $L_\text{feed}$ | $L_\text{thru}/2$ = 5 мм | вычисляется |
| $f_0$ | 2.4 ГГц | |
| $W_\text{ring}$ | 2.0 мм | радиальная толщина кольца |
| $R_\text{tab}$ | 2.0 мм | радиальная толщина TAB |
| `gap_couple` | 0.3 мм | зазор резонатор–TAB |
| `conn_pin_offset` | 4.24 мм | от края ПП до штыря |
| `conn_ins_depth` | 5.08 мм | глубина посадочного места |
| `pad_size_y` | 5.58 мм | длина земляной площадки TopPad |
| `pitch_trl` | 45 мм | шаг между TRL |
| `pitch_res` | 35 мм | шаг от OPEN до резонатора |

### Раскладка по X

| X | Структура | Порты |
|---|---|---|
| `-pitch_trl` | THRU | P1, P2, $y = \pm L_\text{thru}/2$ |
| $0$ | LINE | P1, P2, $y = \pm L_\text{line}/2$ |
| `+pitch_trl` | OPEN_A / OPEN_B | P1_OPEN_A, P1_OPEN_B (в плоскостях LINE) |
| `+pitch_trl + pitch_res`| RES (кольцо + TAB + фидеры) | P1_RES, P2_RES, deembed $L_\text{thru}/2$ |

### Физические формулы (выражения HFSS)

$$
\varepsilon_\text{eff} = \frac{\varepsilon_r + 1}{2} + \frac{\varepsilon_r - 1}{2\sqrt{1 + 12\,h/W}}
$$

$$
\Delta L = \frac{\lambda_g}{4} = \frac{75\ \text{мм}}{f_{0,\text{ГГц}}\sqrt{\varepsilon_\text{eff}}}
$$

$$
r_\text{mean} = \frac{300\ \text{мм}}{2\pi f_{0,\text{ГГц}}\sqrt{\varepsilon_\text{ring}}}
\qquad (n=1)
$$

При $f_0 = 2.4$ ГГц, $W_\text{ring} = 2$ мм: $\varepsilon_\text{ring} \approx 3.35$, $r_\text{mean} \approx 10.9$ мм.

---

## Интеграция с HFSS

### Модель коаксиального разъема
- **Коаксиал**: Диаметры пина `0.23 мм`, диэлектрика `0.75 мм`, оплетки `1.85 мм`.
- **Z-смещение**: `z_coax = h + t_cu - 0.008mm + r_pin_coax`. Пин пересекает медь на 8 мкм.
- **Стенка и лапки**: ширина 12.7 мм, высота стенки 9.53 мм, высота лапок 2.5 мм.

### Wave Ports
- **Sheets** — HFSS-выражения, следуют за геометрией.
- **Integration line** — числовые координаты (float, мм).
- **Deembed** для RES-портов — число $L_\text{thru}/2$ мм.

### Граничные условия
- **GND_BOT**: Perfect E (union прямоугольников).
- **GND_TOP (TopPad)**: Perfect E (локальные площадки, без сплошной заливки).
- **AirBox**: Radiation.

### Порядок операций
Металл → порты → setup → sweep.

---

## Архитектура

```
.
├── hfss_trl_kit.py           # единый генератор проекта
├── memory_bank.md            # текущее состояние
├── DEV_LOG.md                # журнал ошибок и уроков
├── README.md
└── Rules.md / role.md
```

### `hfss_trl_kit.py`

| Блок | Содержание |
|---|---|
| 1 | Параметры (мм, ГГц) |
| 2 | `Hfss`, материалы (FR4, PTFE) |
| 3 | Переменные (сложные формулы предвычислены в Python) |
| 4 | Подложка, нижняя земля, верхние площадки (TopPad), овальные пазы |
| 5 | Металлизация: TRL, OPEN_A/B, кольцо, фидеры |
| 6 | Модели разъемов (коаксиал, стенка, лапки) и порты |
| 7 | Setup + Sweep |
| 8 | Сохранение, диагностика |

---

## Разработка

### Совместимость PyAEDT 1.8.0 / 1.10 / AEDT 2025.1

| API | Устарело | Актуально |
|---|---|---|
| `Hfss(...)` | `projectname`, `designname` | `project`, `design` |
| Новая сессия | `new_desktop_session` | `new_desktop` |
| Примитивы | `position`, `dimensions` | `origin`, `sizes` |
| Чтение переменной | `GetVariableValue` | `hfss.get_evaluated_value(name)` |
| `integration_line` | строки-выражения | **числа** (float) |
| Логические операции | ожидание нового имени | in-place на первом аргументе |
| Строки в `origin` / `sizes` | Python-имена (`W_mm`) | HFSS-переменные (`W`, `pitch`); **без унарного `+`** |

### Синтаксис
Без `from __future__ import annotations`, без f-строк и аннотаций типов — для совместимости с IronPython 2.7.

---

## Известные ограничения

- **3D STEP-модель G14SFB001** отсутствует в открытом доступе, параметры взяты из PDF-чертежа.
- **`deembed` RES-портов** — число. При изменении `L_thru` — перезапуск скрипта.
- **`integration_line`** — числа, движутся за портом (DL-14).
- **FR4 без дисперсии.** Для $f > 5$ ГГц — Wideband Debye.
- **Кольцо — $n=1$.** Для других мод — пересчитать `r_mean`.

---

## Roadmap

- [ ] Автоэкспорт `.s2p` после `Analyze`.
- [ ] Optimetrics-свип при фиксированном `L_thru`.
- [ ] Дисперсионная модель FR4 (Wideband Debye).
- [ ] Автоматизация `Calibration Wizard` (если API позволяет).
- [ ] Запрос STEP-модели G14SFB001 у производителя.

---

## Лицензия
MIT.

## Ссылки
- Hammerstad E., Jensen O. *Accurate Models for Microstrip CAD*, IEEE MTT-S, 1980.
- Pozar D.M. *Microwave Engineering*, 4th ed., 2011.
- Ansys. *PyAEDT Documentation*, v1.8.0.
