from pedalboard import Pedalboard, LowShelfFilter, PeakFilter, HighShelfFilter
from scipy.signal import lfilter
import numpy as np

def peaking_eq(audio, sample_rate, center_freq, q_factor, gain_db):
    """
    Applies a true peaking EQ filter without dulling high frequencies.

    Args:
        audio (numpy.ndarray): Input audio signal.
        sample_rate (int): Sample rate of the audio.
        center_freq (float): Frequency to boost (Hz).
        q_factor (float): Quality factor (higher = narrower peak).
        gain_db (float): Gain boost in dB.

    Returns:
        numpy.ndarray: Filtered audio signal.
    """
    A = 10**(gain_db / 40)  # Amplitude from dB gain
    omega = 2 * np.pi * center_freq / sample_rate
    alpha = np.sin(omega) / (2 * q_factor)

    # Biquad peaking EQ coefficients
    b0 = 1 + alpha * A
    b1 = -2 * np.cos(omega)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(omega)
    a2 = 1 - alpha / A

    # Normalize coefficients
    b = [b0 / a0, b1 / a0, b2 / a0]
    a = [1, a1 / a0, a2 / a0]

    # Apply filter
    filtered_audio = lfilter(b, a, audio)
    return filtered_audio


def create_3band_eq(audio, sample_rate, low_gain, peak_gain, high_gain, peak_cutoff, peak_resonance, low_freq=400, high_freq=2500):
    """
    Creates a 3-band EQ pedalboard.

    Args:
        low_gain (float): Gain for the low shelf filter in dB.
        mid_gain (float): Gain for the peak filter in dB.
        high_gain (float): Gain for the high shelf filter in dB.
        low_freq (float): Cutoff frequency for the low shelf filter in Hz.
        high_freq (float): Cutoff frequency for the high shelf filter in Hz.

    Returns:
        Pedalboard: A Pedalboard object containing the 3-band EQ.
    """
    peak = peaking_eq(audio, sample_rate, peak_cutoff, peak_resonance, peak_gain)

    board = Pedalboard([
        LowShelfFilter(gain_db=low_gain, cutoff_frequency_hz=low_freq),
        PeakFilter(peak_cutoff, peak_gain, peak_resonance), # Q value for a natural-sounding filter
        HighShelfFilter(gain_db=high_gain, cutoff_frequency_hz=high_freq)
    ])
    return board(peak, sample_rate)

def process(audio, sample_rate):
    eq = create_3band_eq(audio, sample_rate, low_gain=-3.0, mid_gain=-2.0, high_gain=5.0)

    # To process audio with the EQ:
    processed_audio = eq(audio, sample_rate)
    return processed_audio