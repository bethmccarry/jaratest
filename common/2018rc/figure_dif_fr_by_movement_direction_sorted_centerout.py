import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from jaratoolbox import colorpalette as cp
from jaratoolbox import extraplots
from jaratoolbox import settings
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import figparams
reload(figparams)
import scipy.stats as stats

FIGNAME = 'dif_fr_by_movement_sorted_center-out'
dataDir = os.path.join(settings.FIGURES_DATA_PATH, figparams.STUDY_NAME, FIGNAME)
STUDY_NAME = figparams.STUDY_NAME
binWidth = 0.01 #0.01
removeSideInTrials = True
controlForSound = True

colorMap = 'PiYG'  #'bwr' #'PiYG'#'RdYlBu'

SAVE_FIGURE = 1
outputDir = '/tmp/'
figFilename = 'figure_movement_selectivity_overtime'#'figure_dif_fr_by_movement_dir_sorted_centerout_{}ms_bin'.format(int(binWidth*1000)) # Do not include extension
figFormat = 'pdf' # 'pdf' or 'svg'
figSize = [7, 7]
#figSize = [5, 6]

fontSizeLabels = figparams.fontSizeLabels
fontSizeTicks = figparams.fontSizeTicks
fontSizePanel = figparams.fontSizePanel

#labelPosX = [0.015, 0.45]   
#labelPosY = [0.95]    
labelPosX = [0.02, 0.46]   
labelPosY = [0.95] 

fig = plt.gcf()
fig.clf()
fig.set_facecolor('w')

gs = gridspec.GridSpec(1, 2)
gs.update(left=0.1, right=1, top=0.95, bottom=0.08, wspace=0.4, hspace=1.7)


movementSelWin = [0.0,0.3] #[0.05,0.15]
if removeSideInTrials:
    dataFilename = 'average_spike_count_by_movement_direction_{}ms_bin_{}_win_removed_sidein_trials.npz'.format(int(binWidth*1000), movementSelWin)
else:
    dataFilename = 'average_spike_count_by_movement_direction_{}ms_bin_{}_win.npz'.format(int(binWidth*1000), movementSelWin)
dataFilePath = os.path.join(dataDir, dataFilename)
data = np.load(dataFilePath)
aveSpikeCountByBlock = data['aveSpikeCountByBlock']
encodeMv = data['encodeMv']
timeBinEdges = np.around(data['timeVec'], decimals=2)
brainAreaEachCell = data['brainAreaEachCell']
#soundRespInds = data['soundRespInds']
#binWidth = np.around(data['binWidth'], decimals=2)
timePeriodToPlot = [0, 0.3]
startInd = list(timeBinEdges).index(timePeriodToPlot[0])
endInd = list(timeBinEdges).index(timePeriodToPlot[1])
numOfBins = endInd - startInd
absSpikeDifEachCell = np.abs(aveSpikeCountByBlock[0,:,:] - aveSpikeCountByBlock[1,:,:])
absSpikeDifEachCell = absSpikeDifEachCell[startInd:endInd, :]
sortedAbsSpikeDifEachCell = np.zeros(absSpikeDifEachCell.shape)
# move left - move right
spikeDifIndEachCell = (aveSpikeCountByBlock[0,:,:] - aveSpikeCountByBlock[1,:,:]) / (aveSpikeCountByBlock[0,:,:] + aveSpikeCountByBlock[1,:,:])
spikeDifIndEachCell[np.isnan(spikeDifIndEachCell)] = 0 # for those bins that does not have a spike, set index to 0
spikeDifIndEachCell = spikeDifIndEachCell[startInd:endInd, :]

brainAreaLabels = np.unique(brainAreaEachCell)
maxDifBinEachCellBothAreas = []
posNegPeakCountBothAreas = []

#fig, axes = plt.subplots(1, 2)
#fig.set_facecolor('w')
#ax0 = axes[0]
#ax1 = axes[1]

ax0 = plt.subplot(gs[:,0])
ax0.annotate('A', xy=(labelPosX[0],labelPosY[0]), xycoords='figure fraction', fontsize=fontSizePanel, fontweight='bold')

ax1 = plt.subplot(gs[:,1])
ax1.annotate('B', xy=(labelPosX[1],labelPosY[0]), xycoords='figure fraction', fontsize=fontSizePanel, fontweight='bold')

allAxes = [ax0,ax1]

for indA,brainArea in enumerate(brainAreaLabels):
    if controlForSound:
        cellsThisArea = ((brainAreaEachCell==brainArea) & encodeMv)
    else:
        cellsThisArea = (brainAreaEachCell==brainArea)
    spikeDifIndEachCellThisArea = spikeDifIndEachCell[:, cellsThisArea]
    maxDifBinEachCellThisArea = np.argmax(np.abs(spikeDifIndEachCellThisArea), axis=0)
    maxDifBinEachCellBothAreas.append(maxDifBinEachCellThisArea)
    meanPeakBinNum = np.mean(maxDifBinEachCellThisArea)
    medianPeakBinNum = np.median(maxDifBinEachCellThisArea)
    chisq, pVal = stats.chisquare(maxDifBinEachCellThisArea)
    print('For {}, using chi square test for uniform distribution of max dif bin, p={}'
        .format(brainArea, pVal))
    print('For {}, mean peak bin number is {}, median peak bin number is {}'
        .format(brainArea, meanPeakBinNum, medianPeakBinNum))
    maxDifEachCellThisArea = spikeDifIndEachCellThisArea[maxDifBinEachCellThisArea, range(len(maxDifBinEachCellThisArea))]
    negPeakDifCells = maxDifEachCellThisArea < 0
    posPeakDifCells = maxDifEachCellThisArea > 0
    posNegPeakCountBothAreas.append([sum(posPeakDifCells), sum(negPeakDifCells)])
    print('For {}, there are {} positive peak cells and {} negative peak cells'
        .format(brainArea, sum(posPeakDifCells), sum(negPeakDifCells)))
    cellReIndNeg = np.argsort(maxDifBinEachCellThisArea[negPeakDifCells])
    cellReIndPos = np.argsort(maxDifBinEachCellThisArea[posPeakDifCells])
    #pdb.set_trace()
    sortedSpikeDifIndEachNegPeakCell = spikeDifIndEachCellThisArea[:, negPeakDifCells][:, cellReIndNeg]
    sortedSpikeDifIndEachPosPeakCell = spikeDifIndEachCellThisArea[:, posPeakDifCells][:, cellReIndPos]
    sortedSpikeDifIndEachCellThisArea = np.hstack((sortedSpikeDifIndEachPosPeakCell, sortedSpikeDifIndEachNegPeakCell))
    
    #ax = plt.subplot(1,2,indA+1)
    ax = allAxes[indA]
    #ax.imshow(np.transpose(sortedAbsSpikeDifEachCellThisArea), origin='lower', cmap='viridis', interpolation='nearest')
    im = ax.imshow(np.transpose(sortedSpikeDifIndEachCellThisArea), origin='lower', cmap=colorMap, 
        vmin=-1, vmax=1, interpolation='nearest', aspect='auto')
    ax.set_xticks(range(numOfBins+1)[::10])#np.arange(len(timeBinEdges))[::10])
    #ax.set_xticklabels([0. , 0.1, 0.2, 0.3])
    xTickLabels = ['{:.1f}'.format(x) for x in np.arange(timePeriodToPlot[0],timePeriodToPlot[1]+0.1,0.1)]
    ax.set_xticklabels(xTickLabels)
    #xticklabels = ['{:.1f}'.format(x) for x in xticks]
    #ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    #plt.yticks([150, 50], brainAreaLabels)
    ax.set_yticks([0,50,100])
    if indA == 0:
        ax.set_ylabel('Cell number')
    ax.set_xlabel('Time from movement onset (s)')
    ax.set_title(brainArea[5:])

ax0.set_title('AC')
ax1.set_title('pStr')

#fig.text(0.3, 0.08, 'Time from movement onset (s)')
plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15, wspace=0.4, hspace=0.2)
#cbar_ax = fig.add_axes([0.95, 0.15, 0.05, 0.7])
#cbar = fig.colorbar(im, ticks=[-1, 0, 1], ax=allAxes.ravel().tolist())
cbar = fig.colorbar(im, ticks=[-1, 0, 1], ax=allAxes)
cbar.ax.set_yticklabels(['-1', '0', '1'])
cbar.set_label('Choice selectivity index',size=fontSizeTicks)

# Stats #
zScore, pVal = stats.ranksums(*maxDifBinEachCellBothAreas)
print('Using bin width of {}s, compare time bin number for peak difference between the two brain areas yielded p value of {:.3f} using Wilcoxon rank sums test.'.format(binWidth, pVal))

#plt.tight_layout()
if SAVE_FIGURE:
    extraplots.save_figure(figFilename, figFormat, figSize, outputDir)

plt.show()
