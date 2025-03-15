from pedalboard import Pedalboard, Gain

def process(audio, sample_rate, gain_db):
    """Applies gain to the audio signal.

    Args:
        audio (np.ndarray): Input audio data.
        sample_rate (int): Sample rate of the audio.

    Returns:
        np.ndarray: Processed audio with gain applied.
    """
    # Define the pedalboard with effects
    board = Pedalboard([
        Gain(gain_db) # Apply gain of 3 dB
    ])

    # Process audio through the pedalboard
    processed_audio = board(audio, sample_rate)
    return processed_audio