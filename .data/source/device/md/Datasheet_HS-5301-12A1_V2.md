# Industrial Computer ATX Series
## 300W Multiple Output Active PFC Data Sheet

*For the latest revision, please visit power.liteon.com*

## Description

This is a high-power factor (PF), multiple-output AC to DC switching mode power supply unit which can provide up to 300 watts continuous with forced cooling by a smart FSC (fan speed control) circuitry. There is a built-in auxiliary converter (5VSB) for better energy saving. It complies with 80+gold as well as worldwide safety and EMC regulations (refer to details below). It is suitable for various industrial PC applications.

## Features

- Full AC input voltage range design.
- High power factor and less fictitious power.
- Withstand 300Vac surge voltage for 5 seconds.
- Full Protections: Short-circuit/ Over-voltage/ Over-current/ Over temperature.
- INTEL® standard ATX form factor.
- Meet 80+gold.
- IEC/EN 62368-1 design compliance.
- Up to 5000 meters operating altitude (note#4)
- High efficiency and high reliability.
- REM_ON/OFF and PWR_OK signal

## Electrical Specification

**Model Name:** HS-5301-12A1

**Output**

| Parameter | 12V | 5V | 3.3V | -12V | 5Vsb |
|---|---|---|---|---|---|
| Rated power | 300W | | | | |
| Rated voltage | 12V | 5V | 3.3V | -12V | 5Vsb |
| Rated current | 25A | 20A | 20A | 0.3A | 3A |
| Ripple & Noise (max.) (note #2) | 120mV | 50mV | 50mV | 120mV | 50mV |
| Line & load regulation | ±5% | ±5% | ±5% | ±10% | ±5% |
| Hold-up time (typ.) (note #5) | 16ms | | | | |
| Timing: AC ON delay / rising (max.) | 2 sec / 20ms | | | | |

**Input**

| Parameter | Value |
|---|---|
| Rated voltage range | 100~240Vac |
| Operated voltage range | 90~264Vac, 300Vac for 5 sec |
| Current range (max.) | 6.0A/100Vac |
| Inrush current | No component damaged (<I²t) |
| Frequency range | 50-60Hz |
| Leakage current (max.) | 3.5mA at 240Vac |
| Efficiency (min.) | 87% - 90% - 87% (at 20% - 50% - 100% of rated loading) |
| Standby power saving (min.) | Pin<1W at 5Vsb/0.1A; Pin<0.5W at Po=0.25W (at REM_OFF, efficiency>50%) |

**Protection Function**

| Parameter | Value |
|---|---|
| Over voltage (max.) | 140% of rated voltage, latch-off protection (for +12V/+5V/+3.3V) |
| Over current (max.) | Latch-off protection (for +12V/+5V/+3.3V) |
| Short circuit at O/P | Latch-off protection (for +12V/+5V/+3.3V) |
| Over temperature | Latch-off protection |

**Others**

| Parameter | Value |
|---|---|
| MTBF (min.) (note#3) | 700K hours @ rated load |

**Environment**

| Parameter | Value |
|---|---|
| Temperature (note#5) | (operating) 0~50℃ / (storage) -40~85℃ |
| Humidity | (operating) 10~90% RH non-condensing / (storage) 5~95% RH |
| Altitude (max.) | 5000 meters |

## Mechanical Specification

| Parameter | Value |
|---|---|
| Dimension | 150(L)*140(W)*86(H) mm |
| Vibration | 10~500 Hz, 5G 20min./1cycle per axis for all axes (X, Y, Z) |
| Weight (typ.) | 1250g |

**Safety**

| Parameter | Value |
|---|---|
| Standard | CB/IEC62368-1, TUV62368-1, UL62368-1, EN62368-1, CCC GB4943.1, BSMI CNS15598-1, KC62368-1 |
| Withstand voltage | Input-Output: 4242VDC / Input-FG: 2150VDC |
| Isolation resistance (min.) | Input-Output: 100Mohm @ 500VDC, 25℃, 70%RH |

**EMC**

| Parameter | Value |
|---|---|
| EN55032 (CISPR32) | Conducted EMI: class B / Radiated EMI: class B |
| FCC | Conducted EMI: class B / Radiated EMI: class B |
| EN61000-3-2 | Harmonic distortion: Class D |
| EN61000-4-2 | ESD: ±8KV contact discharge / ±15KV contact discharge |
| EN61000-4-3 | Radiated RF immunity: 3V/m |
| EN61000-4-4 | EFT: ±1KV (AC port) |
| EN61000-4-5 | Surge: ±1KV DM / ±2KV CM |
| EN61000-4-6 | Conducted RF immunity: 3V/m |
| EN61000-4-8 | Magnetic field immunity: 3A/m |
| EN61000-4-11 | Voltage dip immunity |

## Notes

1. All specification defined at 230Vac/50Hz, rated power and 25℃ ambient temperature if not mentioned specifically.
2. Ripple noise is measured with 0.1uF MLCC & 10uF low ESR capacitor.
3. Calculated by Telcordia SR332 at 25℃ ambient temperature.
4. When operating altitude is higher than 2000m, the environment temperature derating factor is 0.36℃/100m.
5. Hold up time will be evaluated at 80% of rated load.
