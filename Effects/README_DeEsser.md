# **De-Esser Implementation - Explanation**

## **Overview**
This document explains the core functionality of the **De-Esser** implemented in Python. The de-esser is designed to reduce sibilance in audio signals by identifying and attenuating excessive high-frequency energy.

---

## **1. `_butter_bandpass` Method**
### **Purpose:**  
Creates a **bandpass filter** to isolate the **sibilant frequencies** in speech/audio.  

### **How it Works:**
```python
 def _butter_bandpass(self, lowcut, highcut, fs, order=4):
```
- `lowcut`: The **lower** frequency limit of the bandpass filter.
- `highcut`: The **upper** frequency limit of the bandpass filter.
- `fs`: The **sampling rate** of the audio.
- `order`: The **order of the filter** (higher = sharper cutoff, but can cause phase issues).

```python
 nyq = 0.5 * fs
```
- The **Nyquist frequency** (`nyq`) is half the sampling rate (`fs`).
- This is the **maximum frequency** that can be represented in the audio signal.

```python
 low = lowcut / nyq
 high = highcut / nyq
```
- **Normalize** `lowcut` and `highcut` by dividing by `nyq`, so they are within `[0, 1]`.

```python
 sos = butter(order, [low, high], btype='bandpass', analog=False, output='sos')
```
- Uses **SciPy’s `butter()` function** to create a **Butterworth bandpass filter**.
- **`btype='bandpass'`**: Allows only frequencies between `lowcut` and `highcut` to pass.
- **`output='sos'`**: Returns the filter in **Second-Order Sections (SOS)** format, which is **numerically stable**.

```python
 return sos
```
- Returns the **filter coefficients**, which will be used to filter the audio.

---

## **2. `process` Method**
### **Purpose:**
Applies the **de-esser effect** to an audio signal by:
1. **Isolating sibilant frequencies** (using `_butter_bandpass`).
2. **Measuring the energy** of the sibilance.
3. **Reducing gain** dynamically if sibilance is too strong.
4. **Returning the processed audio.**

### **Step-by-Step Breakdown**
```python
 def process(self, audio):
```
- `audio`: A **NumPy array** representing the input audio signal.

### **🔹 1. Extract Sibilance Frequencies**
```python
 sos = self._butter_bandpass(self.sibilance_freq_low, self.sibilance_freq_high, self.sample_rate)
 sibilance = sosfilt(sos, audio)
```
- Calls `_butter_bandpass()` to create a **bandpass filter** for sibilance frequencies.
- **Applies the filter** using `sosfilt()` to **extract** the sibilant parts of the audio.

### **🔹 2. Compute Sibilance Energy (RMS Level)**
```python
 rms_sibilance = np.sqrt(np.mean(sibilance**2))
 sibilance_db = 20 * np.log10(rms_sibilance + 1e-10)  # Avoid log(0)
```
- **Root Mean Square (RMS)** is computed to **measure the energy** of the sibilance.
- Converted to **decibels (dB)** to compare with a threshold.
- `1e-10` prevents **logarithm of zero** errors.

### **🔹 3. Compute Dynamic Gain Reduction**
```python
 if sibilance_db > self.threshold:
 reduction_ratio = (sibilance_db - self.threshold) / self.reduction_db
 reduction_ratio = min(reduction_ratio, 1.0)  # Limit max reduction
 else:
 reduction_ratio = 0
```
- If **sibilance energy exceeds the threshold**, apply **dynamic gain reduction**.
- The louder the sibilance, the **stronger the gain reduction**.
- Capped at `1.0` to **avoid over-attenuation**.

### **🔹 4. Apply Gain Reduction**
```python
 gain = 1.0 - (reduction_ratio * (self.reduction_db / 20))
```
- Converts the **dB reduction** into a **linear gain factor**.
- **Stronger sibilance → More gain reduction**.

```python
 processed_audio = audio - (gain * sibilance)
```
- Subtracts **attenuated sibilance** from the original audio.
- This **reduces harsh “S” and “T” sounds** without affecting the rest of the audio.

### **🔹 5. Normalize Output (Prevent Clipping)**
```python
 processed_audio = np.clip(processed_audio, -1.0, 1.0)
```
- Ensures the audio **stays within the valid range** `[-1, 1]` (prevents distortion).

```python
 return processed_audio
```
- Returns the **de-essed** audio.

---

## **Summary of What Happens**
1️⃣ **Extracts sibilance** from the audio using a **bandpass filter**.
2️⃣ **Measures the loudness** of sibilance using **RMS and dB conversion**.
3️⃣ **If sibilance is too loud**, it **reduces gain dynamically**.
4️⃣ **Applies the gain reduction** to suppress harsh sounds.
5️⃣ **Returns the cleaned-up audio** with **controlled sibilance**.

---

## **Example Usage**
```python
deesser = DeEsser(sample_rate=44100, sibilance_freq_low=5000, sibilance_freq_high=12000, threshold=-30, reduction_db=6)
processed_audio = deesser.process(audio_data)
```
- Creates a **De-Esser instance** with a **5kHz - 12kHz bandpass filter**.
- Processes the input `audio_data`, reducing harsh **sibilance** sounds.

---

## **Why This Works Well**
✅ **Uses a precise bandpass filter** to target only sibilance.  
✅ **Applies gain reduction dynamically**, avoiding over-processing.  
✅ **Maintains natural vocal clarity** while reducing harshness.  
✅ **Prevents clipping** by normalizing the final output.  

---

This document provides a detailed breakdown of the de-esser functionality, ensuring a clear understanding of how it processes and enhances audio quality.

