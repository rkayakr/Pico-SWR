# Pico-SWR

MicroPython code for a Raspberry Pi Pico RF power and SWR meter.

Measures forward power, reflected power, net power, SWR, and return
loss using two Schottky-diode detector circuits, and displays the
results on a 128 × 64 SSD1306 OLED screen.

---

## Features

- Forward, reflected, and net power display (mW → W range)
- SWR (Standing Wave Ratio) with Good / Fair / Poor / Bad quality label
- Return loss in dB
- Forward-power bar graph
- Peak-hold for forward power and SWR (configurable hold time)
- "No Signal" idle screen when no RF is detected
- Adjustable calibration factors in `config.py`

---

## Hardware

### Components

| Item | Notes |
|------|-------|
| Raspberry Pi Pico | Any Pico or Pico W |
| SSD1306 OLED 128 × 64 | I2C version |
| RF directional coupler | e.g. home-brew toroid bridge |
| 2 × Schottky detector circuits | e.g. 1N5711 or BAT43 diode + 100 nF + 10 kΩ |

### Wiring

```
Pico GPIO26 (ADC0) ─── Forward power detector output
Pico GPIO27 (ADC1) ─── Reflected power detector output
Pico GPIO0  (SDA)  ─── OLED SDA
Pico GPIO1  (SCL)  ─── OLED SCL
Pico 3V3           ─── OLED VCC + detector supply
Pico GND           ─── OLED GND + detector GND
```

A typical Schottky detector circuit for each port:

```
RF in ──┬── Schottky diode (anode→) ──┬── 10 kΩ ── GND
        │                              │
       GND                           100 nF         ADC pin
                                       │
                                      GND
```

The DC voltage at the ADC pin is proportional to the RF peak voltage.

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main program loop |
| `swr_meter.py` | ADC reading + SWR / power calculations |
| `display.py` | SSD1306 display management |
| `config.py` | Pin assignments, calibration, tuning constants |

---

## Installation

1. Flash MicroPython onto your Pico (download from
   [micropython.org](https://micropython.org/download/rp2-pico/)).
2. Copy all four `.py` files to the root of the Pico filesystem using
   Thonny, `mpremote`, or `rshell`.
3. The meter starts automatically on power-up (`main.py` is the
   MicroPython entry point).

---

## Calibration

1. Connect a transmitter set to a known power level (e.g. 5 W).
2. Note the "FWD" reading on the display.
3. Adjust `FWD_CAL_FACTOR` in `config.py` until the display matches the
   known power.  If the display reads *too low*, increase the factor; if
   it reads *too high*, decrease it.
4. Repeat for the reflected channel using a known dummy-load mismatch and
   adjust `REF_CAL_FACTOR`.

Other tuning knobs in `config.py`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `MAX_DISPLAY_POWER_W` | 100 | Full-scale for bar graph |
| `PEAK_HOLD_SECONDS` | 3 | Peak-hold reset time |
| `REFRESH_MS` | 200 | Display update interval |
| `MIN_SIGNAL_VOLTAGE` | 0.05 V | Noise-floor threshold |
| `ADC_SAMPLES` | 16 | ADC averaging samples |

---

## Display Layout

```
┌────────────────┐
│FWD:12.3W       │  ← forward power
│REF: 0.50W      │  ← reflected power
│SWR:1.23  GOOD  │  ← SWR + quality
│NET:11.8W       │  ← net / delivered power
│RL:  19.1 dB    │  ← return loss
│PK: 12.3W S:1.23│  ← peak hold values
│────────────────│
│[██████░░░░░░░░]│  ← forward power bar graph
└────────────────┘
```

SWR quality labels:

| SWR range | Label |
|-----------|-------|
| 1.0 – 1.5 | GOOD |
| 1.5 – 2.0 | FAIR |
| 2.0 – 3.0 | POOR |
| > 3.0     | BAD! |

---

## License

See [LICENSE](LICENSE).
