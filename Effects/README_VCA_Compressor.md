# **VCA Compressor - Explanation**

## **Overview**
This document explains the core functionality of the **VCA (Voltage Controlled Amplifier) Compressor** implemented in Python. The compressor **reduces the dynamic range** of an audio signal by attenuating loud sounds above a threshold while maintaining softer sounds.

---

## **1. `Setup` Method**
### **Purpose:**  
Initializes the compressor’s parameters, including **frame size, channels, sample rate, and compression settings**.

### **Breakdown:**
```python
def Setup(self, framesize, channels, sample_rate):
    self.framesize = framesize
    self.channels = channels
    self.sample_rate = sample_rate
    inputBuffer = np.empty((framesize, channels))  # Create a working buffer
    self.threshold_ = -20  # Compression threshold in dB
    self.ratio_ = 2.5  # Compression ratio
```
- **`framesize`**: The number of audio samples per processing frame.
- **`channels`**: Number of audio channels (e.g., 1 for mono, 2 for stereo).
- **`sample_rate`**: The audio sample rate (e.g., 44100 Hz).
- **`inputBuffer`**: A temporary **buffer for signal analysis**.
- **`self.threshold_`**: If the signal exceeds `-20 dB`, compression is applied.
- **`self.ratio_`**: Determines how much gain reduction is applied **(higher = stronger compression).**

---

## **2. `Process` Method**
### **Purpose:**  
Applies **dynamic range compression** to an input audio buffer.

### **Breakdown:**
```python
def Process(self, inputBuffer, channel):
```
- **`inputBuffer`**: A NumPy array containing the audio samples.
- **`channel`**: The specific channel being processed (not used in this version).

### **1. Initialize Variables**
```python
bufferSize = self.framesize
samplerate = self.sample_rate
yL_prev = 0
```
- **`bufferSize`**: Number of samples in the buffer.
- **`samplerate`**: The sample rate (e.g., 44100 Hz).
- **`yL_prev`**: Stores the **previous** gain reduction level.

```python
x_g = np.zeros(bufferSize)  # Input gain in dB
x_l = np.zeros(bufferSize)  # Level reduction amount
y_g = np.zeros(bufferSize)  # Output gain after compression
y_l = np.zeros(bufferSize)  # Smoothed gain reduction
c = np.zeros(bufferSize)  # Control voltage (applied to signal)
```
- **These arrays store different gain-related values for each audio sample.**

---

### **2. Set Compression Parameters**
```python
tauAttack_ = 20  # Attack time (ms)
tauRelease_ = 60  # Release time (ms)
makeUpGain_ = 5  # Boost applied after compression
```
- **`tauAttack_`**: Determines how fast compression **kicks in** after detecting a loud signal.
- **`tauRelease_`**: Determines how fast the compressor **stops compressing** when the signal drops.
- **`makeUpGain_`**: Boosts the output signal to compensate for volume reduction.

```python
alphaAttack = np.exp(-1/(0.001 * samplerate * tauAttack_))
alphaRelease = np.exp(-1/(0.001 * samplerate * tauRelease_))
```
- **`alphaAttack` & `alphaRelease`**: These values **control smoothing** for attack & release behavior.

---

### **3. Compute Gain Reduction**
```python
for i in range(bufferSize):
    if (np.fabs(inputBuffer[i]) < 0.000001):
        x_g[i] = -120  # Silence detection (avoid log(0))
    else:
        x_g[i] = 20 * np.log10(np.fabs(inputBuffer[i]))  # Convert signal level to dB
```
- **If the sample is silent** (`< 0.000001`), set `x_g[i] = -120 dB` (very quiet).
- Otherwise, **convert the absolute signal value to dB**.

```python
    if (x_g[i] >= self.threshold_):
        y_g[i] = self.threshold_ + (x_g[i] - self.threshold_) / self.ratio_
    else:
        y_g[i] = x_g[i]
    x_l[i] = x_g[i] - y_g[i]
```
- **If the signal is above the threshold (`-20 dB`)**, it is **compressed** using the `ratio_`.
- The difference **`x_l[i]`** is how much the signal level is **reduced**.

---

### **4. Apply Attack & Release Smoothing**
```python
    if (x_l[0] > yL_prev):
        y_l[i] = alphaAttack * yL_prev + (1 - alphaAttack) * x_l[i]  # Attack phase
    else:
        y_l[i] = alphaRelease * yL_prev + (1 - alphaRelease) * x_l[i]  # Release phase
```
- **If gain reduction is increasing**, apply **attack time smoothing**.
- **If gain reduction is decreasing**, apply **release time smoothing**.

```python
    c[i] = pow(10.0, (makeUpGain_ - y_l[i]) / 20.0)  # Convert dB to linear gain
    yL_prev = y_l[i]  # Update previous level
```
- Convert **gain reduction** from **dB to linear scale** for volume adjustment.

---

### **5. Apply Gain Reduction to Signal**
```python
for i in range(bufferSize):
    inputBuffer[i] *= c[i]  # Apply control voltage (compression)
```
- **Each sample is multiplied by `c[i]`**, which applies **volume attenuation** based on compression.

---

### **6. Return Processed Audio**
```python
return inputBuffer
```
- Returns the **compressed** audio signal.

---

## **Example Usage**
```python
compressor = VCA_Compressor()
compressor.Setup(framesize=1024, channels=1, sample_rate=44100)

audio_data = np.random.randn(1024)  # Simulated audio input
processed_audio = compressor.Process(audio_data, channel=0)
```
- Creates a compressor instance.
- Sets up parameters for **frame size, channels, and sample rate**.
- Processes an **example audio signal**.

---

## **Why This Works Well**
✅ **Smooth & natural compression** using attack/release times.  
✅ **Threshold & ratio-based dynamic range control**.  
✅ **Prevents sudden volume changes** by applying gain smoothing.  
✅ **Ensures audio clarity** by compensating with makeup gain.  

---

This document provides a detailed breakdown of the **VCA Compressor**, ensuring a clear understanding of how it processes and enhances audio quality.

