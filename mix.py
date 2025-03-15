class Mixer:
    def process(self, signal, effect, mixAmount):
        output = (effect * mixAmount) + (signal  * (1 - mixAmount))
        return output
