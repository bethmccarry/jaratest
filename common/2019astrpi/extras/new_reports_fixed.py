"""
[For all cells in DB] create cell reports include the following plots for three sessions:
noiseburst: raster, PSTH, ISI, waverform, sparks over time
laserpulse: raster, PSTH, ISI, waveform, sparks over time
TuningCurve: raster plot(for one intensity), waveform

You have to specify the name of the subject you want to generate the reports for,
and give answer to question which duplicated session do you want to use to plot in\
case you have more than one same sessions such as laserpulse
"""

import os
import sys
import importlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from jaratoolbox import settings
from jaratoolbox import spikesanalysis
from jaratoolbox import extraplots
from jaratoolbox import spikesorting
from jaratoolbox import ephyscore
from jaratoolbox import celldatabase
from jaratoolbox import behavioranalysis
studyparams = importlib.import_module('jaratest.common.2019astrpi.studyparams')
figparams = importlib.import_module('jaratest.common.2019astrpi.figparams')

# Currently there is an issue with the subplot specs function on our version of matlab, so this function cannot be used
# UPDATE: This issue seems fixed?
def plot_am_with_rate(subplotSpec, spikeTimes, indexLimitsEachTrial, currentFreq, uniqFreq,  color='k'):
    fig = plt.gcf()

    gs = gridspec.GridSpecFromSubplotSpec(4, 4, subplot_spec=subplotSpec, wspace=-0.45, hspace=0.0)

    axRaster = plt.ubplot(fig, specRaster)
    # Possible issue in matplotlib backend preventing subplot from working properly. Based on pylab we use TkAgg
    fig.add_subplot(axRaster)
    timeRange = [-0.2, 0.7]
    freqLabels = ['{0:.0f}'.format(freq) for freq in uniqFreq]
    trialsEachCondition = behavioranalysis.find_trials_each_type(currentFreq, uniqFreq)
    pRaster, hCond, zline = extraplots.raster_plot(spikeTimes, indexLimitsEachTrial,
                                                   timeRange, trialsEachCondition, labels=freqLabels)
    plt.setp(pRaster, ms=figparams.rasterMS)

    blankLabels = ['']*11
    for labelPos in [0, 5, 10]:
        blankLabels[labelPos] = freqLabels[labelPos]

    axRaster.set_yticklabels(blankLabels)

    ax = plt.gca()
    ax.set_xticks([0, 0.5])
    ax.set_xlabel('Time from\nsound onset (s)', fontsize=fontSizeLabels, labelpad=-1)
    ax.set_ylabel('AM rate (Hz)', fontsize=fontSizeLabels, labelpad=-5)

    # ax.annotate('A', xy=(labelPosX[0],labelPosY[0]), xycoords='figure fraction',
    #             fontsize=fontSizePanel, fontweight='bold')

    countRange = [0.1, 0.5]
    spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimes, indexLimitsEachTrial, countRange)
    # numSpikesInTimeRangeEachTrial = np.squeeze(spikeCountMat)

    numSpikesInTimeRangeEachTrial = np.squeeze(np.diff(indexLimitsEachTrial,
                                                       axis=0))

    if len(numSpikesInTimeRangeEachTrial) == len(currentFreq)+1:
        numSpikesInTimeRangeEachTrial = numSpikesInTimeRangeEachTrial[:-1]
    conditionMatShape = np.shape(trialsEachCondition)
    numRepeats = np.product(conditionMatShape[1:])
    nSpikesMat = np.reshape(numSpikesInTimeRangeEachTrial.repeat(numRepeats),
                            conditionMatShape)
    spikesFilteredByTrialType = nSpikesMat * trialsEachCondition
    avgSpikesArray = np.sum(spikesFilteredByTrialType, 0) / np.sum(
        trialsEachCondition, 0).astype('float')/np.diff(np.array(countRange))
    stdSpikesArray = np.std(spikesFilteredByTrialType, 0)/np.diff(np.array(countRange))

    specRate = gs[0:3, 3]
    axRate = plt.Subplot(fig, specRate)
    fig.add_subplot(axRate)

    nRates = len(uniqFreq)
    plt.hold(True)
    plt.plot(avgSpikesArray, range(nRates), 'ro-', mec='none', ms=6, lw=3, color=color)
    plt.plot(avgSpikesArray-stdSpikesArray, range(len(uniqFreq)), 'k:')
    plt.plot(avgSpikesArray+stdSpikesArray, range(len(uniqFreq)), 'k:')
    axRate.set_ylim([-0.5, nRates-0.5])
    axRate.set_yticks(range(nRates))
    axRate.set_yticklabels([])

    # ax = plt.gca()
    axRate.set_xlabel('Firing rate\n(spk/s)', fontsize=fontSizeLabels, labelpad=-1)
    extraplots.boxoff(axRate)
    # extraplots.boxoff(ax, keep='right')
    return axRaster, axRate


if sys.version_info[0] < 3:
    inputFunc = raw_input
elif sys.version_info[0] >= 3:
    inputFunc = input

# -----------parameters----------------
timeRange = [-0.5, 0.5]
binWidth = 0.010
timeVec = np.arange(timeRange[0], timeRange[-1], binWidth)
smoothWinSizePsth = 3  # smoothWinSizePsth2 = 3
lwPsth = 2
downsampleFactorPsth = 1
msRaster = 2
tuningcurve = studyparams.tuningcurve  # ['tuningCurve','tuningCurve(tc)']

# ---------subplot adjust------------
bottom = 0.05
top = 0.93
hspace = 0.4
wspace = 0.65
left = 0.1
right = 0.88
countreport = 0  # count the number of reports generated

# ---------------------------------------------------------------------------
fig = plt.gcf()
fig.clf()

studyname = studyparams.STUDY_NAME
outputDir = os.path.join(settings.FIGURES_DATA_PATH, studyname, 'reports_am_27_test/')

d1mice = studyparams.ASTR_D1_CHR2_MICE
# nameDB = '_'.join(d1mice) + '.h5'
nameDB = "{}.h5".format('saved_frames/python27BranchIn27')
# nameDB = "{}.h5".format('temp')
pathtoDB = os.path.join(settings.FIGURES_DATA_PATH, studyparams.STUDY_NAME, nameDB)
db = celldatabase.load_hdf(pathtoDB)
celldb = db.query('rsquaredFit>{}'.format(studyparams.R2_CUTOFF))
# celldb = celldb.query('subject=="d1pi041"')

# -------------------------------------------------------------------------------
for indRow, dbRow in celldb.iterrows():
    oneCell = ephyscore.Cell(dbRow, useModifiedClusters=False)

    rast1 = []
    rast2 = []
    spkMat = []
    spikeT = []
    waveF = []
    ax = []

    tetnum = dbRow['tetrode']
    chanum = dbRow['cluster']
    # sessionCell = [con for (i, con) in enumerate(dbRow['sessionType'])]
    # sessionUC = pd.Series(sessionCell).unique()
    # sessionsOrig = [ss for ss in sessionUC if (ss == 'noiseburst') or (ss == 'laserpulse') or (ss == 'tuningCurve')]
    # sessions = np.copy(sessionsOrig)
    sessions = [sessiontype for sessiontype in dbRow['sessionType']]

    # Establishing gridspecs
    gs = gridspec.GridSpec(4, 8, width_ratios=[1, 1, 1, 1, 1, 1, 6, 4])
    gs.update(left=0.04, right=0.98, top=0.90, bottom=0.175, wspace=1.1, hspace=0.5)

    axNoiseburstRaster = plt.subplot(gs[0, 0:2])
    axLaserpulseRaster = plt.subplot(gs[0, 2:4])

    axNoiseburstPSTH = plt.subplot(gs[1, 0:2])
    axLaserpulsePSTH = plt.subplot(gs[1, 2:4])

    axTuningCurveISI = plt.subplot(gs[3, 0:2])
    axLaserpulseISI = plt.subplot(gs[2, 0:2])
    axTuningCurveWaveform = plt.subplot(gs[3, 2:4])
    axLaserpulseWaveform = plt.subplot(gs[2, 2:4])
    axTuningCurveEvents = plt.subplot(gs[2, 0:2])

    axTuningCurveRaster = plt.subplot(gs[0:3, 4:7])
    axTuningCurveHeatmap = plt.subplot(gs[3, 4:6])

    axAMRaster = plt.subplot(gs[0:, 7:])

    # ----------------Noiseburst----------------
    if "noiseburst" in sessions:
        # Loading data for session
        noiseEphysData, noBehav = oneCell.load('noiseburst')

        # Variables needed for plotting
        noiseSpikeTimes = noiseEphysData['spikeTimes']
        noiseOnsetTimes = noiseEphysData['events']['soundDetectorOn']
        (noiseSpikeTimesFromEventOnset, noiseTrialIndexForEachSpike, noiseIndexLimitsEachTrial) = \
            spikesanalysis.eventlocked_spiketimes(noiseSpikeTimes, noiseOnsetTimes, timeRange)
        noiseSpikeCountMat = spikesanalysis.spiketimes_to_spikecounts(noiseSpikeTimesFromEventOnset,
                                                                      noiseIndexLimitsEachTrial,
                                                                      timeVec)

        # -----------Plotting-------------
        # Plotting raster
        plt.sca(axNoiseburstRaster)
        pRaster, hcond, zline = extraplots.raster_plot(noiseSpikeTimesFromEventOnset,
                                                       noiseIndexLimitsEachTrial,
                                                       timeRange,
                                                       trialsEachCond=[],
                                                       colorEachCond='g')
        plt.setp(pRaster, ms=msRaster)
        plt.setp(hcond, zorder=3)
        plt.ylabel('Trial')
        axNoiseburstRaster.set_xlim(-0.3, 0.5)
        plt.title("Noiseburst")

        # Plotting PSTH
        plt.sca(axNoiseburstPSTH)
        pPSTH = extraplots.plot_psth(noiseSpikeCountMat / binWidth,
                                     smoothWinSizePsth, timeVec,
                                     trialsEachCond=[],
                                     linestyle=None, linewidth=lwPsth,
                                     downsamplefactor=downsampleFactorPsth,
                                     colorEachCond='g')
        axNoiseburstPSTH.set_xlim(-0.3, 0.5)
        extraplots.boxoff(plt.gca())
        plt.ylabel('Firing rate\n(spk/s)')
        plt.xlabel('Time from onset of the sound')

    # -----------Laserpulse------------
    if "laserpulse" in sessions:
        # Loading data for session
        laserEphysData, noBehav = oneCell.load('laserpulse')

        # Variables needed for plotting
        laserSpikeTimes = laserEphysData['spikeTimes']
        laserOnsetTimes = laserEphysData['events']['stimOn']
        (laserSpikeTimesFromEventOnset, laserTrialIndexForEachSpike, laserIndexLimitsEachTrial) = \
            spikesanalysis.eventlocked_spiketimes(laserSpikeTimes, laserOnsetTimes, timeRange)
        laserSpikeCountMat = spikesanalysis.spiketimes_to_spikecounts(laserSpikeTimesFromEventOnset,
                                                                      laserIndexLimitsEachTrial,
                                                                      timeVec)
        laserWaveform = laserEphysData['samples']
        # -----------Plotting-------------
        # Plotting raster
        plt.sca(axLaserpulseRaster)
        pRaster, hcond, zline = extraplots.raster_plot(laserSpikeTimesFromEventOnset,
                                                       laserIndexLimitsEachTrial,
                                                       timeRange,
                                                       trialsEachCond=[],
                                                       colorEachCond='r')
        plt.setp(pRaster, ms=msRaster)
        plt.setp(hcond, zorder=3)
        plt.ylabel('Trial')
        axLaserpulseRaster.set_xlim(-0.3, 0.5)
        plt.title("Laserpulse")

        # PSTH plotting
        plt.sca(axLaserpulsePSTH)
        pPSTH = extraplots.plot_psth(laserSpikeCountMat / binWidth,
                                     smoothWinSizePsth, timeVec,
                                     trialsEachCond=[], linestyle=None,
                                     linewidth=lwPsth,
                                     downsamplefactor=downsampleFactorPsth,
                                     colorEachCond='r')
        axLaserpulsePSTH.set_xlim(-0.3, 0.5)
        extraplots.boxoff(plt.gca())
        plt.ylabel('Firing rate\n(spk/s)')
        plt.xlabel('time from onset of the sound(s)')

        # Plot waveforms
        plt.sca(axLaserpulseWaveform)
        if laserWaveform.any():
            allLaserWaves, meanLaserWaves, scaleBar = spikesorting.plot_waveforms(laserWaveform)
            plt.setp(meanLaserWaves, color='r')
        plt.title("Laserpulse Waveform")


# TODO: Add tuning curve and AM in same fashion as laserpulse and noiseburst above
    # -----------AM---------------------
    if "am" in sessions:
        # Loading data for session
        amEphysData, amBehavData = oneCell.load('am')

        # General variables for am calculations/plotting
        amSpikeTimes = amEphysData['spikeTimes']
        amOnsetTime = amEphysData['events']['soundDetectorOn']
        amCurrentFreq = amBehavData['currentFreq']
        amUniqFreq = np.unique(amCurrentFreq)
        amTimeRange = [-0.2, 0.7]

        (amSpikeTimesFromEventOnset, amTrialIndexForEachSpike,
         amIndexLimitsEachTrial) = \
            spikesanalysis.eventlocked_spiketimes(amSpikeTimes,
                                                  amOnsetTime,
                                                  amTimeRange)

        amTrialsEachCondition = behavioranalysis.find_trials_each_type(amCurrentFreq, amUniqFreq)
        # Plotting
        plt.sca(axAMRaster)
        fontSizeLabels = figparams.fontSizeLabels * 2
        fontSizeTicks = fontSizeLabels
        freqLabels = ['{0:.0f}'.format(freq) for freq in amUniqFreq]
        # (axRaster, axRate) = plot_am_with_rate(axAMRaster, amSpikeTimes, amIndexLimitsEachTrial,
        #                                        amCurrentFreq, amUniqFreq)
        pRaster, hCond, zline = extraplots.raster_plot(amSpikeTimesFromEventOnset, amIndexLimitsEachTrial,
                                                       amTimeRange, trialsEachCond=amTrialsEachCondition, labels=freqLabels)
        plt.setp(pRaster, ms=figparams.rasterMS)
        blankLabels = [''] * 11
        for labelPos in [0, 5, 10]:
            blankLabels[labelPos] = freqLabels[labelPos]

        axAMRaster.set_yticklabels(blankLabels)

        axAMRaster.set_xticks([0, 0.5])
        axAMRaster.set_xlabel('Time from\nsound onset (s)', fontsize=fontSizeLabels, labelpad=-1)
        axAMRaster.set_ylabel('AM rate (Hz)', fontsize=fontSizeLabels, labelpad=-5)
        axAMRaster.set_title('AM Raster')
        # axRate.set_xlim([0, 30])
        # axRate.set_xticks([0, 30])
        # extraplots.set_ticks_fontsize(axRate, fontSizeTicks)
        extraplots.set_ticks_fontsize(axAMRaster, fontSizeTicks)

    # -----------tuningCurve------------
    if "tuningCurve" in sessions:
        # Loading data for session
        tuningEphysData, tuningBehavData = oneCell.load('tuningCurve')

        # General variables for calculations
        tuningSpikeTimes = tuningEphysData['spikeTimes']
        tuningOnsetTime = tuningEphysData['events']['soundDetectorOn']
        tuningCurrentFreq = tuningBehavData['currentFreq']
        trialsEachType = behavioranalysis.find_trials_each_type(tuningCurrentFreq,
                                                                np.unique(tuningCurrentFreq))
        tuningUniqFreq = np.unique(tuningCurrentFreq)
        b = np.array(["%.0f" % i for i in tuningUniqFreq])  # this is unique frequencies, but rounded off
        freqTicks = [str(b[i]) + " [" + str(i) + "]" for i, con in enumerate(b)]
        nTrialsEachCond = [trialsEachType[:, i].sum() for i in range(trialsEachType.shape[1])]
        new_tick_locations = np.cumsum(nTrialsEachCond)

        tuningWaveform = tuningEphysData['samples']
        # Heatmap calculations
        lowFreq = 2
        highFreq = 40
        nFreqLabels = 3

        freqTickLocations = np.linspace(0, 15, nFreqLabels)
        freqs = np.logspace(np.log10(lowFreq), np.log10(highFreq), nFreqLabels)
        freqs = np.round(freqs, decimals=1)

        baseRange = [-0.1, 0]
        responseRange = [0, 0.1]
        alignmentRange = [baseRange[0], responseRange[1]]

        currentIntensity = tuningBehavData['currentIntensity']
        possibleIntensity = np.unique(tuningBehavData['currentIntensity'])
        nIntenLabels = len(possibleIntensity)
        lowIntensity = min(possibleIntensity)
        highIntensity = max(possibleIntensity)
        intensities = np.linspace(lowIntensity, highIntensity, nIntenLabels)
        intensities = intensities.astype(np.int)
        intenTickLocations = np.linspace(0, nIntenLabels - 1, nIntenLabels)
        allIntenResp = np.empty((len(possibleIntensity), len(tuningUniqFreq)))
        for indinten, inten in enumerate(possibleIntensity):

            for indfreq, freq in enumerate(tuningUniqFreq):
                selectinds = np.flatnonzero((tuningCurrentFreq == freq) & (currentIntensity == inten))
                # =====================index mismatch======================
                while selectinds[-1] >= tuningOnsetTime.shape[0]:
                    selectinds = np.delete(selectinds, -1, 0)

                # ---------------------------------------------------------
                selectedOnsetTimes = tuningOnsetTime[selectinds]
                (tuningSpikeTimesFromEventOnset, tuningTrialIndexForEachSpike,
                 tuningIndexLimitsEachTrial) = \
                    spikesanalysis.eventlocked_spiketimes(tuningSpikeTimes,
                                                          selectedOnsetTimes,
                                                          alignmentRange)

                nspkResp = spikesanalysis.spiketimes_to_spikecounts(tuningSpikeTimesFromEventOnset, tuningIndexLimitsEachTrial,
                                                                    responseRange)

                allIntenResp[indinten, indfreq] = np.mean(nspkResp)
                FRData = allIntenResp / 0.1

        (tuningSpikeTimesFromEventOnset, tuningTrialIndexForEachSpike, tuningIndexLimitsEachTrial) = \
            spikesanalysis.eventlocked_spiketimes(tuningSpikeTimes, tuningOnsetTime, timeRange)

        # Spike count matrix for PSTH
        tuningSpikeCountMat = spikesanalysis.spiketimes_to_spikecounts(tuningSpikeTimesFromEventOnset,
                                                                       tuningIndexLimitsEachTrial,
                                                                       timeVec)

        # -----------Plotting-------------
        # if the length doesn't match, abandon last one from trialsEachType
        while tuningIndexLimitsEachTrial.shape[1] < trialsEachType.shape[0]:
            trialsEachType = np.delete(trialsEachType, -1, 0)

        plt.sca(axTuningCurveRaster)
        pRaster, hcond, zline = extraplots.raster_plot(tuningSpikeTimesFromEventOnset,
                                                       tuningIndexLimitsEachTrial,
                                                       timeRange,
                                                       trialsEachCond=trialsEachType)

        plt.setp(pRaster, ms=msRaster)
        plt.setp(hcond, zorder=3)
        plt.ylabel('Trial')
        axTuningCurveRaster.set_yticks(new_tick_locations)
        axTuningCurveRaster.set_yticklabels(new_tick_locations)
        plt.xticks(np.arange(timeRange[0], timeRange[1], .02))
        plt.xlim([-0.05, 0.3])

        ylim = axTuningCurveRaster.get_ylim()
        plt.vlines(dbRow['latency'], ylim[0], ylim[1], colors='b')

        plt.title('Tuning Curve Raster at {} db SPL'.format('all'))
        # still raster plot, plotting frequency levels
        axTuningCurveRaster.set_yticks(new_tick_locations)
        axTuningCurveRaster.set_yticklabels(freqTicks)
        axTuningCurveRaster.set_ylabel('Frequency(Hz)')

        # Waveform
        plt.sca(axTuningCurveWaveform)
        if tuningWaveform.any():
            allWaves, meanWaves, scaleBar = \
                spikesorting.plot_waveforms(tuningWaveform)
            plt.setp(meanWaves, color='b')
        plt.axis('off')
        plt.title('Tuning Curve Waveform')

        # ISI plot
        plt.sca(axTuningCurveISI)
        hpISI, ISIhistogram, ISIbins = \
            spikesorting.plot_isi_loghist(tuningSpikeTimes)
        plt.setp(hpISI, color='b')
        plt.title('Tuning Curve ISI')

        # Plot events in time
        plt.sca(axTuningCurveEvents)
        if tuningSpikeTimes.any():
            hp_Events = spikesorting.plot_events_in_time(tuningSpikeTimes)
            plt.setp(hp_Events, color='b')
        plt.title('Tuning Curve Events')

        # ----------------------- Tuning Curve heatmap --------------------
        fontSizeLabels = figparams.fontSizeLabels * 2
        fontSizeTicks = fontSizeLabels

        cax = axTuningCurveHeatmap.imshow(np.flipud(FRData),
                                          interpolation='nearest',
                                          cmap='Blues')
        cbar = plt.colorbar(cax, ax=axTuningCurveHeatmap, format='%d')
        maxFR = np.max(FRData.ravel())
        cbar.ax.set_ylabel('Firing rate\n(spk/s)',
                           fontsize=fontSizeLabels, labelpad=-10)
        extraplots.set_ticks_fontsize(cbar.ax, fontSizeTicks)
        cbar.set_ticks([0, maxFR])
        cax.set_clim([0, maxFR])

        axTuningCurveHeatmap.set_yticks(intenTickLocations)
        axTuningCurveHeatmap.set_yticklabels(intensities[::-1])
        axTuningCurveHeatmap.set_xticks(freqTickLocations)
        freqLabels = ['{0:.1f}'.format(freq) for freq in freqs]
        axTuningCurveHeatmap.set_xticklabels(freqLabels)
        axTuningCurveHeatmap.set_xlabel('Frequency (kHz)',
                                        fontsize=fontSizeLabels)
        axTuningCurveHeatmap.set_ylabel('Intensity (dB SPL)',
                                        fontsize=fontSizeLabels)
        extraplots.set_ticks_fontsize(axTuningCurveHeatmap, fontSizeTicks)

        # ###############################################################################
    title = '[{5}]{0}, {1}, {2}um, T{3}c{4}, session ={6}'.format(
        dbRow['subject'], dbRow['date'], dbRow['depth'], tetnum, chanum,
        dbRow.name, sessions)
    plt.suptitle(title, fontsize=15, fontname="Times New Roman Bold")
    fig.set_size_inches([20, 10])
    # pathtoPng = os.path.join(outputDir, 'cellreport/')
    fig.savefig(outputDir + '[c#{0}] {1}_{2}_tetrode{3}_cluster{4}.png'.format(
        dbRow.name, dbRow['subject'], dbRow['depth'], tetnum, chanum))
    plt.clf()
    countreport += 1
    print("Report number {} generated!".format(countreport))
print("Total of {} reports have been generated".format(countreport))

plt.plot()
