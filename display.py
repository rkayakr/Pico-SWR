"""SSD1306 OLED display management for the Pi Pico SWR/Power Meter.

Display layout  (128 × 64 pixels, 8-pixel character height → 8 text rows)
--------------------------------------------------------------------------
Row 0  y=0   "FWD: xxx.xW"         forward power
Row 1  y=8   "REF:   xx.xW"        reflected power
Row 2  y=16  "SWR:x.xx  GOOD"      SWR + quality label
Row 3  y=24  "NET:  xxx.xW"        net / delivered power
Row 4  y=32  "RL:  xx.x dB"        return loss
Row 5  y=40  "PK: xxx.xW S:x.xx"  peak forward power + peak SWR
Row 6  y=48  ─── separator line ───
Row 7  y=56  [=== bar graph ===]   forward-power bar graph

All 16 character columns (128 / 8) are used where needed.
"""

from machine import Pin, I2C
import ssd1306

import config


class MeterDisplay:
    """Manage the SSD1306 OLED display for the SWR/power meter.

    Parameters
    ----------
    None – pin and I2C configuration is read from ``config``.
    """

    # Bar-graph geometry (pixels)
    _BAR_X = 0
    _BAR_Y = 56
    _BAR_W = 128
    _BAR_H = 8

    def __init__(self):
        i2c = I2C(
            config.I2C_ID,
            sda=Pin(config.I2C_SDA_PIN),
            scl=Pin(config.I2C_SCL_PIN),
            freq=config.I2C_FREQ,
        )
        self._oled = ssd1306.SSD1306_I2C(
            config.DISPLAY_WIDTH,
            config.DISPLAY_HEIGHT,
            i2c,
            addr=config.DISPLAY_I2C_ADDR,
        )

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fmt_power(watts):
        """Format a power value to a compact string with units.

        Examples::

            0.005  →  "5mW"
            0.5    →  "500mW"
            1.2    →  "1.20W"
            12.3   →  "12.3W"
            100.0  →  "100W"
        """
        if watts >= 100.0:
            return "{:.0f}W".format(watts)
        if watts >= 10.0:
            return "{:.1f}W".format(watts)
        if watts >= 1.0:
            return "{:.2f}W".format(watts)
        if watts >= 0.001:
            return "{:.0f}mW".format(watts * 1000)
        return "0W"

    @staticmethod
    def _fmt_swr(swr):
        """Format SWR to a compact string."""
        if swr >= 10.0:
            return "{:.1f}".format(swr)
        return "{:.2f}".format(swr)

    @staticmethod
    def _swr_quality(swr):
        """Return a 4-character quality label for the given SWR."""
        if swr <= 1.5:
            return "GOOD"
        if swr <= 2.0:
            return "FAIR"
        if swr <= 3.0:
            return "POOR"
        return "BAD!"

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_bar(self, value, max_value):
        """Draw a filled horizontal bar graph.

        Parameters
        ----------
        value : float
            Current value to represent.
        max_value : float
            Value that corresponds to a full bar.
        """
        oled = self._oled
        x, y, w, h = self._BAR_X, self._BAR_Y, self._BAR_W, self._BAR_H

        # Outer border
        oled.rect(x, y, w, h, 1)

        # Inner fill (leave 1-pixel border on each side)
        if max_value > 0:
            fill_w = int((w - 2) * min(value / max_value, 1.0))
        else:
            fill_w = 0

        if fill_w > 0:
            oled.fill_rect(x + 1, y + 1, fill_w, h - 2, 1)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def show_splash(self):
        """Display a startup splash screen."""
        oled = self._oled
        oled.fill(0)
        # Centre titles (128 px wide, 8 px per char → 16 cols)
        oled.text("Pi Pico SWR Meter", 0, 0, 1)
        oled.text("  Power & SWR", 0, 16, 1)
        oled.text("   Meter v1.0", 0, 28, 1)
        oled.text(" Initializing...", 0, 48, 1)
        oled.show()

    def show_no_signal(self):
        """Display a minimal screen when no RF signal is detected."""
        oled = self._oled
        oled.fill(0)
        oled.text("Pi Pico SWR", 16, 0, 1)
        oled.text("  Meter", 16, 10, 1)
        oled.text("-- No Signal --", 8, 28, 1)
        oled.text("SWR:  1.00", 16, 44, 1)
        oled.text("PWR:   0W", 16, 54, 1)
        oled.show()

    def update(self, measurements, peak_fwd_power=0.0, peak_swr=1.0):
        """Refresh the display with the latest measurement data.

        Parameters
        ----------
        measurements : dict
            Dict returned by ``SWRMeter.get_measurements()``.
        peak_fwd_power : float
            Peak forward power value for the peak-hold row.
        peak_swr : float
            Peak SWR value for the peak-hold row.
        """
        oled = self._oled

        fwd_w = measurements["fwd_power_w"]
        ref_w = measurements["ref_power_w"]
        net_w = measurements["net_power_w"]
        swr = measurements["swr"]
        rl_db = measurements["return_loss_db"]

        oled.fill(0)

        # Row 0 (y=0): forward power
        oled.text("FWD:" + self._fmt_power(fwd_w), 0, 0, 1)

        # Row 1 (y=8): reflected power
        oled.text("REF:" + self._fmt_power(ref_w), 0, 8, 1)

        # Row 2 (y=16): SWR + quality indicator
        swr_str = "SWR:" + self._fmt_swr(swr)
        quality = self._swr_quality(swr)
        # Right-align quality label (each char = 8 px → col 12 = x=96)
        oled.text(swr_str, 0, 16, 1)
        oled.text(quality, 96, 16, 1)

        # Row 3 (y=24): net power
        oled.text("NET:" + self._fmt_power(net_w), 0, 24, 1)

        # Row 4 (y=32): return loss
        if rl_db >= 99.0:
            rl_str = "RL: -.-- dB"
        else:
            rl_str = "RL:{:5.1f} dB".format(rl_db)
        oled.text(rl_str, 0, 32, 1)

        # Row 5 (y=40): peak hold values
        pk_str = "PK:" + self._fmt_power(peak_fwd_power)
        pk_swr = " S:" + self._fmt_swr(peak_swr)
        oled.text(pk_str, 0, 40, 1)
        oled.text(pk_swr, 72, 40, 1)

        # Row 6 (y=48): separator line
        oled.hline(0, 48, 128, 1)

        # Row 7 (y=56): forward-power bar graph
        self._draw_bar(fwd_w, config.MAX_DISPLAY_POWER_W)

        oled.show()
