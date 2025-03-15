import numpy as np

class VCA_Compressor(object):
        def Setup(self, framesize, channels, sample_rate):
            self.framesize = framesize
            self.channels = channels
            self.sample_rate = sample_rate
            inputBuffer = np.empty((framesize, channels)) # Working buffer to analyse
            self.threshold_ = -12
            self.ratio_ = 2.5

        # def UpdateParams(self):
    
        def Process(self, inputBuffer):
            # the input signal
            bufferSize = self.framesize
            samplerate = self.sample_rate
            yL_prev = 0
            x_g = np.zeros(bufferSize)
            x_l = np.zeros(bufferSize)
            y_g = np.zeros(bufferSize)
            y_l = np.zeros(bufferSize)
            c = np.zeros(bufferSize)

            tauAttack_ = 20
            tauRelease_ = 60 # Attack and release time
            # constants
            makeUpGain_ = 5           # Compressor make-up gain
            # inputBuffer.clear(0, 0, bufferSize)
            # Mix down left-right to analyse the input
            # inputBuffer.addFrom(0, 0, buffer, channel, 0, bufferSize, 0.5)
            # inputBuffer.addFrom(0, 0, buffer, channel, 0, bufferSize, 0.5)

            # Compression: calculates the control voltage
            alphaAttack = np.exp(-1/(0.001 * samplerate *
                                        tauAttack_))
            alphaRelease = np.exp(-1/(0.001 * samplerate *
                                         tauRelease_))
            for i in range(bufferSize):
                # Level detection- estimate level using peak detector
                if (np.fabs(inputBuffer[i]) < 0.000001):
                    x_g[i] = -120
                else:
                    x_g[i] = 20 * np.log10(np.fabs(inputBuffer[i]))

                # Gain computer- static apply input/output curve
                if (x_g[i] >= self.threshold_):
                    y_g[i] = self.threshold_ + (x_g[i]-self.threshold_) / self.ratio_
                else:
                    y_g[i] = x_g[i]
                x_l[i] = x_g[i] - y_g[i]

                # Ballistics- smoothing of the gain
                if (x_l[0] > yL_prev):
                    y_l[i] = alphaAttack * yL_prev + (1 - alphaAttack ) * x_l[i]

                # Compressor thresh. in dB
                # Compression ratio
                else:
                    y_l[i] = alphaRelease* yL_prev + (1 - alphaRelease) * x_l[i]
                # Find control
                c[i] = pow(10.0, (makeUpGain_ - y_l[i]) / 20.0)
                yL_prev = y_l[i]

            # Apply control voltage to the audio signal
            for i in range(bufferSize):
                inputBuffer[i] *= c[i]

            return inputBuffer
