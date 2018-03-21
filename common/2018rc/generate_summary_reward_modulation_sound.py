'''
Generate and store summary data for reward modulation index for astr or ac in reward-change task. 

Lan Guo 20180221
'''
import os
import sys
import numpy as np
import pandas as pd
from jaratoolbox import settings
import figparams
reload(figparams)

STUDY_NAME = figparams.STUDY_NAME

FIGNAME = 'reward_modulation_sound'
dataDir = os.path.join(settings.FIGURES_DATA_PATH, STUDY_NAME, FIGNAME)

if not os.path.exists(dataDir):
    os.mkdir(dataDir)

####################################################################################
scriptFullPath = os.path.realpath(__file__)
brainAreas = ['rightAC','rightAStr']
maxZThreshold = 3
alphaLevel = 0.05
modWindow = '0-0.1s'
###################################################################################
dbKey = 'reward_change'
dbFolder = os.path.join(settings.FIGURES_DATA_PATH, STUDY_NAME)
celldbPath = os.path.join(dbFolder, 'rc_database.h5')
celldb = pd.read_hdf(celldbPath, key=dbKey)

for brainArea in brainAreas:
    goodQualCells = celldb.query("keepAfterDupTest==True and brainArea=='{}'".format(brainArea))

    soundResp = goodQualCells.behavZscore.apply(lambda x: np.max(np.abs(x)) >=  maxZThreshold) #The bigger of the sound Z score is over threshold
    moreRespLowFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[0]) > abs(x[1]))
    moreRespHighFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[1]) > abs(x[0]))
    goodLowFreqRespCells = goodQualCells[moreRespLowFreq]
    goodHighFreqRespCells = goodQualCells[moreRespHighFreq]

    lowFreqModIndName = 'modIndLow_'+modWindow+'_'+'sound'
    lowFreqModSigName = 'modSigLow_'+modWindow+'_'+'sound'
    lowFreqModDirName = 'modDirLow_'+modWindow+'_'+'sound'
    highFreqModIndName = 'modIndHigh_'+modWindow+'_'+'sound'
    highFreqModSigName = 'modSigHigh_'+modWindow+'_'+'sound'
    highFreqModDirName = 'modDirHigh_'+modWindow+'_'+'sound'
            
    goodLowFreqRespModInd = (-1) * goodLowFreqRespCells[lowFreqModIndName]
    goodLowFreqRespModSig = goodLowFreqRespCells[lowFreqModSigName]
    goodLowFreqRespModDir = goodLowFreqRespCells[lowFreqModDirName]
    goodHighFreqRespModInd = goodHighFreqRespCells[highFreqModIndName]
    goodHighFreqRespModSig = goodHighFreqRespCells[highFreqModSigName]
    goodHighFreqRespModDir = goodHighFreqRespCells[highFreqModDirName]
    
    sigModulatedLow = (goodLowFreqRespModSig < alphaLevel) & (goodLowFreqRespModDir > 0)
    sigModulatedHigh = (goodHighFreqRespModSig < alphaLevel) & (goodHighFreqRespModDir > 0)
    sigModI = np.concatenate((goodLowFreqRespModInd[sigModulatedLow].values,
                                      goodHighFreqRespModInd[sigModulatedHigh].values))
    nonsigModI = np.concatenate((goodLowFreqRespModInd[~sigModulatedLow].values,
                                      goodHighFreqRespModInd[~sigModulatedHigh].values))
    allModI = np.concatenate((goodLowFreqRespModInd.values, goodHighFreqRespModInd.values))
    # -- Save summary data -- #    
    outputFile = 'summary_reward_modulation_sound_{}.npz'.format(brainArea)
    outputFullPath = os.path.join(dataDir,outputFile)
    np.savez(outputFullPath, brainArea=brainArea, soundResponsive=soundResp, goodLowFreqRespCells=goodLowFreqRespCells, goodHighFreqRespCells=goodHighFreqRespCells, sigModulatedLow=sigModulatedLow, sigModulatedHigh=sigModulatedHigh, sigModI=sigModI, nonsigModI=nonsigModI, allModI=allModI, script=scriptFullPath)