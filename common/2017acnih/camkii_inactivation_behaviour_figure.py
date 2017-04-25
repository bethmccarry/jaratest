from statsmodels.stats.proportion import proportion_confint
import numpy as np
from jaratest.anna import behaviour_test as bt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'Helvetica'
matplotlib.rcParams['svg.fonttype'] = 'none'

fontSizeLabels = 14
fontSizeTicks = 12
fontSizePanel = 16

animal = 'band011'
sessions = ['20170314a','20170315a','20170324a']
validPerSNR, rightPerSNR, possibleSNRs, laserTrialTypes = bt.band_SNR_laser_psychometric(animal, sessions)
colours = ['k','g']
for las in range(len(validPerSNR)):
    bt.plot_psychometric(validPerSNR[las,:], rightPerSNR[las,:], possibleSNRs, colour = colours[las])
plt.ylabel('% rightward choice', fontsize=fontSizeLabels)
plt.xlabel('Signal to noise ratio (dB)', fontsize=fontSizeLabels)
plt.show()