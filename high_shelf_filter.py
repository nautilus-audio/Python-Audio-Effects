from pedalboard import Pedalboard, HighShelfFilter, Gain

def process(input_audio, sample_rate, cutoff_freq=3480, gain_db=3):
    """
    Apply a high-shelf filter with specified cutoff frequency and gain.
    
    :param input_audio: The input audio signal (numpy array).
    :param sample_rate: The sample rate of the audio signal.
    :param cutoff_freq: The cutoff frequency for the high-shelf filter in Hz.
    :param gain_db: The gain to apply to the frequencies above the cutoff (in dB).
    :return: The filtered audio signal.
    """
    # Create a Pedalboard with the HighShelfFilter
    board = Pedalboard([
        HighShelfFilter(cutoff_frequency_hz=cutoff_freq, gain_db=gain_db),
    ])
    
    # Apply the high-shelf filter to the audio signal
    processed_audio = board(input_audio, sample_rate)
    
    return processed_audio