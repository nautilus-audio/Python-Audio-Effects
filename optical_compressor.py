import numpy as np

class OpticalCompressor:
    def __init__(self, sample_rate, attack_time=0.005, release_time=0.2, threshold=-12, ratio=4, makeup_gain=True, make_up_gain=3):
        self.attack_time = attack_time
        self.release_time = release_time
        self.comp_threshold = 10**(threshold / 20)  # Convert threshold to linear scale
        self.comp_ratio = ratio
        self.sample_rate = sample_rate
        self.comp_makeup_gain = make_up_gain

    # Function to convert dB to linear gain
    @staticmethod
    def db_to_linear(db):
        return 10 ** (db / 20)

    # Function to convert linear gain to dB
    @staticmethod
    def linear_to_db(linear):
        return 20 * np.log10(linear)

    def compressor(self, audio):
        # Convert threshold to linear gain
        threshold_linear = self.opt_compressor.db_to_linear(self.comp_threshold)
        
        # Attack and release coefficients (simple exponential smoothing)
        attack_coeff = np.exp(-1 / (self.attack_time * self.sample_rate))
        release_coeff = np.exp(-1 / (self.release_time * self.sample_rate))

        # Initialize variables
        gain = 1.0
        envelope = 0.0
        output_audio = np.zeros_like(audio)

        for i, sample in enumerate(audio):
            # Envelope follower (simple peak detection)
            envelope = max(abs(sample), envelope * attack_coeff)
            
            # Compression (apply soft knee curve)
            if envelope > threshold_linear:
                # Simple ratio compression
                compressed_gain = 1 - (1 - self.comp_ratio) * (envelope - threshold_linear) / envelope
                compressed_gain = np.clip(compressed_gain, 0, 1)  # Ensure gain doesn't exceed 1
            else:
                compressed_gain = 1
            
            # Smooth the gain using release coefficient
            if compressed_gain < gain:
                gain = compressed_gain + (gain - compressed_gain) * release_coeff
            else:
                gain = compressed_gain

            # Apply compression and make-up gain
            output_audio[i] = sample * gain * self.opt_compressor.db_to_linear(self.comp_makeup_gain)

        return output_audio

    def process(self, audio):
        # Apply the compressor effect
        processed_audio = self.opt_compressor.compressor(self, audio)
        return processed_audio
