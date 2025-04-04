The `peaking_eq` function applies a **peaking equalizer (EQ)** filter to an audio signal, which boosts or cuts a specific frequency range in the signal. It's typically used to emphasize or reduce certain frequencies without affecting others too much, especially in the high-frequency range. This is done using a **biquad filter** (a second-order filter).

Here’s a breakdown of how the function works:

### Function Arguments:
- **audio (numpy.ndarray)**: The input audio signal you want to apply the EQ to. It's typically a 1D array containing the samples of the audio.
- **sample_rate (int)**: The sample rate of the audio signal (how many samples are captured per second, e.g., 44,100 samples per second).
- **center_freq (float)**: The frequency around which you want to apply the boost or cut (in Hz). This is the "center" of the filter.
- **q_factor (float)**: The quality factor of the filter, which controls the bandwidth of the boost or cut. A higher `q_factor` means a narrower peak, and a lower `q_factor` means a broader peak.
- **gain_db (float)**: The amount of boost (positive values) or cut (negative values) you want to apply at the center frequency, in decibels (dB).

### How the Peaking EQ Works:

1. **Gain Calculation (`A`)**:
   - The first step is to convert the gain from decibels (dB) to a linear scale (amplitude) using the formula:
     \[
     A = 10^{\frac{\text{gain\_db}}{40}}
     \]
     This ensures that the gain can be applied linearly, rather than in the dB scale.

2. **Angular Frequency (`omega`)**:
   - The `omega` is calculated from the `center_freq` (in Hz) using the formula:
     \[
     \omega = 2\pi \cdot \frac{\text{center\_freq}}{\text{sample\_rate}}
     \]
     This gives the angular frequency, which is a normalized version of the frequency with respect to the sample rate.

3. **Alpha Calculation (`alpha`)**:
   - The `alpha` is a parameter that helps define the width of the EQ peak. It’s calculated from the `q_factor`:
     \[
     \alpha = \frac{\sin(\omega)}{2 \cdot \text{q\_factor}}
     \]
     A higher `q_factor` results in a narrower peak (more selective frequency boost), and a lower `q_factor` results in a wider, more general boost across a larger frequency range.

4. **Biquad Filter Coefficients**:
   - A biquad filter is used here, which is a second-order IIR (Infinite Impulse Response) filter. It has the following general form:
     \[
     y[n] = b0 \cdot x[n] + b1 \cdot x[n-1] + b2 \cdot x[n-2] - a1 \cdot y[n-1] - a2 \cdot y[n-2]
     \]
     The coefficients for the biquad filter are computed as:
     - \( b0 = 1 + \alpha \cdot A \)
     - \( b1 = -2 \cdot \cos(\omega) \)
     - \( b2 = 1 - \alpha \cdot A \)
     - \( a0 = 1 + \frac{\alpha}{A} \)
     - \( a1 = -2 \cdot \cos(\omega) \)
     - \( a2 = 1 - \frac{\alpha}{A} \)

     These coefficients define how the filter will modify the audio signal. The `b` coefficients are the feedforward coefficients, and the `a` coefficients are the feedback coefficients.

5. **Normalization of Coefficients**:
   - The coefficients are normalized by dividing `b0`, `b1`, and `b2` by `a0` to ensure that the filter’s response is properly scaled. The `a0` term ensures that the filter's overall gain is set to 1 (i.e., no overall gain at frequencies where there is no boost or cut).

6. **Apply the Filter**:
   - The `lfilter` function from `scipy.signal` applies the biquad filter to the audio signal. It uses the coefficients (`b`, `a`) to modify the input signal (`audio`), producing the filtered audio signal.

### Output:
- The function returns the **filtered audio** signal, which has been processed by the peaking EQ filter. This signal will have the specified frequency boosted or cut around the `center_freq`, based on the `gain_db` and `q_factor` parameters.

### Example Use Case:
- **Boosting a certain frequency**: You can use this function to boost a specific frequency (e.g., 1000 Hz) to emphasize a particular aspect of the sound (e.g., vocals or guitar).
- **Cutting unwanted frequencies**: You can also use it to reduce certain frequencies (e.g., 60 Hz) to remove hum or noise.

### Summary of Key Concepts:
- The **peaking EQ filter** is a type of parametric EQ that allows you to apply a boost or cut at a specific frequency.
- The **Q factor** controls the bandwidth of the filter (how wide or narrow the frequency range is affected).
- The **gain** (in dB) controls the amount of boost or cut.
- The **biquad filter** is a simple and efficient filter type used to implement this EQ.
