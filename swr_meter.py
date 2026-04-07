"""SWR and power measurement for the Pi Pico SWR/Power Meter.

This module reads two ADC channels (forward and reflected detector voltages)
and computes:

  - Forward power  (watts)
  - Reflected power (watts)
  - Net / delivered power (watts)
  - SWR (Standing Wave Ratio)
  - Return Loss (dB)

Calculation chain
-----------------
1. ADC raw value  →  voltage (V)           via  V = raw × VREF / ADC_MAX
2. voltage        →  calibrated voltage    via  V_cal = V × CAL_FACTOR
3. calibrated V   →  power (W)            via  P = V_cal² / Z0
4. forward V + reflected V  →  SWR        via  SWR = (Vf + Vr) / (Vf − Vr)
5. forward V + reflected V  →  return loss via  RL = −20 log10(Vr / Vf)

The square-law relationship P = V²/Z0 assumes the detector output voltage is
linearly proportional to the RF peak voltage, which is a good approximation
for Schottky-diode detectors at moderate power levels.  The calibration
factors absorb any deviation from ideal behaviour.
"""

import machine
import math
import time

import config


class SWRMeter:
    """Read forward/reflected detector voltages and compute RF metrics.

    Attributes
    ----------
    peak_fwd_power : float
        Highest forward power (W) seen during the current peak-hold window.
    peak_swr : float
        Highest SWR seen during the current peak-hold window.
    """

    # Clamp SWR to this value when reflected power ≈ forward power
    SWR_MAX = 99.9

    def __init__(self):
        self._adc_fwd = machine.ADC(config.ADC_FORWARD_PIN)
        self._adc_ref = machine.ADC(config.ADC_REFLECTED_PIN)

        # Peak-hold state
        self.peak_fwd_power = 0.0
        self.peak_swr = 1.0
        self._peak_reset_time = time.time()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _adc_to_voltage(self, adc_obj):
        """Return the averaged ADC voltage (V) from multiple samples.

        Averaging ADC_SAMPLES readings reduces the effect of ADC noise and
        any ripple on the detector output.
        """
        total = 0
        for _ in range(config.ADC_SAMPLES):
            total += adc_obj.read_u16()
        return (total / config.ADC_SAMPLES) * config.ADC_VREF / config.ADC_MAX

    @staticmethod
    def _voltage_to_power(voltage_v, cal_factor):
        """Convert a detector DC voltage (V) to RF power (W).

        Uses the square-law approximation:  P = (V × cal)² / Z0
        """
        v_cal = voltage_v * cal_factor
        return (v_cal * v_cal) / config.Z0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read_voltages(self):
        """Return ``(fwd_voltage_V, ref_voltage_V)`` from the ADC channels."""
        vf = self._adc_to_voltage(self._adc_fwd)
        vr = self._adc_to_voltage(self._adc_ref)
        return vf, vr

    def calculate_swr(self, fwd_voltage, ref_voltage):
        """Calculate SWR from forward and reflected detector voltages.

        SWR = (Vf + Vr) / (Vf − Vr)

        Returns
        -------
        float
            SWR ≥ 1.0.  Returns 1.0 when there is no forward signal.
            Returns SWR_MAX when reflected voltage equals or exceeds forward.
        """
        if fwd_voltage <= config.MIN_SIGNAL_VOLTAGE:
            return 1.0  # No signal — report perfect match

        # Reflection coefficient Γ = Vr / Vf, clamped to [0, 1]
        gamma = min(ref_voltage / fwd_voltage, 1.0)
        if gamma >= 1.0:
            return self.SWR_MAX

        swr = (1.0 + gamma) / (1.0 - gamma)
        return min(swr, self.SWR_MAX)

    @staticmethod
    def calculate_return_loss(fwd_voltage, ref_voltage):
        """Calculate return loss in dB (positive value means loss).

        RL = −20 × log10(Vr / Vf)

        Returns 0.0 when there is no forward signal, and 99.9 when there
        is no reflected signal (ideal match).
        """
        if fwd_voltage <= config.MIN_SIGNAL_VOLTAGE:
            return 0.0
        if ref_voltage <= 0.0:
            return 99.9

        gamma = min(ref_voltage / fwd_voltage, 1.0)
        if gamma <= 0.0:
            return 99.9
        return -20.0 * math.log10(gamma)

    def get_measurements(self):
        """Perform one complete measurement cycle and return all metrics.

        Also updates the internal peak-hold values (``peak_fwd_power`` and
        ``peak_swr``), resetting them after ``PEAK_HOLD_SECONDS`` with no
        new peak.

        Returns
        -------
        dict
            fwd_power_w    : forward power in watts
            ref_power_w    : reflected power in watts
            net_power_w    : net (delivered) power in watts  (fwd − ref)
            swr            : Standing Wave Ratio (1.0 = perfect match)
            return_loss_db : return loss in dB (positive number)
            fwd_voltage    : raw forward detector voltage (V)
            ref_voltage    : raw reflected detector voltage (V)
        """
        vf, vr = self.read_voltages()

        fwd_power = self._voltage_to_power(vf, config.FWD_CAL_FACTOR)
        ref_power = self._voltage_to_power(vr, config.REF_CAL_FACTOR)
        net_power = max(fwd_power - ref_power, 0.0)

        swr = self.calculate_swr(vf, vr)
        rl_db = self.calculate_return_loss(vf, vr)

        # --- Peak-hold logic ---
        now = time.time()
        if now - self._peak_reset_time >= config.PEAK_HOLD_SECONDS:
            # Hold window expired — reset peaks to current values
            self.peak_fwd_power = fwd_power
            self.peak_swr = swr
            self._peak_reset_time = now
        else:
            if fwd_power > self.peak_fwd_power:
                self.peak_fwd_power = fwd_power
            if swr > self.peak_swr and vf > config.MIN_SIGNAL_VOLTAGE:
                self.peak_swr = swr

        return {
            "fwd_power_w": fwd_power,
            "ref_power_w": ref_power,
            "net_power_w": net_power,
            "swr": swr,
            "return_loss_db": rl_db,
            "fwd_voltage": vf,
            "ref_voltage": vr,
        }
