from pydub import AudioSegment
import time
import numpy as np

class GV_Delay(object):
    def __init__(self, feedback=0.3, mix=0.5):
        self.vocal_delay_feedback = feedback
        self.vocal_delay_mix = mix

    def set_delay_seconds(self, tempo):
        delay_seconds=60000/(tempo / 2) #quarter note delay
        self.vecal_delay_seconds = delay_seconds


    def process(self, audio, sample_rate):
        """
        Applies a delay effect to the input audio data.

        Args:
            audio_data (numpy.ndarray): The input audio data as a NumPy array.
            delay_time_ms (int): The delay time in milliseconds.
            sample_rate (int): The sample rate of the audio data.
            feedback (float): The feedback factor (0 to 1).

        Returns:
            numpy.ndarray: The processed audio data with the delay effect.
        """
        delay_samples = int(sample_rate * (self.vecal_delay_seconds / 1000.0))
        delayed_signal = np.zeros(len(audio))

        for i in range(len(audio)):
            delayed_signal[i] = audio[i]
            if i >= delay_samples:
                delayed_signal[i] += delayed_signal[i - delay_samples] * self.vocal_delay_feedback
        # Mix
        output = ((audio * (1 - self.vocal_delay_mix)) + (delayed_signal * self.vocal_delay_mix))

        return output

