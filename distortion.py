
class Distortion(object):
    def __init__(self):
        self.a = 0.2

    def UpdateParams(self, value):
        self.a = value

    def TubeSaturation(x, a):
        y = 0
        threshold1 = 1.0 / 3.0
        threshold2 = 2.0 / 3.0

        if (a == 0.0):
            y = x
        elif (x > threshold2):
            y = 1.0

        elif (x > threshold1):
            y = (3.0 - ((2.0 - 3.0 * x)) *((2.0 - 3.0 * x))) / 3.0
        elif (x < -threshold2):
            y = -1.0

        elif (x < -threshold1):
            y = -(3.0 - ((2.0+ 3.0 * x)) *((2.0 + 3.0 * x))) / 3.0
        else:
            y = (2.0 * x)

        return y

    def Process(self, inputBuffer, a):
        Distortion.UpdateParams(self, a)
        length = len(inputBuffer)
        for i in range(length):
            TubeSaturation = Distortion.TubeSaturation(inputBuffer[i], self.a)
            inputBuffer[i] = TubeSaturation




