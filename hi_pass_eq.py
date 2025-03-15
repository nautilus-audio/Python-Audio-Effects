import pedalboard as pb

class HiPass(object):
    def __init__(self):
        self.cutoff = 125

    def update_params(self, freq):
        self.cutoff = freq

    def process(self, buffer, samplerate):
        highpass_filter = pb.HighpassFilter(125)  # Set the desired cutoff frequency
        output = highpass_filter(buffer, samplerate, len(buffer))
        return output
