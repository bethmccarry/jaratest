'''
Script to plot significantly reward-modulated cells that were also responsive to the modulated frequency.
'''
import os
import imp
import shutil
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from jaratoolbox import settings
reload(settings)
from jaratest.lan.analysis_reward_change import reward_change_loader_plotter_functions as rcfuncs
reload(rcfuncs)
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

colorDictRC = {'leftMoreLowFreq':'g', #green
               'rightMoreLowFreq':'m', #magenta
               'sameRewardLowFreq':'y', #yellow
               'leftMoreHighFreq':'r', #red
               'rightMoreHighFreq':'b', #blue
               'sameRewardHighFreq':'darkgrey'}


#animalLists = [['adap005','adap012', 'adap013', 'adap015', 'adap017'], ['gosi001','gosi004', 'gosi008','gosi010']]
animalList = ['adap067', 'adap071'] #['gosi001','gosi004', 'gosi008','gosi010','adap005','adap012', 'adap013', 'adap015', 'adap017']
#animalLabels = ['astr', 'ac']

freqLabels = ['Low','High']
qualityThreshold = 3 #2.5 
maxZThreshold = 3
ISIcutoff = 0.02
alphaLevel = 0.05

modulationWindows = {'sound':['0-0.1s']}

for indRegion, animal in enumerate(animalList):
    celldbPath = os.path.join(settings.DATABASE_PATH,'{}_database.h5'.format(animal))
    celldb = pd.read_hdf(celldbPath, key='reward_change')

    # -- Take movement-selected cells that are modulated by reward expectation, plot the modulated movement direction -- #
    goodQualCells = celldb.query('isiViolations<{} and shapeQuality>{} and consistentInFiring==True and keep_after_dup_test==True and inTargetArea==True and met_behav_criteria==True'.format(ISIcutoff, qualityThreshold))

    #soundResp = goodQualCells.behavZscore.apply(lambda x: np.max(np.abs(x)) >=  maxZThreshold) #The bigger of the sound Z score is over threshold
    #moreRespLowFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[0]) > abs(x[1]))
    #moreRespHighFreq = soundResp & goodQualCells.behavZscore.apply(lambda x: abs(x[1]) > abs(x[0]))
    respLowFreq = goodQualCells.behavZscore.apply(lambda x: abs(x[0]) >= maxZThreshold)
    respHighFreq = goodQualCells.behavZscore.apply(lambda x: abs(x[-1]) >= maxZThreshold)
    #goodLowFreqRespCells = goodQualCells[moreRespLowFreq]
    #goodHighFreqRespCells = goodQualCells[moreRespHighFreq]
    goodLowFreqRespCells = goodQualCells[respLowFreq]
    goodHighFreqRespCells = goodQualCells[respHighFreq]

    for indw, modWindow in enumerate(modulationWindows['sound']):
        lowFreqModIndName = 'modIndLow_'+modWindow+'_'+'sound'
        lowFreqModSigName = 'modSigLow_'+modWindow+'_'+'sound'
        highFreqModIndName = 'modIndHigh_'+modWindow+'_'+'sound'
        highFreqModSigName = 'modSigHigh_'+modWindow+'_'+'sound'          
        goodLowFreqRespModSig = goodLowFreqRespCells[lowFreqModSigName]
        goodHighFreqRespModSig = goodHighFreqRespCells[highFreqModSigName]
        sigModulatedLow = goodLowFreqRespModSig < alphaLevel
        sigModulatedHigh = goodHighFreqRespModSig < alphaLevel
        sigModLowCells = goodLowFreqRespCells[sigModulatedLow]
        sigModHighCells = goodHighFreqRespCells[sigModulatedHigh]
        
        newOutputDir = '/home/languo/data/ephys/reward_change_stats/modulated_cells_reports/mod_{}_sound_responsive'.format(modWindow)
        if not os.path.exists(newOutputDir):
            os.mkdir(newOutputDir)

        oldOutputDir = '/home/languo/data/ephys/reward_change_stats/modulated_cells_reports/sound_responsive'.format(modWindow)

        for freq, cells in zip(freqLabels, [sigModLowCells, sigModHighCells]):
            for indc, cell in cells.iterrows():
                if freq == 'Low':
                    indf = 0
                elif freq == 'High':
                    indf = -1
                modIndName = 'modInd'+freq+'_'+modWindow+'_sound'
                modSigName = 'modSig'+freq+'_'+modWindow+'_sound'
                animal = cell['animalName']
                date = cell['date']
                tetrode = int(cell['tetrode'])
                cluster = int(cell['cluster'])
                modIThisFreqThisWindow = cell[modIndName]
                modSigThisFreqThisWindow = cell[modSigName]
                movementModInd = cell['movementModI']
                spikeQuality = cell['shapeQuality']

                figname = '{}_{}_T{}_c{}_{}_{}_sound.png'.format(animal,date,tetrode,cluster, freq, modWindow)
                figOldFullPath = os.path.join(oldOutputDir, figname)
                figNewFullPath = os.path.join(newOutputDir, figname)
                if os.path.exists(figOldFullPath):
                    shutil.copyfile(figOldFullPath, figNewFullPath)
                elif os.path.exists(figNewFullPath):
                    continue
                else:
                    tuningSessionInd = cell['sessiontype'].index('tc')
                    tuningEphysThisCell = cell['ephys'][tuningSessionInd]
                    tuningBehavThisCell = cell['behavior'][tuningSessionInd]
                    thisFreqZscore = cell['behavZscore'][indf]
                    rcInd = cell['sessiontype'].index('behavior')
                    rcEphysThisCell = cell['ephys'][rcInd]
                    rcBehavThisCell = cell['behavior'][rcInd]
                    print 'Ploting report for {} {} T{}c{}'.format(animal,date,tetrode,cluster)
                    plt.figure(figsize=(18,9))
                    gs = gridspec.GridSpec(2,3)
                    gs.update(left=0.1, right=0.9, wspace=0.5, hspace=0.2)
                    gs00 = gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=gs[0,1], hspace=0.1)
                    gs01 = gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=gs[0,2], hspace=0.1)

                    # Tuning raster
                    ax1 = plt.subplot(gs[0, 0])
                    try:
                        rcfuncs.plot_tuning_raster(animal, tuningEphysThisCell, tuningBehavThisCell, tetrode, cluster, intensity=50, timeRange = [-0.5,1])
                        ax1.set_title('Z score for {} freq: {:.3f}'.format(freq, thisFreqZscore))
                    except:
                        ax1.set_title('Cannot load tuning data or clustering for tuning session had failed')
                        pass
                    # centerout-aligned this freq 
                    alignment = 'sound' #modWindow.split('_')[1]
                    ax2 = plt.subplot(gs00[0:2, :])
                    rcfuncs.plot_reward_change_raster(animal, rcBehavThisCell, rcEphysThisCell, tetrode, cluster, freqToPlot=freq.lower(), byBlock=True, alignment=alignment, timeRange=[-0.3,0.5])
                    ax2.set_title('Reward modulation {}: {:.3f}\npVal {:.2E}'.format(modWindow, modIThisFreqThisWindow, modSigThisFreqThisWindow))
                    ax3 = plt.subplot(gs00[2, :])
                    rcfuncs.plot_reward_change_psth(animal, rcBehavThisCell, rcEphysThisCell, tetrode, cluster, freqToPlot=freq.lower(), byBlock=True, alignment=alignment, timeRange=[-0.3,0.5], binWidth=0.010)

                    # Plot movement-related response, includes all valid trials (correct&incorrect)
                    ax4 = plt.subplot(gs01[0:2, :])
                    rcfuncs.plot_movement_response_raster(animal, rcBehavThisCell, rcEphysThisCell, tetrode, cluster, alignment='center-out', timeRange=[-0.3,0.5])
                    ax4.set_title('Movement modulation index: {:.3f}'.format(movementModInd))
                    ax5 = plt.subplot(gs01[2, :])
                    rcfuncs.plot_movement_response_psth(animal, rcBehavThisCell, rcEphysThisCell, tetrode, cluster, alignment='center-out', timeRange=[-0.3,0.5], binWidth=0.010)

                    # Plot spike quality summary graphs
                    ax6 = plt.subplot(gs[1, 0])
                    rcfuncs.plot_waveform_each_cluster(animal, rcEphysThisCell, tetrode, cluster)
                    ax6.set_title('spike shape quality: {:.3f}'.format(spikeQuality))

                    ax7 = plt.subplot(gs[1,1])
                    rcfuncs.plot_isi_loghist_each_cluster(animal, rcEphysThisCell, tetrode, cluster)

                    ax8 = plt.subplot(gs[1, 2])
                    rcfuncs.plot_events_in_time_each_cluster(animal, rcEphysThisCell, tetrode, cluster)

                    plt.suptitle(figname)
                    # Save figure

                    plt.savefig(figNewFullPath)
