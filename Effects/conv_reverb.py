from pedalboard import Pedalboard, Convolution, Reverb
from pedalboard.io import AudioFile

# Load an impulse response (IR) file for convolution reverb
# ir_file = "Audio/Reverbs/Church Schellingwoude.wav"
# ir_file = "Audio/Reverbs/emt_140_bright_2.wav"
ir_file = "Audio/Reverbs/A_Plate.aif"



def process(audio, sr):
    # Create a Pedalboard with the Convolution reverb
    pedalboard = Pedalboard([
        Convolution(ir_file, 0.35),  # Adjust the mix parameter as needed
    ])

    # Apply the effects
    effected = pedalboard(audio, sr)
    return effected

