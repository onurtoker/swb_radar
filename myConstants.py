# All constants used for the USRP experiments (Global variables)

# LO frequency
fLO = 2400e6
# Sampling frequency
fs = 0.1e6
# LO settling time
lo_settling_time = 100e-3

# TX channels
channelsTX = (0,)
# TX gains in dB
gainTX = (70,)

# RX channels
channelsRX = (0,1)
# RX gains in dB
gainRX = (50,70)

# Number of samples in a I/Q data frame
ns = 2040
# High resolution factor for FFT plots
hrf = 1

# Number of repetitions
nrep = 5