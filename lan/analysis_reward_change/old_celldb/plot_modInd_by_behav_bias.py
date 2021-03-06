import os
import pandas as pd
import numpy as np
from jaratoolbox import settings
from jaratoolbox import extraplots
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.stats as stats
import pdb

brainRegions = ['astr', 'ac']
qualityThreshold = 3 #2.5 
maxZThreshold = 3
ISIcutoff = 0.02
alphaLevel = 0.05

modulationWindows = {'sound':['0-0.1s'],
                     'center-out': ['0.05-0.15s',
                                    '0.05-0.25s',
                                    '0.05-0.35s']
                     }
outputDir = '/home/languo/data/ephys/reward_change_stats/reports/correlation_modInd_behav'

plt.figure()

for indRegion, brainRegion in enumerate(brainRegions):
    celldbPath = os.path.join(settings.DATABASE_PATH,'reward_change_{}.h5'.format(brainRegion))
    celldb = pd.read_hdf(celldbPath, key='reward_change')
    goodQualCells = celldb.query('isiViolations<{} and shapeQuality>{} and consistentInFiring==True and keep_after_dup_test==True and inTargetArea==True and met_behav_criteria==True'.format(ISIcutoff, qualityThreshold))
    soundResp = goodQualCells.behavZscore.apply(lambda x: np.max(np.abs(x)) >=  maxZThreshold) #The bigger of the sound Z score is over threshold
    moreRespLowFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[0]) > abs(x[1]))
    moreRespHighFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[1]) > abs(x[0]))
    goodLowFreqRespCells = goodQualCells[moreRespLowFreq]
    goodHighFreqRespCells = goodQualCells[moreRespHighFreq]

    # for sound do we want to just use sound responsive cells?
    for indw, modWindow in enumerate(modulationWindows['sound']):
        lowFreqModIndName = 'modIndLow_'+modWindow+'_'+'sound'
        lowFreqModSigName = 'modSigLow_'+modWindow+'_'+'sound'
        highFreqModIndName = 'modIndHigh_'+modWindow+'_'+'sound'
        highFreqModSigName = 'modSigHigh_'+modWindow+'_'+'sound'
        #lowFreqModInd = goodQualCells[lowFreqModIndName]
        #highFreqModInd = goodQualCells[highFreqModIndName]
        lowFreqRespModInd = goodLowFreqRespCells[lowFreqModIndName]
        lowFreqRespModSig = goodLowFreqRespCells[lowFreqModSigName]
        highFreqRespModInd = goodHighFreqRespCells[highFreqModIndName]
        highFreqRespModSig = goodHighFreqRespCells[highFreqModSigName]
        lowFreqBehavBias = goodQualCells['rightwardBiasByReward'].apply(lambda x: x[0])
        highFreqBehavBias = goodQualCells['rightwardBiasByReward'].apply(lambda x: x[-1])
        lowFreqRespBehavBias = goodLowFreqRespCells['rightwardBiasByReward'].apply(lambda x: x[0])
        highFreqRespBehavBias = goodHighFreqRespCells['rightwardBiasByReward'].apply(lambda x: x[-1])
        plt.clf()
        plt.scatter(lowFreqRespBehavBias, np.abs(lowFreqRespModInd))
        plt.scatter(lowFreqRespBehavBias[lowFreqRespModSig<alphaLevel], np.abs(lowFreqRespModInd[lowFreqRespModSig<alphaLevel]), color='red')
        plt.ylabel('Modulation index (absolute)')
        plt.xlabel('Delta % rightward \n (more_right - more_left)')
        figTitle = '{} low freq responsive cells_{}'.format(brainRegion, modWindow)
        plt.title(figTitle)
        rho, pVal = stats.spearmanr(np.abs(lowFreqRespModInd), lowFreqRespBehavBias)
        plt.text(-0.2, 0.5*plt.ylim()[1], 'spearman correlation r={:.2f}, p={:.2f}'.format(rho, pVal))
        rhos, pVals = stats.spearmanr(lowFreqRespBehavBias[lowFreqRespModSig<alphaLevel], np.abs(lowFreqRespModInd[lowFreqRespModSig<alphaLevel]))
        plt.text(-0.2, 0.4*plt.ylim()[1], 'for reward-modulated cells r={:.2f}, p={:.2f}'.format(rhos, pVals))
        plt.ylim([-0.1, 0.85])
        figFullPath = os.path.join(outputDir, figTitle)
        plt.savefig(figFullPath,format='png')

        #plt.show()
        plt.clf()
        plt.scatter(highFreqRespBehavBias, np.abs(highFreqRespModInd))
        plt.scatter(highFreqRespBehavBias[highFreqRespModSig<alphaLevel], np.abs(highFreqRespModInd[highFreqRespModSig<alphaLevel]), color='red')
        plt.ylabel('Modulation index (absolute)')
        plt.xlabel('Delta % rightward \n (more_right - more_left)')
        #plt.show()
        figTitle = '{} high freq responsive cells_{}'.format(brainRegion, modWindow)
        plt.title(figTitle)
        rho, pVal = stats.spearmanr(np.abs(highFreqRespModInd), highFreqRespBehavBias)
        plt.text(-0.2, 0.5*plt.ylim()[1], 'spearman correlation r={:.2f}, p={:.2f}'.format(rho, pVal))
        rhos, pVals = stats.spearmanr(highFreqRespBehavBias[highFreqRespModSig<alphaLevel], np.abs(highFreqRespModInd[highFreqRespModSig<alphaLevel]))
        plt.text(-0.2, 0.4*plt.ylim()[1], 'for reward-modulated cells r={:.2f}, p={:.2f}'.format(rhos, pVals))
        plt.ylim([-0.1, 0.85])
        figFullPath = os.path.join(outputDir, figTitle)
        plt.savefig(figFullPath,format='png')

    for indw, modWindow in enumerate(modulationWindows['center-out']):
        leftModIndName = 'modIndLow_'+modWindow+'_'+'center-out'
        leftModSigName = 'modSigLow_'+modWindow+'_'+'center-out'
        rightModIndName = 'modIndHigh_'+modWindow+'_'+'center-out'
        rightModSigName = 'modSigHigh_'+modWindow+'_'+'center-out'
        movementSelective = goodQualCells.movementModS < alphaLevel
        goodMovementSelCells = goodQualCells[movementSelective]
        leftMovementSelModInd = goodMovementSelCells[leftModIndName]
        leftMovementSelModSig = goodMovementSelCells[leftModSigName]
        rightMovementSelModInd = goodMovementSelCells[rightModIndName]
        rightMovementSelModSig = goodMovementSelCells[rightModSigName]

        lowFreqBehavBias = goodMovementSelCells['rightwardBiasByReward'].apply(lambda x: x[0])
        highFreqBehavBias = goodMovementSelCells['rightwardBiasByReward'].apply(lambda x: x[-1])
        
        plt.clf()
        plt.scatter(lowFreqBehavBias, np.abs(leftMovementSelModInd))
        plt.scatter(lowFreqBehavBias[leftMovementSelModSig<alphaLevel],np.abs(leftMovementSelModInd[leftMovementSelModSig<alphaLevel]), color='red')
        plt.ylabel('Modulation index (absolute)')
        plt.xlabel('Delta % rightward \n (more_right - more_left)')
        #plt.show()
        figTitle = '{} movement selective cells going left_{}'.format(brainRegion, modWindow)
        plt.title(figTitle)
        rho, pVal = stats.spearmanr(np.abs(leftMovementSelModInd), lowFreqBehavBias)
        plt.text(-0.2, 0.5*plt.ylim()[1], 'spearman correlation r={:.2f}, p={:.2f}'.format(rho, pVal))
        rhos, pVals = stats.spearmanr(lowFreqBehavBias[leftMovementSelModSig<alphaLevel],np.abs(leftMovementSelModInd[leftMovementSelModSig<alphaLevel]))
        plt.text(-0.2, 0.4*plt.ylim()[1], 'for reward-modulated cells r={:.2f}, p={:.2f}'.format(rhos, pVals))
        plt.ylim([-0.1, 0.85])
        figFullPath = os.path.join(outputDir, figTitle)
        plt.savefig(figFullPath,format='png')

        plt.clf()
        plt.scatter(highFreqBehavBias, np.abs(rightMovementSelModInd))
        plt.scatter(highFreqBehavBias[rightMovementSelModSig<alphaLevel], np.abs(rightMovementSelModInd[rightMovementSelModSig<alphaLevel]), color='red')
        plt.ylabel('Modulation index (absolute)')
        plt.xlabel('Delta % rightward \n (more_right - more_left)')
        #plt.show()
        figTitle = '{} movement selective cells going right_{}'.format(brainRegion, modWindow)
        plt.title(figTitle)
        rho, pVal = stats.spearmanr(np.abs(rightMovementSelModInd), highFreqBehavBias)
        plt.text(-0.2, 0.5*plt.ylim()[1], 'spearman correlation r={:.2f}, p={:.2f}'.format(rho, pVal))
        rhos, pVals = stats.spearmanr(highFreqBehavBias[rightMovementSelModSig<alphaLevel], np.abs(rightMovementSelModInd[rightMovementSelModSig<alphaLevel]))
        plt.text(-0.2, 0.4*plt.ylim()[1], 'for reward-modulated cells r={:.2f}, p={:.2f}'.format(rhos, pVals))
        plt.ylim([-0.1, 0.85])
        figFullPath = os.path.join(outputDir, figTitle)
        plt.savefig(figFullPath,format='png')
