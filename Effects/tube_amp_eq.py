
# low_eq_signal = self.low_pass_filter(audio_signal, self.low_freq, self.low_boost, self.low_cut)
# high_eq_signal = self.high_pass_filter(low_eq_signal, self.high_freq, self.high_boost, self.high_cut

import numpy as np
import scipy.signal as sig
import librosa
import soundfile as sf
from scipy.signal import butter, sosfilt

class PultecEQP1A:
    def __init__(self, sample_rate, low_freq, low_q, low_boost, low_cut, high_freq, high_q, high_boost, high_cut):
        self.sample_rate = sample_rate
        
        # Frequencies, Q, and Boost/Cut settings
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.low_q = low_q
        self.high_q = high_q
        self.low_boost = low_boost
        self.low_cut = low_cut
        self.high_boost = high_boost
        self.high_cut = high_cut

    def pultec_low_shelf_filter(self, signal, sample_rate, cutoff_freq, boost_db, cut_db, order=4):
        """
        Apply a Pultec-style low-shelf filter with both boost and cut to the signal.

        :param signal: The input audio signal (1D numpy array).
        :param sample_rate: The sample rate of the audio signal (e.g., 44100 Hz).
        :param cutoff_freq: The cutoff frequency for the low-shelf filter (in Hz).
        :param boost_db: The boost gain applied to frequencies below the cutoff (in dB).
        :param cut_db: The cut gain applied to frequencies below the cutoff (in dB).
        :param order: The order of the filter (higher values lead to sharper transitions).
        :return: The filtered audio signal.
        """

        # Convert boost and cut gains from dB to linear scale
        boost_gain = 10**(boost_db / 20.0)
        cut_gain = 10**(cut_db / 20.0)
        
        # Design a low-shelf filter using a parametric EQ style (using a second-order filter section)
        nyquist = 0.5 * sample_rate
        cutoff_norm = cutoff_freq / nyquist
        
        # We create a low-shelf filter with boost applied to the lower frequencies
        sos = butter(order, cutoff_norm, btype='low', analog=False, output='sos')

        # Apply the low-shelf filter to the signal
        filtered_signal = sosfilt(sos, signal)
        
        # Boost or cut the signal based on the frequencies below the cutoff
        signal_below_cutoff = np.where(signal <= cutoff_freq, filtered_signal * boost_gain, signal)
        signal_above_cutoff = np.where(signal > cutoff_freq, filtered_signal * cut_gain, signal)
        
        # Combine the results from the boosted and cut signals
        final_signal = signal_below_cutoff + signal_above_cutoff

        return final_signal

    def pultec_high_shelf_filter(self, signal, sample_rate, cutoff_freq, boost_db, cut_db, order=4):
        """
        Apply a Pultec-style high-shelf filter with both boost and cut to the signal.

        :param signal: The input audio signal (1D numpy array).
        :param sample_rate: The sample rate of the audio signal (e.g., 44100 Hz).
        :param cutoff_freq: The cutoff frequency for the high-shelf filter (in Hz).
        :param boost_db: The boost gain applied to frequencies above the cutoff (in dB).
        :param cut_db: The cut gain applied to frequencies above the cutoff (in dB).
        :param order: The order of the filter (higher values lead to sharper transitions).
        :return: The filtered audio signal.
        """

        # Convert boost and cut gains from dB to linear scale
        boost_gain = 10**(boost_db / 20.0)
        cut_gain = 10**(cut_db / 20.0)
        
        # Design a high-shelf filter using a parametric EQ style (using a second-order filter section)
        nyquist = 0.5 * sample_rate
        cutoff_norm = cutoff_freq / nyquist
        
        # We create a high-shelf filter with boost applied to the higher frequencies
        # Using butterworth filter as a foundation for smoother transitions
        sos = butter(order, cutoff_norm, btype='high', analog=False, output='sos')

        # Apply the high-shelf filter to the signal
        filtered_signal = sosfilt(sos, signal)
        
        # Boost or cut the signal based on the frequencies above the cutoff
        # Here we're boosting or cutting in a more selective way
        signal_above_cutoff = np.where(signal > cutoff_freq, filtered_signal * boost_gain, signal)
        signal_below_cutoff = np.where(signal <= cutoff_freq, filtered_signal * cut_gain, signal)
        
        # Combine the results from the boosted and cut signals
        final_signal = signal_above_cutoff + signal_below_cutoff

        return final_signal

        
    def tube_distortion(self, signal, drive=0.5):
        """Apply tube-style distortion (soft clipping) to the signal"""
        return np.tanh(signal * drive)

    def apply_eq(self, audio_signal):
        """Apply the full EQ (low and high shelf) to the audio signal"""
        # Apply Low Shelf (Boost / Cut)
        low_eq_signal = self.pultec_low_shelf_filter(audio_signal, self.sample_rate, self.low_freq, self.low_boost, self.low_cut, 4)

        # Apply High Shelf (Boost / Cut)
        high_eq_signal = self.pultec_high_shelf_filter(low_eq_signal, self.sample_rate, self.high_freq, self.high_boost, self.high_cut, 4)
        
        return high_eq_signal

    def process(self, audio):
        """Apply EQ and distortion to the input audio"""
        eq_signal = self.apply_eq(audio)  # Apply EQ
        
        # Normalize the signal before applying distortion (to avoid too much clipping)
        eq_signal = np.clip(eq_signal, -1.0, 1.0)  # Clipping if necessary to prevent excessive values

        # Apply distortion
        processed_audio = self.tube_distortion(eq_signal, drive=0.2)  # Apply distortion
        
        return processed_audio

# Example usage:

if __name__ == "__main__":
    # Load an audio file
    audio_file = 'Audio/Input/M_T2.wav'  # Replace with your file path
    y, sr = librosa.load(audio_file, sr=None)

    # Create an instance of the Pultec EQ
    pultec_eq = PultecEQP1A(
        sample_rate=sr,
        low_freq=100, low_q=0.5, low_boost=6, low_cut=-3,  # Low shelf settings
        high_freq=8000, high_q=0.5, high_boost=3, high_cut=-3  # High shelf settings
    )

    # Process the audio signal
    processed_audio = pultec_eq.process(y)

    # Save the processed audio to a file
    output_file = 'output_audio.wav'
    sf.write(output_file, processed_audio, sr)
    print(f"Processed audio saved to {output_file}")




# # Example usage
# if __name__ == "__main__":
#     # Load an audio file (replace 'audio_file.wav' with your own file path)
#     audio_file = 'audio_file.wav'  # Path to your audio file
#     audio_data, sr = librosa.load(audio_file, sr=None)

#     # Initialize PultecEQP1A with sample rate and frequency settings
#     pultec_eq = PultecEQP1A(
#         sample_rate=sr,
#         low_freq=60.0,   # Low frequency (in Hz)
#         low_q=0.7,       # Low Q
#         low_boost=6.0,   # Low boost (in dB)
#         low_cut=-3.0,    # Low cut (in dB)
#         high_freq=8000.0,  # High frequency (in Hz)
#         high_q=0.7,       # High Q
#         high_boost=3.0,  # High boost (in dB)
#         high_cut=-2.0    # High cut (in dB)
#     )

#     # Process the audio through the Pultec EQP1A
#     processed_audio = pultec_eq.process(audio_data)

#     # Save the processed audio
#     sf.write('processed_audio.wav', processed_audio, sr)

#     print("Processing complete. Output saved as 'processed_audio.wav'")
