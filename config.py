"""Configuration constants for the Pi Pico SWR/Power Meter.

Hardware connections
--------------------
GPIO26 (ADC0) : Forward power detector DC output
GPIO27 (ADC1) : Reflected power detector DC output
GPIO0  (SDA)  : I2C data  – SSD1306 OLED display
GPIO1  (SCL)  : I2C clock – SSD1306 OLED display

The detector circuits (Schottky diode + filter capacitor + load resistor)
convert RF voltage to a proportional DC voltage that is read by the ADC.
Adjust FWD_CAL_FACTOR and REF_CAL_FACTOR against a calibrated power source
to get accurate watt readings.
"""

# ---------------------------------------------------------------------------
# ADC pin assignments
# ---------------------------------------------------------------------------
ADC_FORWARD_PIN = 26    # GPIO26 = ADC0 — forward power detector
ADC_REFLECTED_PIN = 27  # GPIO27 = ADC1 — reflected power detector

# Number of ADC samples averaged per reading (reduces noise)
ADC_SAMPLES = 16

# ---------------------------------------------------------------------------
# I2C / display settings  (SSD1306 OLED 128 × 64)
# ---------------------------------------------------------------------------
I2C_ID = 0              # I2C peripheral (0 = I2C0)
I2C_SDA_PIN = 0         # GPIO0
I2C_SCL_PIN = 1         # GPIO1
I2C_FREQ = 400_000      # 400 kHz fast-mode
DISPLAY_I2C_ADDR = 0x3C # Default SSD1306 I2C address
DISPLAY_WIDTH = 128     # Pixels
DISPLAY_HEIGHT = 64     # Pixels

# ---------------------------------------------------------------------------
# RF / measurement constants
# ---------------------------------------------------------------------------
Z0 = 50.0               # System impedance in ohms (standard 50 Ω coax)

# Full-scale forward power for the bar-graph display (watts)
MAX_DISPLAY_POWER_W = 100.0

# ---------------------------------------------------------------------------
# ADC / calibration constants
# ---------------------------------------------------------------------------
ADC_VREF = 3.3          # ADC reference voltage (volts)
ADC_MAX = 65535         # Maximum value from read_u16() (2**16 − 1)

# Calibration multipliers applied to the measured detector voltages.
# Increase a factor to read *higher* power; decrease to read *lower* power.
# Procedure: apply a known power level, then adjust until display matches.
FWD_CAL_FACTOR = 1.0    # Forward channel calibration multiplier
REF_CAL_FACTOR = 1.0    # Reflected channel calibration multiplier

# Minimum detector voltage (V) treated as a valid RF signal.
# Readings below this threshold are considered "no signal" (noise floor).
MIN_SIGNAL_VOLTAGE = 0.05

# ---------------------------------------------------------------------------
# Update / display rate
# ---------------------------------------------------------------------------
REFRESH_MS = 200        # Main-loop delay in milliseconds (≈ 5 Hz)

# Peak-hold duration: the peak SWR/power is held for this many seconds after
# the last new peak before it resets to the current live reading.
PEAK_HOLD_SECONDS = 3
