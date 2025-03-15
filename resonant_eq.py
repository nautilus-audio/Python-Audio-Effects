import numpy as np
from scipy.signal import lfilter

class ResonantEQ:
    def __init__(self, sample_rate, attack_time, release_time, depth=1.0):
        self.sample_rate = sample_rate
        
        # Default EQ settings
        self.peak_1_freq = 100
        self.peak_1_gain = 6
        self.peak_1_q = 1
        self.peak_2_freq = 500
        self.peak_2_gain = 6
        self.peak_2_q = 1
        self.low_freq = 50
        self.high_freq = 15000
        self.low_gain_db = 0
        self.mid_gain_db = 0
        self.high_gain_db = 0
        self.res_eq_attack_time = attack_time
        self.res_eq_release_time = release_time
        self.res_eq_depth = depth  # Depth controls the intensity of the EQ effect

        
        # Calculate attack and release coefficients
        self.attack_coeff = np.exp(-1 / (self.res_eq_attack_time * self.sample_rate))
        self.release_coeff = np.exp(-1 / (self.res_eq_release_time * self.sample_rate))
        
        # Initialize previous gain values (start with no gain change)
        self.previous_gain_1 = self.peak_1_gain
        self.previous_gain_2 = self.peak_2_gain

    def set_peak_values(self, peak_1_freq, peak_1_gain, peak_1_q, peak_2_freq, peak_2_gain, peak_2_q):
        self.peak_1_freq = peak_1_freq
        self.peak_1_gain = peak_1_gain
        self.peak_1_q = peak_1_q
        self.peak_2_freq = peak_2_freq
        self.peak_2_gain = peak_2_gain
        self.peak_2_q = peak_2_q

    def set_filter_values(self, low_freq, high_freq, low_gain_db, mid_gain_db, high_gain_db):
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.low_gain_db = low_gain_db
        self.mid_gain_db = mid_gain_db
        self.high_gain_db = high_gain_db

    @staticmethod
    def peaking_eq(self, audio, sample_rate, center_freq, q_factor, gain_db, attack_coeff, release_coeff, previous_gain):
        """
        Applies a true peaking EQ filter, with attack and release smoothing on the gain.
        
        Args:
            audio (numpy.ndarray): Input audio signal.
            sample_rate (int): Sample rate of the audio.
            center_freq (float): Frequency to boost (Hz).
            q_factor (float): Quality factor (higher = narrower peak).
            gain_db (float): Gain boost in dB.
            attack_coeff (float): Attack smoothing coefficient.
            release_coeff (float): Release smoothing coefficient.
            previous_gain (float): Previous gain value for smoothing.

        Returns:
            numpy.ndarray: Filtered audio signal.
            float: New gain value for future processing.
        """
        effective_gain_db = gain_db * self.res_eq_depth

        A = 10**(gain_db / 40)  # Amplitude from dB gain
        omega = 2 * np.pi * center_freq / sample_rate
        alpha = np.sin(omega) / (2 * q_factor)

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

        # Update the gain based on the attack or release times
        if gain_db > previous_gain:
            # Attack phase: gain increases
            new_gain = attack_coeff * previous_gain + (1 - attack_coeff) * gain_db
        else:
            # Release phase: gain decreases
            new_gain = release_coeff * previous_gain + (1 - release_coeff) * gain_db

        return filtered_audio, new_gain

    def process(self, audio):
        """Processes the audio with EQ and peaks, applying attack and release smoothing."""
        # Apply the first peaking EQ filter with attack/release smoothing
        peak_one, new_gain_1 = self.peaking_eq(self, audio, self.sample_rate, self.peak_1_freq, self.peak_1_q, self.peak_1_gain, 
                                               self.attack_coeff, self.release_coeff, self.previous_gain_1)
        
        # Apply the second peaking EQ filter with attack/release smoothing
        peak_two, new_gain_2 = self.peaking_eq(self, peak_one, self.sample_rate, self.peak_2_freq, self.peak_2_q, self.peak_2_gain, 
                                               self.attack_coeff, self.release_coeff, new_gain_1)

        # Update the previous gain values for the next process call
        self.previous_gain_1 = new_gain_1
        self.previous_gain_2 = new_gain_2

        return peak_two

    
            # # Apply band EQ using Pedalboard
        # board = Pedalboard([
        #     HighpassFilter(cutoff_frequency_hz=self.low_freq),
        #     Gain(gain_db=self.low_gain_db),
        #     LowpassFilter(cutoff_frequency_hz=self.high_freq),
        #     Gain(gain_db=self.high_gain_db),
        # ])


# --- Offline Processing ---
# if __name__ == "__main__":
#     # Load an audio file
#     audio, sample_rate = sf.read("audio_file.wav")

#     # Ensure mono for processing
#     if len(audio.shape) > 1:
#         audio = audio[:, 0]  

#     # Create EQ instance
#     eq = ResonantEQ(sample_rate)
#     eq.set_peak_values(200, 6, 1, 1000, 6, 1)
#     eq.set_filter_values(50, 15000, 0, 3, -3)

#     # Process audio
#     processed_audio = eq.process(audio)

#     # Save output
#     sf.write("processed_audio.wav", processed_audio, sample_rate)
#     print("Processed audio saved as 'processed_audio.wav'")
