import numpy as np
import os
import soundfile as sf

class Tests:
    def test_diff(input, output):
        print("Comparison: ", np.allclose(input, output))

if __name__ == "__main__":
    input = "Audio/Output/M_T1_Dry_ResEq1.wav"
    output = "Audio/Output/M_T1_Dry_ResEq1_Mix.wav"

    inputData, sample_rate = sf.read(input)
    outputData, sample_rate = sf.read(output)

    test = Tests

    test.test_diff(inputData, outputData)


            
