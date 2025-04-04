import numpy as np
from scipy.signal import butter, sosfilt

class DeEsser:
    def __init__(self, sample_rate, sibilance_freq_low=5000, sibilance_freq_high=12000, threshold=-30, reduction_db=6, range_db=10):
        """
        Initialize the De-Esser with added range parameter.
        
        :param sample_rate: Sampling rate of the audio.
        :param sibilance_freq_low: Lower bound of sibilance frequencies (in Hz).
        :param sibilance_freq_high: Upper bound of sibilance frequencies (in Hz).
        :param threshold: Sibilance reduction threshold in dB.
        :param reduction_db: Maximum reduction amount in dB.
        :param range_db: Dynamic range of sibilance reduction in dB.
        """
        self.sample_rate = sample_rate
        self.sibilance_freq_low = sibilance_freq_low
        self.sibilance_freq_high = sibilance_freq_high
        self.threshold = threshold
        self.reduction_db = reduction_db
        self.range_db = range_db  # The range of reduction in dB

    def _butter_bandpass(self, lowcut, highcut, fs, order=4):
        """Create a bandpass filter to isolate sibilance frequencies."""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], btype='bandpass', analog=False, output='sos')
        return sos

    def process(self, audio):
        """
        Apply the de-esser effect to the audio with dynamic range control.
        
        :param audio: NumPy array of audio samples.
        :return: De-essed audio.
        """
        # Extract sibilance frequencies using bandpass filter
        sos = self._butter_bandpass(self.sibilance_freq_low, self.sibilance_freq_high, self.sample_rate)
        sibilance = sosfilt(sos, audio)

        # Compute the RMS energy of sibilance
        rms_sibilance = np.sqrt(np.mean(sibilance**2))
        sibilance_db = 20 * np.log10(rms_sibilance + 1e-10)  # Avoid log(0)

        # Compute dynamic gain reduction (soft-knee compression with range parameter)
        if sibilance_db > self.threshold:
            # Calculate the dynamic reduction based on range
            excess_db = sibilance_db - self.threshold
            if excess_db < self.range_db:
                # Linear reduction within the range
                reduction_ratio = (excess_db / self.range_db) * (self.reduction_db / 20)
            else:
                # Full reduction when above the range
                reduction_ratio = self.reduction_db / 20
        else:
            reduction_ratio = 0  # No reduction if under threshold

        # Apply gain reduction smoothly to only the sibilance frequencies
        gain = 1.0 - reduction_ratio

        # Smoothly mix the processed sibilance back with the original audio
        processed_sibilance = sibilance * gain
        processed_audio = audio + processed_sibilance

        # Normalize to prevent clipping
        processed_audio = np.clip(processed_audio, -1.0, 1.0)

        return processed_audio



