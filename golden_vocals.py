import sys
import os
import numpy as np
from scipy.io import wavfile
import soundfile as sf
import librosa
import scipy.signal as signal
import pyloudnorm as pyln

# Add effects directory to path
effects_dir = os.path.join(os.getcwd(), "Effects")
sys.path.append(effects_dir)

import doubler
import optical_compressor
import vca_compressor
import dynamic_eq
import hi_pass_eq
import chorus
from de_esser import DeEsser
import conv_reverb
import distortion
from tube_amp_eq import PultecEQP1A
import gain
from resonant_eq import ResonantEQ
import delay
import mix
import high_shelf_filter
import test_match

class GoldenVocals(object):
    def __init__(self, sample_rate, num_channels, data_length):
        vca_compressor.VCA_Compressor.Setup(self, data_length, num_channels, sample_rate)
        chorus.GVChorus.UpdateParams(self, rateHz=5, depth=20, cDelay=20, feedback=50, mix=0.2)
        self.opt_compressor = optical_compressor.OpticalCompressor
        self.opt_compressor.__init__(self, sample_rate, attack_time=0.005, release_time=0.2, threshold=-15, ratio=4, makeup_gain=True)
        delay.GV_Delay.__init__(self, feedback=0.2, mix=0.3)
        self.deesser1 = DeEsser(sample_rate, sibilance_freq_low=6210, sibilance_freq_high=20000, threshold=-33.84, reduction_db=6, range_db=6.5)
        self.deesser2 = DeEsser(sample_rate, sibilance_freq_low=6210, sibilance_freq_high=20000, threshold=-36, reduction_db=6, range_db=5.3)
        self.hi_pass = hi_pass_eq.HiPass
        self.tube_amp_eq = PultecEQP1A(sample_rate, low_freq=100, low_q=0.074738, low_boost=1.0, low_cut=1.0, high_freq=16000, high_q=0.074738, high_boost=3.5, high_cut=0.8)
        self.resEQ1 = ResonantEQ(sample_rate, 0.01, 6.0, -1.0)
        self.resEQ2 = ResonantEQ(sample_rate, 1.0, 0.01, 3.5)
        self.resEQ1.set_peak_values(peak_1_freq=1100, peak_1_gain=8.7, peak_1_q=1, peak_2_freq=4100, peak_2_gain=11, peak_2_q=1)
        self.resEQ1.set_filter_values(low_freq=20, high_freq=20000, low_gain_db=0, mid_gain_db=0, high_gain_db=0)
        self.resEQ2.set_peak_values(peak_1_freq=588, peak_1_gain=12, peak_1_q=10, peak_2_freq=0, peak_2_gain=0, peak_2_q=1)
        self.resEQ2.set_filter_values(low_freq=20, high_freq=20000, low_gain_db=0, mid_gain_db=0, high_gain_db=0)

    
    def calculate_loudness(file_path):
        """Calculate LUFS and RMS loudness of an audio file."""
        y, sr = librosa.load(file_path, sr=None)
        meter = pyln.Meter(sr)  
        lufs = meter.integrated_loudness(y)
        rms = np.sqrt(np.mean(y ** 2))
        return lufs, rms, sr

    def find_gain_adjustment(self, master_dir, stems_dir):
        """Determine gain adjustments for stems to match the master track loudness."""
        ref_gains = {}
        gains = {}
# 
        for file in os.listdir(master_dir):
            master_path = os.path.join(master_dir, file)
            master_lufs, master_rms, _ = self.calculate_loudness(master_path)
            ref_gains[file] = (master_lufs * 0.7) + (master_rms * 0.3)

        for file in os.listdir(stems_dir):
            if file.endswith(".wav"):
                stem_path = os.path.join(stems_dir, file)
                stem_lufs, stem_rms, sr = self.calculate_loudness(stem_path)

                # Balanced loudness adjustment: blend LUFS and RMS
                lufs_adjustment = master_lufs - stem_lufs
                rms_adjustment = 20 * np.log10(master_rms / (stem_rms + 1e-6))  # Avoid division by zero
                gain_adjustment = (lufs_adjustment * 0.7) + (rms_adjustment * 0.3)

                # Ensure reductions are explicitly negative
                if gain_adjustment > 0:
                    gain_adjustment = abs(gain_adjustment)  # Boost (positive)
                else:
                    gain_adjustment = -abs(gain_adjustment)  # Reduction (negative)

                # Cap excessive gain changes
                gain_adjustment = np.clip(gain_adjustment, -6, 3)  # Max boost +3 dB, max cut -6 dB

                gains[file] = (gain_adjustment, sr)

        return gains, ref_gains

    def apply_gain_adjustment(self, data, gain_db, sr):
        """Apply a gain adjustment to an audio file and save the result."""
        y = data
        gain_factor = 10 ** (gain_db / 20)  # Convert dB to linear scale
        y_adjusted = np.clip((y * gain_factor) * .707, -1, 1)  # Prevent clipping, gain stage with -3 dB
        return y_adjusted

    def process(self, data, sample_rate, file_name, tempo, wet=True):
        output_data = np.zeros_like(data, dtype=np.float32)
        num_channels = data.shape[1]

        delay.GV_Delay.set_delay_seconds(self, tempo)
        
        for channel in range(num_channels):
            in_channel = data[:, channel]
            if(file=="F_T2.wav"):
                in_channel = self.apply_gain_adjustment(in_channel, 6, sr)

            de_essed_audio1 = self.deesser2.process(in_channel)
            compressed_audio = vca_compressor.VCA_Compressor.Process(self, de_essed_audio1)
            gained_audio = gain.process(compressed_audio, sample_rate, -6)
            res_eq_one_audio = self.resEQ1.process(gained_audio)
            res_eq_one_audio_mix = mix.Mixer.process(self, gained_audio, res_eq_one_audio, 0.4)
            res_eq_two_audio = self.resEQ2.process(res_eq_one_audio_mix)
            res_eq_two_audio_mix = mix.Mixer.process(self, res_eq_one_audio_mix, res_eq_two_audio, 0.47)
            dyn_eq_audio = dynamic_eq.process(self, res_eq_two_audio_mix)
            op_comp_audio = self.opt_compressor.process(self, dyn_eq_audio)
            tube_eq_audio = self.tube_amp_eq.process(op_comp_audio)
            gained_audio3 = gain.process(tube_eq_audio, sample_rate, 6)
            de_essed_audio2 = self.deesser1.process(gained_audio3)
            high_shelf_audio = high_shelf_filter.process(de_essed_audio2, sample_rate)
            output = high_shelf_audio
            
            if wet:
                chorused_audio = chorus.GVChorus.Process(self, output, len(in_channel), sample_rate)
                delayed_audio = delay.GV_Delay.process(self, chorused_audio, sample_rate)
                reverb_audio = conv_reverb.process(delayed_audio, sample_rate)
                output_data[:, channel] = reverb_audio
            else:
                output_data[:, channel] = output

        # Avoid clipping the output too aggressively, use soft limiting or careful clipping.
        np.clip(output_data, -1.0, 1.0, out=output_data)

        # Save processed file
        output_filename = f"Audio/Output/{file_name}_{'Wet' if wet else 'Dry'}_FullChain_v6.0.wav"
        sf.write(output_filename, output_data, sample_rate, subtype='PCM_24')
        return output_data

if __name__ == "__main__":
    audio_dir = "Audio/Input/"
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".wav")]
    tempos = np.zeros(len(audio_files))
    
    for i, file in enumerate(audio_files):
        # if i > 1:
        #     break
        # else:
        file_path = os.path.join(audio_dir, file)
        data, sample_rate = sf.read(file_path)

        # Load the audio file
        audio_file = file_path  # Replace with your audio file path
        y, sr = librosa.load(audio_file, sr=None)

        # Estimate the tempo
        tempos[i], _ = librosa.beat.beat_track(y=y, sr=sr)

        print(f"Processing: {file}")
        golden_vocals = GoldenVocals(sample_rate, data.ndim, len(data))
        # gains, ref_gains = golden_vocals.find_gain_adjustment(f"Audio/Input/{file}", f"Audio/Output/")
        # golden_vocals.process(data, sample_rate, os.path.splitext(file)[0], tempos[i], wet=True)
        output_data = golden_vocals.process(data, sample_rate, os.path.splitext(file)[0], tempos[i], wet=False)
        
        # golden_vocals.apply_gain_adjustment(output_data, output_path, gain_db, sr)
