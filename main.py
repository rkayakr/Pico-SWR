"""Pi Pico SWR / Power Meter — main entry point.

Hardware
--------
- Raspberry Pi Pico running MicroPython
- Two RF detector circuits (Schottky diode + capacitor) wired to
  GPIO26 (ADC0) for forward power and GPIO27 (ADC1) for reflected power
- 128 × 64 SSD1306 OLED on I2C0 (GPIO0 = SDA, GPIO1 = SCL)

Usage
-----
Copy ``main.py``, ``swr_meter.py``, ``display.py``, and ``config.py`` to
the Pico (e.g. with Thonny or ``mpremote``).  The meter starts automatically
on power-up because MicroPython runs ``main.py`` at boot.

Calibration
-----------
With a known RF power source, adjust ``FWD_CAL_FACTOR`` and
``REF_CAL_FACTOR`` in ``config.py`` until the displayed forward power
matches the source output.
"""

import time

import config
from display import MeterDisplay
from swr_meter import SWRMeter


def main():
    """Initialise hardware and run the main measurement loop."""
    meter = SWRMeter()
    disp = MeterDisplay()

    disp.show_splash()
    time.sleep(2)

    while True:
        data = meter.get_measurements()

        if data["fwd_voltage"] < config.MIN_SIGNAL_VOLTAGE:
            disp.show_no_signal()
        else:
            disp.update(data, meter.peak_fwd_power, meter.peak_swr)

        time.sleep_ms(config.REFRESH_MS)


if __name__ == "__main__":
    main()
