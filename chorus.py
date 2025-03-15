from pedalboard import Chorus
import pedalboard as pd

class GVChorus(object):
    def __init__(self, rateHz, depth, cDelay, feedback, mix):
        self.rate = rateHz
        self.depth = depth
        self.centre_delay_ms = cDelay
        self.feedback = feedback
        self.mix = mix

    def UpdateParams(self, rateHz, depth, cDelay, feedback, mix):
        self.rate = rateHz
        self.depth = depth
        self.centre_delay_ms = cDelay
        self.feedback = feedback
        self.mix = mix
        Chorus(self.rate, self.depth, self.centre_delay_ms, self.feedback, self.mix)

        # Define the chorus effect with options
    def create_chorus(rateHz=5, depth=20, cDelay=20, feedback=50, mix=0.35):
        return Chorus(rate_hz=rateHz, depth=depth, centre_delay_ms=cDelay, feedback=feedback, mix=mix)


    def Process(self, buffer, frameSize, sampleRate):
        board = pd.Pedalboard([
            Chorus(rate_hz=5, depth=0.1, centre_delay_ms=10, feedback=0.2, mix=0.15)
        ])

        processed_audio = board(buffer, sampleRate)
        return processed_audio