<div align="center">

# TRL Kit + кольцевой резонатор на FR4 для HFSS 2025

**Версия 3.8**

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

- **THRU** — микрополосковая линия 50 Ом длиной $L_\text{thru}$;
- **LINE** — линия длиной $L_\text{thru} + \Delta L$, где $\Delta L = \lambda_g/4$ на $f_0$;
- **OPEN_A / OPEN_B** — две разомкнутые линии длиной $L_\text{thru}/2$, коллинеарны, порты с противоположных концов;
- **RES** — кольцевой резонатор ($n=1$) с T-лапками и фидерами длиной $L_\text{thru}/2$ для слабой связи ($|S_{21}| \approx -25\ldots-35$ дБ).
- **RES2** *(в `hfss_trl_fmcn1476.py` v2.5)* — второй кольцевой резонатор ($n=1$) с ортогональными фидерами под углом **90°** (`-Y` и `+X`) для выделения анизотропии диэлектрика FR4.

Для верификации с реальными вертикальными разъёмами **Fairview Microwave FMCN1476 (2.92 мм)** используется отдельный производственный генератор `hfss_trl_fmcn1476.py` (v2.5, 10 портов, стек FR4 $h = 0.115$ мм, $W = 0.2$ мм, сплошной верхний экран `GND_TOP` с отступом `gap_gnd = 0.5 мм` и прошивкой via по технологическим нормам **Резонит** $\ge 200$ мкм от края отверстия до края меди).

Все структуры размещены на единой ступенчатой подложке FR4, повторяющей реальный контур платы (union блоков с перемычками), а не абстрактный bounding box. В `hfss_trl_kit.py` используются **параметризованные sheet-порты** ($4W \times 3h$) с 3D PEC-крышками.

### Возможности

- **Полная параметризация** через переменные HFSS (`Design Properties`): $L_\text{line}$, $r_\text{mean}$, $r_\text{out}$, $r_\text{in}$, $r_\text{tab\_in}$, $r_\text{tab\_out}$, $y_\text{top\_res}$, координаты структур и **все 8 портов** пересчитываются при изменении $W$, $h$, $\varepsilon_r$, $f_0$, $L_\text{thru}$, `pitch_trl`.
- **TRL-длины связаны с $L_\text{thru}$** — обеспечивает корректный сдвиг опорной плоскости (reference plane).
- **Исключение высших мод в портах** — поперечное сечение порта уменьшено до $4W \times 3h = 6.8 \times 2.79$ мм ($< \lambda_0/2$ на 10 ГГц, частота отсечки $TE_{10}$ составляет 12.2 ГГц).
- **PEC-крышка вплотную к порту (`port_gap = 0`)** — 3D box из `pec` толщиной $t_\text{cu}$ с вычитанием из `GND_BOT` для гальванического замыкания обратной стороны порта.
- **Назначение Wave Port через `AssignWavePort`** — sheet-порт в плоскости XZ с явной интеграционной линией `IntLine` через HFSS-выражения и `renormalize=False`.
- **Open Region** — padding 15 мм по $\pm X, +Z$; 0.5 мм по $\pm Y$ (для размещения PEC-крышек внутри Region); 0 мм по $-Z$ (нижняя земля на границе).
- **Совместимость с PyAEDT 1.8.0 / 1.10 / AEDT 2025.1**.

---

## Что такое TRL и зачем это нужно

**TRL** (**T**hru — **R**eflect — **L**ine) — метод калибровки векторного анализатора цепей (VNA), исключающий влияние паразитных параметров измерительного тракта (кабелей, разъёмов, тестовых переходов).

### Суть метода

1. **Thru** — прямая линия передачи, соединяющая два порта; задаёт опорную плоскость (reference plane).
2. **Reflect** — разомкнутая (Open) или короткозамкнутая (Short) линия с высоким коэффициентом отражения ($|\Gamma| \approx 1$).
3. **Line** — отрезок линии с электрической длиной, отличающейся от Thru на четверть волны ($\lambda_g/4$).

### Преимущества

- **Высокая точность** на СВЧ/КВЧ — не требуется эталонная согласованная нагрузка 50 Ом.
- **Сдвиг Reference Plane** — перенос плоскости отсчёта с торца разъёма непосредственно к плоскости связи резонатора (`TAB`).
- **Учёт дисперсии и потерь** в подводящих линиях и переходах.

---

## Установка

### Требования

- Ansys Electronics Desktop 2025 R1 (HFSS).
- Python 3.10+ и `pyaedt >= 1.8.0` (для запуска из внешнего интерпретатора).
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

> **Внимание:** Не используйте `Tools → Run Script`. Этот механизм запускает IronPython 2.7 без PyAEDT, что вызовет `ImportError`.

### После создания модели

1. Открыть проект, проверить `Modeler → Design Properties`.
2. Выполнить `Modeler → Validation Check` (ошибок быть не должно).
3. Запустить `Analyze All`.
4. Экспортировать S-параметры: `Results → Solution Data → Export → Touchstone` или выполнить деэмбеддинг в `Tools → Calibration Wizard` (Type: TRL).

---

## Методика TRL-калибровки на VNA Agilent 8722ES (1 стандарт LINE)

Для платы на FR4 ($h = 0.115$ мм, $W = 0.2$ мм, $L_\text{thru} = 10$ мм, $\Delta L = 4.20$ мм, $L_\text{ref} = L_\text{feed} = 5$ мм, $\varepsilon_\text{eff} \approx 3.19$) опорная плоскость (reference plane) задаётся в **центре `THRU`** (совпадает с плоскостью T-лапок резонатора `TAB`). Рабочее фазовое окно $20^\circ \le \Delta\varphi \le 160^\circ$ для одной меры `LINE` охватывает диапазон **2.22 – 17.78 ГГц**.

### 1. Настройка полосы и приёмника VNA
1. **`PRESET`** → **`START`** `2.5 GHz`, **`STOP`** `17.5 GHz`.
2. **`MENU` → `NUMBER OF POINTS`** → `401` (или `801`); **`AVG` → `IF BW`** → `1 kHz`; **`POWER`** → `-5 dBm`.

### 2. Создание User Cal Kit (`CAL → CAL KIT → SELECT CAL KIT → USER KIT → MODIFY CAL KIT`)
1. **`STD 1` (`THRU`, тип `DELAY / THRU`):** `OFFSET DELAY = 0 ps`, `OFFSET Z0 = 50 Ohm`, `OFFSET LOSS = 0`.
2. **`STD 2` (`OPEN`, тип `OPEN`):** `OFFSET DELAY = 0 ps` (торец `OPEN` длиной $L_\text{thru}/2$ лежит в опорной плоскости), `OFFSET Z0 = 50 Ohm`, `MIN FREQ = 2.2 GHz`, `MAX FREQ = 18 GHz`.
3. **`STD 3` (`LINE`, тип `DELAY / THRU`):** задержка $\tau_{\Delta L} = \Delta L\sqrt{\varepsilon_\text{eff}}/c \approx \mathbf{25.0\text{ ps}}$, `OFFSET Z0 = 50 Ohm`, `MIN FREQ = 2.25 GHz`, `MAX FREQ = 17.7 GHz`.
4. **`SPECIFY CLASS → MORE → TRL / LRM`:** назначить `THRU` → `STD 1`, `S11 REFLECT` / `S22 REFLECT` → `STD 2`, `LINE / MATCH` → `STD 3`. Сохранить через **`KIT DONE` → `SAVE USER KIT`**.

### 3. Измерение стандартов и верификация (`CAL → CALIBRATE MENU → TRL 2-PORT`)
1. **`THRU`:** подключить кабели Порта 1 и Порта 2 к `P_THRU_1` и `P_THRU_2`.
2. **`REFLECT`:** подключить Порт 1 к `P_OPEN_A`, Порт 2 к `P_OPEN_B` (`S11 REFLECT`, `S22 REFLECT`).
3. **`LINE`:** подключить кабели к `P_LINE_1` и `P_LINE_2` (`LINE / MATCH`).
4. **`ISOLATION → OMIT ISOLATION`**, затем **`DONE TRL 2-PORT`** (на экране загорится **`Cor`**).
5. **Контроль:** на `THRU` должно быть $\angle S_{21} = 0.0^\circ \pm 0.5^\circ$, $|S_{11}| < -35$ дБ; на `OPEN` — $\angle S_{11} \approx 0^\circ$. После проверки подключить **`P_RES_1` / `P_RES_2`** (резонатор 180°) или **`P_RES2_1` / `P_RES2_2`** (ортогональный резонатор 90°) для прямого измерения $f_0$, расщепления мод и $Q_L$.

---

## TRL: связь длин и Reference Plane

Длины всех стандартов и фидеров являются производными от $L_\text{thru}$:

| Структура | Длина | Назначение |
|---|---|---|
| **THRU** | $L_\text{thru}$ | Базовая линия; reference plane в её центре ($y=0$) |
| **LINE** | $L_\text{thru} + \Delta L$ | $\Delta L = \lambda_g/4$ — четвертьволновый фазовый сдвиг для TRL |
| **OPEN_A / OPEN_B** | $L_\text{thru}/2$ | Плечи отражателей; порты в плоскости LINE-портов |
| **Фидеры RES** | $L_\text{thru}/2$ | При `deembed = L_thru/2` сдвигают reference plane на плоскость TAB |

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

### Параметры по умолчанию (`hfss_trl_kit.py` v3.6.1)

| Параметр | Значение | Комментарий |
|---|---|---|
| $h$ | 0.93 мм | Толщина подложки FR4 |
| $W$ | 1.7 мм | Ширина микрополоска 50 Ом на 10 ГГц |
| $t_\text{cu}$ | 0.035 мм | Толщина медной фольги (1 oz) |
| $\varepsilon_r$, $\tan\delta$ | 4.4, 0.02 | Параметры диэлектрика FR4 |
| $f_0$ | 10 ГГц | Расчётная центральная частота |
| $L_\text{thru}$ | 10 мм | Длина стандарта THRU |
| $L_\text{ref}$ | $L_\text{thru}/2 = 5$ мм | Длина плеча OPEN (вычисляется) |
| $L_\text{feed}$ | $L_\text{thru}/2 = 5$ мм | Длина фидера резонатора (вычисляется) |
| $W_\text{ring}$ | 0.4 мм | Ширина проводника кольца |
| $R_\text{tab}$ | 0.4 мм | Радиальная ширина T-лапки связи |
| $W_\text{tab}$ | 1.7 мм | Ширина T-лапки по оси X |
| `gap_couple` | 0.2 мм | Емкостной зазор между кольцом и T-лапкой |
| `port_w` | $4W = 6.8$ мм | Ширина Wave Port |
| `port_h` | $3h = 2.79$ мм | Высота Wave Port |
| `port_gap` | 0.0 мм | Зазор PEC-крышки от порта (строго 0) |
| `pitch_trl` | 25 мм | Шаг между TRL-структурами по оси X |
| `pitch_res` | 25 мм | Шаг от OPEN до резонатора по оси X |

### Параметризованные Wave Ports на sheet-объектах

1. **Sheet-порт** (`PortSheet_<name>`) создаётся в плоскости `XZ` через `create_rectangle(orientation="XZ", sizes=["port_h", "port_w"])` (порядок `[Z, X]`).
2. **PEC-крышка** (`PEC_Cap_<name>`) — 3D box из `pec` толщиной `t_cu`, устанавливается вплотную к обратной стороне порта (`port_gap = 0.0`).
3. **`subtract(GND_BOT, PEC_Cap, keep_originals=True)`** — исключает пересечение объёмов в слое $z \in [-t_\text{cu}, 0]$.
4. **`hfss.oboundary.AssignWavePort(props)`** — назначает порт на `sheet.name` с `IntLine` через HFSS-выражения и `RenormalizeAllTerminals = False` (`CharImp = "Zpi"`).

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
| $+Y$, $-Y$ | 0.5 мм | Запас для размещения 3D PEC-крышки внутри Region |
| $-Z$ | 0 мм | Нижняя земля `GND_BOT` совпадает с границей Region |

---

## Архитектура

```
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
```

---

## Разработка и совместимость (PyAEDT 1.8.0+)

1. **Порядок размеров `create_rectangle(orientation="XZ")` (DL-56):** передаётся как `[Z_size, X_size]`, то есть `["port_h", "port_w"]`.
2. **`port_gap = 0.0` (DL-57):** PEC-крышка должна примыкать вплотную к листу порта; зазор срывает возбуждение моды.
3. **Назначение Wave Port (DL-53):** выполняется через `hfss.oboundary.AssignWavePort(props)` с `IntLine` в виде строк-выражений (`Start=[x_expr, y_expr, "h"]`, `End=[x_expr, y_expr, "0mm"]`).
4. **Чтение переменных (DL-06…DL-08):** используется `hfss.get_evaluated_value(name)` (возвращает число в СИ).
5. **Унарный плюс (DL-15):** запрещён в начале выражений HFSS (`"+L_thru/2"` → ошибка парсера).

---

## Известные ограничения

- **`x_margin_mm`** для ширины блоков подложки вычисляется в Python при генерации модели; при значительном увеличении `W` в `Design Properties` следует перезапустить скрипт.
- **De-embedding для портов `RES`** (`deembed = L_thru/2`) не включён по умолчанию в `AssignWavePort` и выполняется на этапе постобработки / Calibration Wizard.
- **FR4 без дисперсии:** заданы постоянные $\varepsilon_r = 4.4$, $\tan\delta = 0.02$. Для точного анализа выше 5 ГГц рекомендуется перейти на модель Wideband Debye.
- **Кольцевой резонатор рассчитан на первую гармонику ($n=1$):** на $f_0 = 10$ ГГц второй резонанс ($n=2$) находится около 20 ГГц.

---

## Roadmap

- [ ] Автоматический экспорт `.s2p` файлов после завершения `Analyze`.
- [ ] Блок Optimetrics-свипа (`W`, `dL`, `er`) при фиксированном `L_thru`.
- [ ] Опциональная дисперсионная модель FR4 (Wideband Debye).
- [ ] Интеграция деэмбеддинга `deembed = L_thru/2` для портов резонатора.

---

## Лицензия

MIT License.

## Ссылки

- Hammerstad E., Jensen O. *Accurate Models for Microstrip Computer-Aided Design*, IEEE MTT-S Int. Microwave Symp. Dig., 1980.
- Pozar D.M. *Microwave Engineering*, 4th ed. — Wiley, 2011. §3.8 (microstrip), §4.5 (TRL).
- Balanis C.A. *Antenna Theory: Analysis and Design*, 4th ed. — Wiley, 2016.
- Ansys. *HFSS User's Guide*, Release 2025 R1.
- Ansys. *PyAEDT Documentation*, v1.8.0. <https://aedt.docs.pyansys.com/>
