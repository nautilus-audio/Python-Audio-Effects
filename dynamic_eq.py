from pedalboard import Pedalboard, LowShelfFilter, PeakFilter, HighpassFilter
import numpy as np
from scipy.signal import lfilter

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

def create_dyn_eq(self, audio, low_gain, peak_cutoff_1, peak_resonance_1, peak_gain_1, peak_cutoff_2, peak_resonance_2, peak_gain_2, low_freq=400):
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
    peak_one = peaking_eq(audio, self.sample_rate, peak_cutoff_1, peak_resonance_1, peak_gain_1)
    peak_two = peaking_eq(peak_one, self.sample_rate, peak_cutoff_1, peak_resonance_1, peak_gain_1)



    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=low_freq)
    ])
    return board(peak_two, self.sample_rate)

def process(self, audio):
    # To process audio with the EQ:
    output = create_dyn_eq(self, audio, -18, 550, 2.459, -0.5, 1500, 1, -1.4, low_freq=100)

    return output