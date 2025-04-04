# **GoldenVocals - Vocal Processing Chain**

## **Overview**
GoldenVocals is a **vocal processing chain** that applies multiple **audio effects** such as **compression, equalization, de-essing, chorus, reverb, and delay** to an input audio file. This script is designed for high-quality vocal enhancement, making it suitable for professional music production.

---

## **1️⃣ Dependencies & Audio File Loading**
```python
import numpy as np
from scipy.io import wavfile
import doubler, optical_compressor, vca_compressor, dynamic_eq, hi_pass_eq, chorus
from de_esser import DeEsser
import conv_reverb, distortion, tube_amp_eq, gain, delay, mix
from resonant_eq import ResonantEQ
```
- Various **DSP (Digital Signal Processing) modules** handle different effects.
- Reads the input **WAV file**:
```python
file_name = "TooLate_Vocal"
sample_rate, data = wavfile.read('Audio/' + file_name + ".wav")
```
- **`data`** is a NumPy array containing the raw audio samples.

---

## **2️⃣ `GoldenVocals` Class**
### **Purpose:**
This class initializes and processes the vocal effects chain.

### **🔹 `__init__()` Method**
```python
class GoldenVocals(object):
    def __init__(self):
```
- Initializes the **audio processing effects**.

#### **🎚️ Compressor & Chorus Setup**
```python
vca_compressor.VCA_Compressor.Setup(self, len(data[0]), data.ndim, sample_rate)
chorus.GVChorus.UpdateParams(self, rateHz=5, depth=20, cDelay=20, feedback=50, mix=0.2)
```
- **VCA Compressor**: Controls dynamics by reducing the difference between loud and quiet parts.
- **Chorus Effect**: Creates a thick, widened vocal sound.

#### **🎚️ Optical Compressor Setup**
```python
optical_compressor.OpticalCompressor.__init__(self, attack_time=0.005, release_time=0.2, threshold=-12, ratio=4, makeup_gain=True, sample_rate=44100)
optical_compressor.OpticalCompressor.set_sample_rate(self, sample_rate)
```
- **Optical Compressor**: A smooth compression effect, often used in vocals.

#### **🎚️ Delay Setup**
```python
delay.GV_Delay.__init__(self, delay_seconds=1200, feedback=0.2, mix=0.3)
```
- **Delay Effect**: Adds an echo with a **1200ms delay**.

#### **🎚️ De-Esser Setup**
```python
self.deesser1 = DeEsser(sample_rate, sibilance_freq_low=6210, sibilance_freq_high=20000, threshold=-33.84, reduction_db=6)
self.deesser2 = DeEsser(sample_rate, sibilance_freq_low=6210, sibilance_freq_high=20000, threshold=-36, reduction_db=6)
```
- **Two de-essers** remove sibilance (harsh “S” sounds) at different stages.

#### **🎚️ Equalizer Setup**
```python
self.hi_pass = hi_pass_eq.HiPass
self.resEQ1 = ResonantEQ
self.resEQ2 = ResonantEQ
```
- **Hi-Pass Filter** removes low frequencies.
- **Resonant EQs** shape the vocal tone.

---

## **3️⃣ `process()` Method**
### **Purpose:**
Applies all effects **sequentially** to the audio signal.

### **🔹 Processing Each Channel**
```python
num_channels = data.ndim
for channel in range(num_channels):
    inChannel = data[:, channel]
```
- The **loop processes each channel separately**.

### **🔹 Step-by-Step Processing Chain:**
1️⃣ **De-Esser 1** → 2️⃣ **VCA Compressor** → 3️⃣ **Gain Adjustment** → 4️⃣ **Hi-Pass Filter**  
5️⃣ **De-Esser 2** → 6️⃣ **Resonant EQ 1 & 2** → 7️⃣ **Tube EQ & Dynamic EQ** → 8️⃣ **Optical Compressor & Chorus**  
9️⃣ **(Optional) Delay & Reverb**  

```python
deEssedAudio1 = self.deesser2.process(inChannel)
compressedAudio = vca_compressor.VCA_Compressor.Process(self, deEssedAudio1, channel)
gainedAudio = gain.process(compressedAudio, sample_rate, gain_db=-6)
hiPassAudio = self.hi_pass.process(self, gainedAudio, sample_rate)
deEssedAudio2 = self.deesser1.process(hiPassAudio)
resEQOneAudio = ((self.resEQ1.process(self, deEssedAudio2) * 0.4) + (deEssedAudio2 * 0.6))
resEQTwoAudio = ((self.resEQ2.process(self, resEQOneAudio) * 0.67) + (resEQOneAudio * 0.33))
tubeEQAudio = tube_amp_eq.process(resEQTwoAudio, sample_rate)
dynEQAudio = dynamic_eq.process(tubeEQAudio, sample_rate)
opCompAudio = optical_compressor.OpticalCompressor.process(self, dynEQAudio)
chorusedAudio = chorus.GVChorus.Process(self, opCompAudio, len(inChannel), sample_rate)
```
- If `wet=True`, applies **delay & convolution reverb**.

---

## **4️⃣ Saving Processed Audio**
```python
if wet:
    wavfile.write("Audio/" + file_name + "_Wet_Full_Chain.wav", sample_rate, outputData)
else:
    wavfile.write("Audio/" + file_name + "_Dry_Full_Chain.wav", sample_rate, outputData)
```
- Saves **processed audio** as either **dry** or **wet**.

---

## **5️⃣ Running the Processor**
```python
if __name__ == "__main__":
    golden_vocals = GoldenVocals()
    golden_vocals.process()
```
- Creates an instance of `GoldenVocals` and processes the **audio file**.

---

## **🚀 Why This Works Well**
✅ **Advanced Vocal Processing** with multiple **custom DSP effects**.  
✅ **Multi-stage De-Essing** to remove sibilance effectively.  
✅ **Optimized Compression & EQ** for **professional-sounding vocals**.  

This document provides a detailed breakdown of the **GoldenVocals Processing Chain**, ensuring a clear understanding of how it enhances vocal quality.

