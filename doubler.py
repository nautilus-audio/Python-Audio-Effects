import pedalboard as pd
import numpy as np
import librosa

class Doubler(object):
    def __init__(self, delay_ms=20, detune_cents=5, mix=0.5):
        self.delay_ms = delay_ms
        self.detune_cents = detune_cents
        self.mix = mix


    def process(audio, sample_rate, delay_ms=20, detune_cents=5, mix=0.3):
        """
        Applies a doubler effect to an audio signal.
        
        Parameters:
        - audio: np.array, input mono audio signal.
        - sample_rate: int, sample rate of the audio.
        - delay_ms: int, delay in milliseconds for doubling.
        - detune_cents: float, pitch shift in cents.
        - mix: float, blend between original (0) and doubled (1) signal.
        
        Returns:
        - np.array, audio with doubler effect applied.
        """
        # Convert delay from ms to samples
        delay_samples = int((delay_ms / 1000) * sample_rate)

        # Create a delayed version of the signal (zero-padding at the start)
        delayed_audio = np.pad(audio, (delay_samples, 0), mode='constant')[:len(audio)]

        # Apply slight pitch shift
        detune_factor = 2 ** (detune_cents / 1200)  # Convert cents to pitch factor
        shifted_audio = librosa.effects.pitch_shift(delayed_audio, sr=sample_rate, n_steps=detune_factor)

        # Mix the original and processed signal
        output = (1 - mix) * audio + mix * shifted_audio

        # Normalize to prevent clipping
        output = np.clip(output, -1.0, 1.0)

        return output
