import os
import numpy as np
from jaratoolbox import spikesanalysis
from jaratoolbox import celldatabase
from jaratoolbox import ephyscore
from jaratoolbox import settings
from jaratoolbox import extraplots
from jaratoolbox import colorpalette as cp
import figparams
reload(figparams)
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec

dbPath = os.path.join(settings.FIGURES_DATA_PATH, figparams.STUDY_NAME, 'celldatabase_NBQX.h5')
database = celldatabase.load_hdf(dbPath)

colorControl = cp.TangoPalette['Aluminium5']
colorLaser = cp.TangoPalette['SkyBlue1']
colorNBQX = cp.TangoPalette['Plum1']
# colorNBQX = 'm'

waveformLineWidth = 2
psthLineWidth = 2
psthXrange = [-0.1, 1]
psthStart = 20 #Index to start (we compute more psth values than we want to show)

fontSizeLabels = figparams.fontSizeLabels * 2
fontSizeTicks = figparams.fontSizeTicks * 2
fontSizePanel = figparams.fontSizePanel * 2

SAVE_FIGURE = 1
outputDir='/tmp'
figFilename = 'plots_method' # Do not include extension
figFormat = 'svg' # 'pdf' or 'svg'
figSize = [13,4] # In inches

# cell = ephyscore.Cell(dbRow)

examples = [

    {'subject':'pinp031',
     'date':'2018-06-28',
     'depth':2251.0,
     'tetrode':6,
     'cluster':4},

    {'subject':'pinp031',
     'date':'2018-06-28',
     'depth':2423.0,
     'tetrode':1,
     'cluster':4},

    {'subject':'pinp031',
     'date':'2018-06-28',
     'depth':2423,
     'tetrode':6,
     'cluster':3},

    ]

plt.clf()
nCriteria = 3
gsAllCriteria = gridspec.GridSpec(nCriteria, 1, hspace=0.5, wspace=0.6, top=0.95)
gsAllCriteria.update(left=0.25, right=0.98)
nExamples = 3
wSpaceExamples = 0.5

gsCriterion = []
examplesAllCriteria = []
for indCriterion in [0, 1]:
    gsThisCriterion = gridspec.GridSpecFromSubplotSpec(1, nExamples, subplot_spec=gsAllCriteria[indCriterion],
                                                       wspace=wSpaceExamples)
    gsCriterion.append(gsThisCriterion)
    examplesThisCriterion = []
    for indExample in range(nExamples):
        #Define the shape for each subplot here
        gsThisExample = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gsThisCriterion[indExample])
        examplesThisCriterion.append(gsThisExample)
    examplesAllCriteria.append(examplesThisCriterion)

#Waveform/rasterplots
indCriterion=2
gsThisCriterion = gridspec.GridSpecFromSubplotSpec(1, nExamples, subplot_spec=gsAllCriteria[indCriterion],
                                                   wspace=wSpaceExamples)
gsCriterion.append(gsThisCriterion)
examplesThisCriterion = []
for indExample in range(nExamples):
    #Define the shape for each subplot here
    gsThisExample = gridspec.GridSpecFromSubplotSpec(1, 7, subplot_spec=gsThisCriterion[indExample], wspace=1)
    examplesThisCriterion.append(gsThisExample)
examplesAllCriteria.append(examplesThisCriterion)


def plot_psth_axes(ax, startX, startY, stopX, stopY, offset=0.2, xLabel=None, yLabel=None):
    dx = stopX - startX
    dy = stopY - startY
    offsetX = dx*(offset*2)
    offsetY = dy*offset
    #Plot x
    ax.plot([startX-offsetX, stopX-offsetX], [startY-offsetY, startY-offsetY], 'k-', clip_on=False, lw=2)
    #Plot y
    ax.plot([startX-offsetX, startX-offsetX], [startY-offsetY, stopY-offsetY], 'k-', clip_on=False, lw=2)
    if xLabel is not None:
        ax.text(stopX-offsetX, startY-offsetY*2, xLabel, ha='right', va='top', fontsize=fontSizeTicks)
    if yLabel is not None:
        # ax.text(startX-(offsetX*1.2), stopY-offsetY, yLabel, ha='right', va='top', rotation=90)
        ax.text(startX-(offsetX*1.2), stopY-offsetY, yLabel, ha='right', va='top', fontsize=fontSizeTicks)

def plot_stim_bars(ax, barY, xStarts, barLength, lw=2, color=colorLaser):
    for xStart in xStarts:
        ax.plot([xStart, xStart+barLength], [barY, barY], '-', lw=lw, color=color)


labelPosX = [0.01, 0.23, 0.5, 0.775]   # Horiz position for panel labels
labelPosY = [0.94]    # Vert position for panel labels



plt.clf()

# Criterion 1: Responds to laser pulse

labelHeightFactor = 0.8

indCriterion = 0
for indExample in range(nExamples):

    indRow, dbRow = celldatabase.find_cell(database, **examples[indExample])
    cell = ephyscore.Cell(dbRow)

    ### -- Pre -- ###
    sessiontype = 'laserpulse_pre'
    axPSTH = plt.subplot(examplesAllCriteria[indCriterion][indExample][0])

    ephysData, bdata = cell.load(sessiontype)
    eventOnsetTimes = ephysData['events']['stimOn']
    eventOnsetTimes = spikesanalysis.minimum_event_onset_diff(eventOnsetTimes, minEventOnsetDiff=0.5)

    if not indCriterion == 2:
        timeRange = [-0.3, 1.0]
    else:
        timeRange = [-0.01, 0.05]

    (spikeTimesFromEventOnset,
    trialIndexForEachSpike,
    indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(ephysData['spikeTimes'],
                                                                    eventOnsetTimes,
                                                                    timeRange)


    smoothPSTH = True
    smoothWinSize = 3
    binsize = 10 #in milliseconds
    binEdges = np.around(np.arange(timeRange[0]-(binsize/1000.0), timeRange[1]+2*(binsize/1000.0), (binsize/1000.0)), decimals=2)
    winShape = np.concatenate((np.zeros(smoothWinSize),np.ones(smoothWinSize))) # Square (causal)
    winShape = winShape/np.sum(winShape)
    psthTimeBase = np.linspace(timeRange[0], timeRange[1], num=len(binEdges)-1)

    spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,
                                                                indexLimitsEachTrial,binEdges)

    thisPSTH = np.mean(spikeCountMat,axis=0)
    if smoothPSTH:
        thisPSTH = np.convolve(thisPSTH, winShape, mode='same')
    ratePSTH = thisPSTH/float(binsize/1000.0)
    maxRatePre = np.max(ratePSTH)
    axPSTH.plot(psthTimeBase[psthStart:], ratePSTH[psthStart:], '-',
                color=colorControl, lw=psthLineWidth, clip_on=False)
    axPSTH.set_ylim([0, maxRatePre*1.2])
    axPSTH.set_xlim(psthXrange)
    axPSTH.text(0.4, maxRatePre*labelHeightFactor, 'Control', ha='left', color=colorControl, fontsize=fontSizeTicks)
    # extraplots.boxoff(axPSTH)
    axPSTH.axis('off')
    plot_stim_bars(axPSTH, maxRatePre+maxRatePre*0.1, [0], 0.1)
    if indExample==0:
        plot_psth_axes(axPSTH, 0, 0, 0.5, maxRatePre/2.0, xLabel='500 ms', yLabel='{}\nspk/s'.format(int(maxRatePre/2)))
    else:
        plot_psth_axes(axPSTH, 0, 0, 0.5, maxRatePre/2.0, xLabel=None, yLabel='{}\nspk/s'.format(int(maxRatePre/2)))

    ### -- Post -- ###
    sessiontype = 'laserpulse_post'
    axPSTH = plt.subplot(examplesAllCriteria[indCriterion][indExample][1])

    ephysData, bdata = cell.load(sessiontype)
    eventOnsetTimes = ephysData['events']['stimOn']
    eventOnsetTimes = spikesanalysis.minimum_event_onset_diff(eventOnsetTimes, minEventOnsetDiff=0.5)

    if not indCriterion == 2:
        timeRange = [-0.3, 1.0]
    else:
        timeRange = [-0.01, 0.05]

    (spikeTimesFromEventOnset,
    trialIndexForEachSpike,
    indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(ephysData['spikeTimes'],
                                                                    eventOnsetTimes,
                                                                    timeRange)

    smoothPSTH = True
    smoothWinSize = 3
    binsize = 10 #in milliseconds
    binEdges = np.around(np.arange(timeRange[0]-(binsize/1000.0), timeRange[1]+2*(binsize/1000.0), (binsize/1000.0)), decimals=2)
    winShape = np.concatenate((np.zeros(smoothWinSize),np.ones(smoothWinSize))) # Square (causal)
    winShape = winShape/np.sum(winShape)
    psthTimeBase = np.linspace(timeRange[0], timeRange[1], num=len(binEdges)-1)

    spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,
                                                                indexLimitsEachTrial,binEdges)

    thisPSTH = np.mean(spikeCountMat,axis=0)
    if smoothPSTH:
        thisPSTH = np.convolve(thisPSTH, winShape, mode='same')
    ratePSTH = thisPSTH/float(binsize/1000.0)
    psthStart = 20
    axPSTH.plot(psthTimeBase[psthStart:], ratePSTH[psthStart:], '-',
                color=colorNBQX, lw=psthLineWidth, clip_on=False)

    axPSTH.set_ylim([0, maxRatePre*1.2])
    plot_stim_bars(axPSTH, maxRatePre+maxRatePre*0.1, [0], 0.1)
    axPSTH.set_xlim(psthXrange)
    axPSTH.text(0.4, maxRatePre*labelHeightFactor, 'NBQX', ha='left', color=colorNBQX, fontsize=fontSizeTicks)
    # extraplots.boxoff(axPSTH)
    axPSTH.axis('off')

    # # Waveform Comparison
    # plt.subplot(examplesAllCriteria[indCriterion][indExample][2])


# Criterion 2: Responds to laser pulse

indCriterion = 1
for indExample in range(nExamples):

    indRow, dbRow = celldatabase.find_cell(database, **examples[indExample])
    cell = ephyscore.Cell(dbRow)

    ### -- Pre -- ###
    sessiontype = 'lasertrain_pre'
    axPSTH = plt.subplot(examplesAllCriteria[indCriterion][indExample][0])

    ephysData, bdata = cell.load(sessiontype)
    eventOnsetTimes = ephysData['events']['stimOn']
    eventOnsetTimes = spikesanalysis.minimum_event_onset_diff(eventOnsetTimes, minEventOnsetDiff=0.5)

    if not indCriterion == 2:
        timeRange = [-0.3, 1.0]
    else:
        timeRange = [-0.01, 0.05]

    (spikeTimesFromEventOnset,
    trialIndexForEachSpike,
    indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(ephysData['spikeTimes'],
                                                                    eventOnsetTimes,
                                                                    timeRange)


    smoothPSTH = True
    smoothWinSize = 3
    binsize = 10 #in milliseconds
    binEdges = np.around(np.arange(timeRange[0]-(binsize/1000.0), timeRange[1]+2*(binsize/1000.0), (binsize/1000.0)), decimals=2)
    winShape = np.concatenate((np.zeros(smoothWinSize),np.ones(smoothWinSize))) # Square (causal)
    winShape = winShape/np.sum(winShape)
    psthTimeBase = np.linspace(timeRange[0], timeRange[1], num=len(binEdges)-1)

    spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,
                                                                indexLimitsEachTrial,binEdges)

    thisPSTH = np.mean(spikeCountMat,axis=0)
    if smoothPSTH:
        thisPSTH = np.convolve(thisPSTH, winShape, mode='same')
    ratePSTH = thisPSTH/float(binsize/1000.0)
    maxRatePre = np.max(ratePSTH)
    axPSTH.plot(psthTimeBase[psthStart:], ratePSTH[psthStart:], '-',
                color=colorControl, lw=psthLineWidth, clip_on=False)
    axPSTH.set_ylim([0, maxRatePre*1.2])
    plot_stim_bars(axPSTH, maxRatePre+maxRatePre*0.1, [0, 0.2, 0.4, 0.6, 0.8], 0.01)
    plot_psth_axes(axPSTH, 0, 0, 0.5, maxRatePre/2.0, xLabel=None, yLabel='{}\nspk/s'.format(int(maxRatePre/2)))
    # axPSTH.set_xlim([-0.05, 1])
    axPSTH.set_xlim(psthXrange)
    # extraplots.boxoff(axPSTH)
    axPSTH.axis('off')
    plot_psth_axes(axPSTH, 0, 0, 0.5, maxRatePre/2.0)

    ### -- Post -- ###
    sessiontype = 'lasertrain_post'
    axPSTH = plt.subplot(examplesAllCriteria[indCriterion][indExample][1])

    ephysData, bdata = cell.load(sessiontype)
    eventOnsetTimes = ephysData['events']['stimOn']
    eventOnsetTimes = spikesanalysis.minimum_event_onset_diff(eventOnsetTimes, minEventOnsetDiff=0.5)

    if not indCriterion == 2:
        timeRange = [-0.3, 1.0]
    else:
        timeRange = [-0.01, 0.05]

    (spikeTimesFromEventOnset,
    trialIndexForEachSpike,
    indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(ephysData['spikeTimes'],
                                                                    eventOnsetTimes,
                                                                    timeRange)

    smoothPSTH = True
    smoothWinSize = 3
    binsize = 10 #in milliseconds
    binEdges = np.around(np.arange(timeRange[0]-(binsize/1000.0), timeRange[1]+2*(binsize/1000.0), (binsize/1000.0)), decimals=2)
    winShape = np.concatenate((np.zeros(smoothWinSize),np.ones(smoothWinSize))) # Square (causal)
    winShape = winShape/np.sum(winShape)
    psthTimeBase = np.linspace(timeRange[0], timeRange[1], num=len(binEdges)-1)

    spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,
                                                                indexLimitsEachTrial,binEdges)

    thisPSTH = np.mean(spikeCountMat,axis=0)
    if smoothPSTH:
        thisPSTH = np.convolve(thisPSTH, winShape, mode='same')
    ratePSTH = thisPSTH/float(binsize/1000.0)
    axPSTH.plot(psthTimeBase[psthStart:], ratePSTH[psthStart:], '-',
                color=colorNBQX, lw=psthLineWidth, clip_on=False)

    axPSTH.set_ylim([0, maxRatePre*1.2])
    plot_stim_bars(axPSTH, maxRatePre+maxRatePre*0.1, [0, 0.2, 0.4, 0.6, 0.8], 0.01)
    # axPSTH.set_xlim([-0.05, 1])
    axPSTH.set_xlim(psthXrange)
    # extraplots.boxoff(axPSTH)
    axPSTH.axis('off')

    # # Waveform Comparison
    # plt.subplot(examplesAllCriteria[indCriterion][indExample][2])


indCriterion = 2
for indExample in range(nExamples):

    indRow, dbRow = celldatabase.find_cell(database, **examples[indExample])
    cell = ephyscore.Cell(dbRow)

    ### -- Pre -- ###
    sessiontype = 'laserpulse_pre'
    axRaster = plt.subplot(examplesAllCriteria[indCriterion][indExample][:5])

    ephysData, bdata = cell.load(sessiontype)
    eventOnsetTimes = ephysData['events']['stimOn']
    eventOnsetTimes = spikesanalysis.minimum_event_onset_diff(eventOnsetTimes, minEventOnsetDiff=0.5)

    timeRangeForRaster = [0, 0.075]

    (spikeTimesFromEventOnset,
    trialIndexForEachSpike,
    indexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(ephysData['spikeTimes'],
                                                                    eventOnsetTimes,
                                                                    timeRangeForRaster)

    axRaster.plot(spikeTimesFromEventOnset, trialIndexForEachSpike, 'k.', ms=1)
    # axRaster.axvline(x=0.01)
    # extraplots.boxoff(axRaster)
    axRaster.axis('off')

    xTickRange = [0, timeRangeForRaster[-1]]
    xAxisYval = -10
    textOffset = 15
    yTickRange = 10
    plt.plot([xTickRange[0], xTickRange[1]], [xAxisYval, xAxisYval], 'k-')
    plt.plot([xTickRange[0], xTickRange[0]], [xAxisYval, xAxisYval-yTickRange], 'k-')
    plt.plot([xTickRange[1], xTickRange[1]], [xAxisYval, xAxisYval-yTickRange], 'k-')
    plt.text(xTickRange[0], xAxisYval-textOffset, '0', ha='center', va='top', fontsize=fontSizeTicks)
    plt.text(xTickRange[1], xAxisYval-textOffset, '{}'.format(int(timeRangeForRaster[1]*1000)), ha='center', va='top', fontsize=fontSizeTicks)
    plt.text(np.mean(xTickRange), xAxisYval-textOffset*1.5, 'Time from\nlaser onset (ms)', ha='center', va='top', fontsize=fontSizeTicks)


#Waveform comparison plots
for indExample in range(nExamples):

    indRow, dbRow = celldatabase.find_cell(database, **examples[indExample])
    cell = ephyscore.Cell(dbRow)
    axWave = plt.subplot(examplesAllCriteria[indCriterion][indExample][5:])
    axWave.hold(1)

    ### -- Pre -- ###
    sessiontype = 'noiseburst_pre'
    ephysData, bdata = cell.load(sessiontype)
    samples = ephysData['samples']
    channelMax = np.argmin(samples.mean(axis=0).min(axis=1)) #Find the index of the channel with the largest min (biggest channel)
    avgWave = samples.mean(axis=0)[channelMax,:]
    stdWave = samples.std(axis=0)[channelMax,:]
    axWave.plot(avgWave, '-', color=colorControl, lw=waveformLineWidth, zorder=0)
    # axWave.fill_between(range(len(avgWave)), avgWave+stdWave, avgWave-stdWave, color='0.5')


    ### -- Post -- ###
    sessiontype = 'noiseburst_post'
    ephysData, bdata = cell.load(sessiontype)

    samples = ephysData['samples']
    channelMax = np.argmin(samples.mean(axis=0).min(axis=1)) #Find the index of the channel with the largest min (biggest channel)
    avgWave = samples.mean(axis=0)[channelMax,:]
    stdWave = samples.std(axis=0)[channelMax,:]
    axWave.plot(avgWave, '-', color=colorNBQX, lw=waveformLineWidth, zorder=1)
    axWave.axis('off')

    scaleBarStartX = 20
    scaleBarLength = 30
    scaleBarY = np.min(avgWave)
    axWave.text(scaleBarStartX+scaleBarLength+3, scaleBarY+scaleBarY*0.1, "1 ms", fontsize=fontSizeTicks, ha='right', va='top')

    axWave.plot([scaleBarStartX, scaleBarStartX+scaleBarLength], [scaleBarY, scaleBarY], '-', lw=2, color='k', clip_on=False)


axRaster.annotate('A', xy=(labelPosX[0],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axRaster.annotate('B', xy=(labelPosX[1],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axRaster.annotate('C', xy=(labelPosX[2],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')
axRaster.annotate('D', xy=(labelPosX[3],labelPosY[0]), xycoords='figure fraction',
             fontsize=fontSizePanel, fontweight='bold')


plt.show()
if SAVE_FIGURE:
    extraplots.save_figure(figFilename, figFormat, figSize, outputDir)

