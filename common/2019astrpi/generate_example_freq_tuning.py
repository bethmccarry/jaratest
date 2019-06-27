'''
Generate npz file for tuningCurve heatmaps
'''
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from jaratoolbox import settings
from jaratoolbox import extraplots
from jaratoolbox import ephyscore
from jaratoolbox import spikesanalysis
from jaratoolbox import extraplots
from jaratoolbox import spikesorting
from jaratoolbox import ephyscore
from jaratoolbox import celldatabase
from jaratoolbox import behavioranalysis
from scipy import stats
import pandas as pd
import studyparams
reload(extraplots)
reload(studyparams)

#===================================parameters=================================
baseRange = [-0.1, 0]
responseRange = [0, 0.1]
alignmentRange = [baseRange[0], responseRange[1]]
msRaster = 2

FIGNAME = 'figure_frequency_tuning'
titleExampleBW=True

d1mice = studyparams.ASTR_D1_CHR2_MICE
nameDB = '_'.join(d1mice) + '.h5'
pathtoDB = os.path.join(studyparams.PATH_TO_TEST,nameDB)
db = pd.read_hdf(pathtoDB)


examples = {}
examples.update({'D1':'d1pi032_2019-02-22_2900.0_TT3c6'})
examples.update({'nD1':'d1pi032_2019-02-19_3200.0_TT8c4'})

exampleCell = [val for key, val in examples.items()]
exampleKeys = [key for key, val in examples.items()]

exampleSpikeData = {}
#===========================Create and save figures=============================
for ind, cellInfo in enumerate(exampleCell):

    (subject, date, depth, tetrodeCluster) = cellInfo.split('_')
    depth = float(depth)
    tetrode = int(tetrodeCluster[2])
    cluster = int(tetrodeCluster[4:])
    indRow, dbRow = celldatabase.find_cell(db, subject, date, depth, tetrode, cluster)

    oneCell = ephyscore.Cell(dbRow)

    ephysData, bdata = oneCell.load('tuningCurve')
    spikeTimes = ephysData['spikeTimes']
    eventOnsetTimes = ephysData['events']['stimOn']
#--------------------------Tuning curve------------------------------------------
## Parameters
    currentFreq = bdata['currentFreq']

    uniqFreq = np.unique(currentFreq)

    currentIntensity = bdata['currentIntensity']
    possibleIntensity = np.unique(bdata['currentIntensity'])
    nIntenLabels = len(possibleIntensity)
    lowIntensity = min(possibleIntensity)
    highIntensity = max(possibleIntensity)
    intensities = np.linspace(lowIntensity, highIntensity, nIntenLabels)
    intensities = intensities.astype(np.int)
    intenTickLocations = np.linspace(0, nIntenLabels-1, nIntenLabels)
    allIntenResp = np.empty((len(possibleIntensity), len(uniqFreq)))

    for indinten, inten in enumerate(possibleIntensity):

        for indfreq, freq in enumerate(uniqFreq):
            selectinds = np.flatnonzero((currentFreq==freq)&(currentIntensity==inten))
            #=====================index mismatch=====================================
            while selectinds[-1] >= eventOnsetTimes.shape[0]:
                 selectinds = np.delete(selectinds,-1,0)
            #------------------------------------------------------------------------------
            selectedOnsetTimes = eventOnsetTimes[selectinds]
            (spikeTimesFromEventOnset,
            trialIndexForEachSpike,
            indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(spikeTimes,
                                                                        selectedOnsetTimes,
                                                                        alignmentRange)
            nspkResp = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,
                                                            indexLimitsEachTrial,
                                                            responseRange)
            allIntenResp[indinten, indfreq] = np.mean(nspkResp)
    exampleSpikeData.update({exampleKeys[ind]:allIntenResp})

exampleDataPath = os.path.join(settings.FIGURES_DATA_PATH, studyparams.STUDY_NAME, FIGNAME, 'data_freq_tuning_examples.npz')
np.savez(exampleDataPath, **exampleSpikeData)
