"""
Generate[1] and save[2] database with calculated stats and parameters that will be used in /
analysis. Optionally takes the arguments in the order of: script.py concat run_parameters mouse_name
"""
import os
import sys
import numpy as np
import pandas as pd
import studyparams
from scipy import stats
from scipy import signal
from jaratoolbox import behavioranalysis
from jaratoolbox import celldatabase
from jaratoolbox import ephyscore
from jaratoolbox import spikesorting
from jaratoolbox import spikesanalysis
from jaratoolbox import settings
from jaratoolbox import histologyanalysis
import database_generation_funcs as funcs


if sys.version_info[0] < 3:
    input_func = raw_input
elif sys.version_info[0] >= 3:
    input_func = input

SAVE = 1


def append_base_stats(cellDB, filename=''):
    """
    Calculate parameters to be used to filter cells in calculate_indices
    """

    # FILTERING DATAFRAME
    firstCells = cellDB.query(studyparams.FIRST_FLTRD_CELLS)  # isiViolations<0.02 and spikeShapeQuality>2.5

    for indIter, (indRow, dbRow) in enumerate(firstCells.iterrows()):

        sessions = dbRow['sessionType']
        oneCell = ephyscore.Cell(dbRow, useModifiedClusters=False)

        print("Now processing ", dbRow['subject'], dbRow['date'], dbRow['depth'], dbRow['tetrode'], dbRow['cluster'],
              indRow)
        print("Sessions tested in this cell are(is) ", sessions)

        # -------------- Noiseburst data calculations -------------------------
        session = 'noiseburst'
        try:
            noiseEphysData, noBData = oneCell.load(session)
        except IndexError:
            print('This cell does not contain a {} session'.format(session))
        else:
            baseRange = [-0.1, 0]  # if session != 'laserpulse' else [-0.05,-0.04]
            noiseEventOnsetTimes = noiseEphysData['events']['soundDetectorOn']
            noiseSpikeTimes = noiseEphysData['spikeTimes']
            nspkBaseNoise, nspkRespNoise = funcs.calculate_firing_rate(noiseEventOnsetTimes, noiseSpikeTimes, baseRange)
            respSpikeMean = np.mean(nspkRespNoise)

            # Significance calculations for the noiseburst
            try:
                zStats, pVals = stats.mannwhitneyu(nspkRespNoise, nspkBaseNoise, alternative='two-sided')
            except ValueError:  # All numbers identical will cause mann-whitney to fail, therefore p-value should be 1 as there is no difference
                zStats, pVals = [0, 1]

            # Adding noiseburst values to the dataframe
            cellDB.at[
                indRow, '{}_pVal'.format(session)] = pVals  # changed from at to loc via recommendation from pandas
            cellDB.at[indRow, '{}_zStat'.format(session)] = zStats
            cellDB.at[indRow, '{}_FR'.format(session)] = respSpikeMean  # mean firing rate

        # ------------ Laserpulse calculations --------------------------------
        session = 'laserpulse'
        try:
            pulseEphysData, noBData = oneCell.load(session)
        except IndexError:
            print('This cell does not contain a {} session'.format(session))
        else:
            baseRange = [-0.1, 0]  # if session != 'laserpulse' else [-0.05,-0.04]
            laserEventOnsetTimes = pulseEphysData['events']['laserOn']
            laserSpikeTimes = pulseEphysData['spikeTimes']
            nspkBaseLaser, nspkRespLaser = funcs.calculate_firing_rate(laserEventOnsetTimes, laserSpikeTimes, baseRange)
            respSpikeMean = np.mean(nspkRespLaser)
            baseSpikeMean = np.mean(nspkBaseLaser)
            changeFiring = respSpikeMean - baseSpikeMean

            # Significance calculations for the laserpulse
            try:
                zStats, pVals = stats.mannwhitneyu(nspkRespLaser, nspkBaseLaser, alternative='two-sided')
            except ValueError:  # All numbers identical will cause mann-whitney to fail
                zStats, pVals = [0, 1]

            # Adding laserpulse calculations to the dataframe
            cellDB.at[
                indRow, '{}_pVal'.format(session)] = pVals  # changed from at to loc via recommendation from pandas
            cellDB.at[indRow, '{}_zStat'.format(session)] = zStats
            cellDB.at[indRow, '{}_FR'.format(session)] = respSpikeMean  # mean firing rate
            cellDB.at[indRow, '{}_dFR'.format(session)] = changeFiring  # Difference between base and response firing rate

        # -------------- Tuning curve calculations ----------------------------
        session = 'tuningCurve'
        try:
            tuningEphysData, tuningBehavData = oneCell.load(session)
        except IndexError:
            print('This cell does not contain a {} session'.format(session))
        else:
            baseRange = [-0.1, 0]

            # Extracting information from ephys and behavior data to do calculations later with
            currentFreq = tuningBehavData['currentFreq']
            currentIntensity = tuningBehavData['currentIntensity']
            uniqFreq = np.unique(currentFreq)
            uniqueIntensity = np.unique(currentIntensity)
            tuningTrialsEachCond = behavioranalysis.find_trials_each_combination(currentFreq, uniqFreq, currentIntensity, uniqueIntensity)

            allIntenBase = np.array([])
            respSpikeMean = np.empty((len(uniqueIntensity), len(uniqFreq)))  # same as allIntenResp
            allIntenRespMedian = np.empty((len(uniqueIntensity), len(uniqFreq)))
            Rsquareds = []
            popts = []
            tuningSpikeTimes = tuningEphysData['spikeTimes']
            tuningEventOnsetTimes = tuningEphysData['events']['soundDetectorOn']
            tuningEventOnsetTimes = spikesanalysis.minimum_event_onset_diff(tuningEventOnsetTimes, minEventOnsetDiff=0.2)

            # Checking to see if the ephys data has one more trial than the behavior data and removing the last session if it does
            if len(tuningEventOnsetTimes) == (len(currentFreq) + 1):
                tuningEventOnsetTimes = tuningEventOnsetTimes[0:-1]
                print("Correcting ephys data to be same length as behavior data")
                toCalculate = True
            elif len(tuningEventOnsetTimes) == len(currentFreq):
                print("Data is already the same length")
                toCalculate = True
            else:
                print("Something is wrong with the length of these data")
                toCalculate = False
                # Instead of generating an error I made it just not calculate statistics. I should posisbly have it log all mice
                # and sites where it failed to calculate so someone can review later

        # -------------------- Start of calculations for the tuningCurve data -------------------------
            # The latency of the cell from the onset of the stim
            if toCalculate:
                tuningZStat, tuningPVal = \
                    funcs.sound_response_any_stimulus(tuningEventOnsetTimes, tuningSpikeTimes, tuningTrialsEachCond[:, :, -1],
                                                      timeRange=[0.0, 0.05], baseRange=baseRange)  # All trials at all frequencies at the highest intensity
                respLatency = funcs.calculate_latency(tuningEventOnsetTimes, currentFreq, uniqFreq, currentIntensity,
                                                      uniqueIntensity, tuningSpikeTimes, indRow)
            else:
                respLatency = np.nan
                tuningPVal = np.nan
                tuningZStat = np.nan

            for indInten, intensity in enumerate(uniqueIntensity):
                spks = np.array([])
                freqs = np.array([])
                pcovs = []
                ind10AboveButNone = []
                # ------------ start of frequency specific calculations -------------
                for indFreq, freq in enumerate(uniqFreq):
                    selectinds = np.flatnonzero((currentFreq == freq) & (currentIntensity == intensity))#.tolist()

                    nspkBase, nspkResp = funcs.calculate_firing_rate(tuningEventOnsetTimes, tuningSpikeTimes, baseRange,
                                                                     selectinds=selectinds)

                    spks = np.concatenate([spks, nspkResp.ravel()])
                    freqs = np.concatenate([freqs, np.ones(len(nspkResp.ravel())) * freq])
                    respSpikeMean[indInten, indFreq] = np.mean(nspkResp)
                    allIntenBase = np.concatenate([allIntenBase, nspkBase.ravel()])

                    # ------------------- Significance and fit calculations for tuning ----------------
                # TODO: Do we really need to calculate this for each frequency at each intensity?
                Rsquared, popt = funcs.calculate_fit(uniqFreq, allIntenBase, freqs, spks)

                Rsquareds.append(Rsquared)
                popts.append(popt)

            # ------------------------------ Intensity based calculations -------------------------
            # The reason why we are calculating bw10 here, it is to save the calculation time
            responseThreshold = funcs.calculate_response_threshold(0.2, allIntenBase, respSpikeMean)
            # [6] Find Frequency Response Area (FRA) unit: fra boolean set, yes or no, but it's originally a pair
            fra = respSpikeMean > responseThreshold
            # [6.5] get the intensity threshold
            intensityInd, freqInd = funcs.calculate_intensity_threshold_and_CF_indices(fra, respSpikeMean)
            if intensityInd is None:  # None of the intensities had anything
                bw10 = None
                lowerFreq = None
                upperFreq = None
                cf = None
                intensityThreshold = None
                fit_midpoint = None
            else:
                intensityThreshold = uniqueIntensity[intensityInd]
                cf = uniqFreq[freqInd]

                if toCalculate:
                    monoIndex, overallMaxSpikes = funcs.calculate_monotonicity_index(tuningEventOnsetTimes, currentFreq,
                                                                                     currentIntensity,
                                                                                     uniqueIntensity, tuningSpikeTimes, cf
                                                                                     )
                    onsetRate, sustainedRate, baseRate = funcs.calculate_onset_to_sustained_ratio(tuningEventOnsetTimes,
                                                                                                  tuningSpikeTimes,
                                                                                                  currentFreq,
                                                                                                  currentIntensity,
                                                                                                  cf, respLatency)
                else:
                    monoIndex = np.nan
                    overallMaxSpikes = np.nan
                    onsetRate = np.nan
                    sustainedRate = np.nan
                    baseRate = np.nan

                # [8] getting BW10 value, Bandwidth at 10dB above the neuron's sound intensity threshold(SIT)
                ind10Above = intensityInd + int(
                    10 / np.diff(uniqueIntensity)[0])  # How many inds to go above the threshold intensity ind
                lowerFreq, upperFreq, Rsquared10AboveSIT = funcs.calculate_BW10_params(ind10Above, popts, Rsquareds,
                                                                                       responseThreshold,
                                                                                       intensityThreshold)
                # print('lf:{},uf:{},R2:{}'.format(lowerFreq,upperFreq,Rsquared10AboveSIT))

                if (lowerFreq is not None) and (upperFreq is not None):
                    fitMidpoint = np.sqrt(lowerFreq * upperFreq)
                    bw10 = (upperFreq - lowerFreq) / cf

                else:
                    fitMidpoint = None
                    bw10 = None

                # Adding tuningCurve calculations to the dataframe to be saved later
                cellDB.at[indRow, 'thresholdFRA'] = intensityThreshold
                cellDB.at[indRow, 'cf'] = cf
                cellDB.at[indRow, 'lowerFreq'] = lowerFreq
                cellDB.at[indRow, 'upperFreq'] = upperFreq
                cellDB.at[indRow, 'rsquaredFit'] = Rsquared10AboveSIT
                cellDB.at[indRow, 'bw10'] = bw10
                cellDB.at[indRow, 'fit_midpoint'] = fitMidpoint
                cellDB.at[indRow, 'latency'] = respLatency
                cellDB.at[indRow, 'monotonicityIndex'] = monoIndex
                cellDB.at[indRow, 'onsetRate'] = onsetRate
                cellDB.at[indRow, 'sustainedRate'] = sustainedRate
                cellDB.at[indRow, 'baseRate'] = baseRate
                cellDB.at[indRow, 'tuning_pVal'] = tuningPVal
                cellDB.at[indRow, 'tuning_ZStat'] = tuningZStat

        # -------------------- am calculations ---------------------------
        session = 'am'
        try:
            amEphysData, amBehavData = oneCell.load(session)
        except IndexError:
            print('This cell does not contain a {} session'.format(session))
        else:
            significantFreqsArray = np.array([])

            # General variables for am calculations/plotting from ephys and behavior data
            amSpikeTimes = amEphysData['spikeTimes']
            amEventOnsetTimes = amEphysData['events']['soundDetectorOn']
            amCurrentFreq = amBehavData['currentFreq']
            amUniqFreq = np.unique(amCurrentFreq)
            amTimeRange = [-0.2, 0.7]
            amTrialsEachCond = behavioranalysis.find_trials_each_type(amCurrentFreq, amUniqFreq)

            if len(amCurrentFreq) != len(amEventOnsetTimes):
                amEventOnsetTimes = amEventOnsetTimes[:-1]
            if len(amCurrentFreq) != len(amEventOnsetTimes):
                print('Removing one does not align events and behavior. Skipping AM for cell')
            else:
                (amSpikeTimesFromEventOnset, amTrialIndexForEachSpike,
                 amIndexLimitsEachTrial) = \
                    spikesanalysis.eventlocked_spiketimes(amSpikeTimes,
                                                          amEventOnsetTimes,
                                                          amTimeRange)
                amBaseTime = [-0.6, -0.1]
                amOnsetTime = [0, 0.1]
                amResponseTime = [0, 0.5]

                # TODO: Should do some kind of post-hoc/correction on these such as
                # taking the p-value and dividing by the total number of comparisons done and using that as a threshold
                zStat, amPValue = \
                    funcs.sound_response_any_stimulus(amEventOnsetTimes, amSpikeTimes, amTrialsEachCond, amResponseTime, amBaseTime)
                cellDB.at[indRow, 'am_response_pVal'] = amPValue
                cellDB.at[indRow, 'am_response_ZStat'] = zStat

                # TODO: test calculations below
                # TODO: Should do some kind of post-hoc/correction on the alpha such as
                # taking the alpha and dividing by the total number of comparisons done (11) and using that as a threshold
                correctedPval = 0.05 / len(amUniqFreq)

                # Decide whether to make the next calculations based on 0.05 or on corrected value
                if amPValue > correctedPval:  # No response
                    print("No significant AM response, no synchronization will be calculated")
                elif amPValue < correctedPval:
                    amTimeRangeSync = [0.1, 0.5]  # Use this to cut out onset responses
                    (amSyncSpikeTimesFromEventOnset,
                     amSyncTrialIndexForEachSpike,
                     amSyncIndexLimitsEachTrial) = spikesanalysis.eventlocked_spiketimes(amSpikeTimes,
                                                                                         amEventOnsetTimes,
                                                                                         amTimeRangeSync)

                    allFreqSyncPVal, allFreqSyncZScore, allFreqVectorStrength, allFreqRal = \
                        funcs.calculate_am_significance_synchronization(amSyncSpikeTimesFromEventOnset,
                                                                        amSyncTrialIndexForEachSpike, amCurrentFreq,
                                                                        amUniqFreq)
                    amSyncPValue = np.min(allFreqSyncPVal)
                    amSyncZStat = np.max(allFreqSyncZScore)
                    cellDB.at[indRow, 'am_synchronization_pVal'] = amSyncPValue
                    cellDB.at[indRow, 'am_synchronization_ZStat'] = amSyncZStat

                    phaseDiscrimAccuracyDict = funcs.calculate_phase_discrim_accuracy(amSpikeTimes, amEventOnsetTimes,
                                                                                      amCurrentFreq, amUniqFreq)
                    for rate in amUniqFreq:
                        cellDB.at[indRow, 'phaseDiscrimAccuracy_{}Hz'.format(int(rate))] = \
                            phaseDiscrimAccuracyDict[int(rate)]

                    rateDiscrimAccuracy = funcs.calculate_rate_discrimination_accuracy(amSpikeTimes, amEventOnsetTimes,
                                                                                       amBaseTime, amResponseTime,
                                                                                       amCurrentFreq)
                    cellDB.at[indRow, 'rateDiscrimAccuracy'] = rateDiscrimAccuracy
                    if any(allFreqSyncPVal < 0.05):
                            sigPvals = np.array(allFreqSyncPVal) < 0.05
                            highestSyncInd = funcs.index_all_true_before(sigPvals)
                            cellDB.at[indRow, 'highestSync'] = amUniqFreq[allFreqSyncPVal < 0.05].max()
                            cellDB.at[indRow, 'highestUSync'] = amUniqFreq[highestSyncInd]
                            # print possibleFreq[pValThisCell<0.05].max()

                    else:
                        cellDB.at[indRow, 'highestSync'] = 0

                    if any(allFreqSyncPVal < correctedPval):
                        cellDB.at[indRow, 'highestSyncCorrected'] = amUniqFreq[allFreqSyncPVal < correctedPval].max()
                        highestSyncCorrected = amUniqFreq[allFreqSyncPVal < correctedPval].max()
                        freqsBelowThresh = allFreqSyncPVal < correctedPval
                        freqsBelowThresh = freqsBelowThresh.astype(int)
                        if len(significantFreqsArray) == 0:
                            significantFreqsArray = freqsBelowThresh
                        else:
                            # significantFreqsArray = np.concatenate([[significantFreqsArray], [freqsBelowThresh]])
                            significantFreqsArray = np.vstack((significantFreqsArray, freqsBelowThresh))
                    else:
                        cellDB.at[indRow, 'highestSyncCorrected'] = 0

    cellDB['cfOnsetivityIndex'] = \
        (cellDB['onsetRate'] - cellDB['sustainedRate']) / \
        (cellDB['sustainedRate'] + cellDB['onsetRate'])
    return cellDB


def calculate_indices(db, filename=''):
    """
    Filter cells that has a good fitting then separate D1 cells(laser responsive)\
    and non-D1 cells(non laser-responsive)
    """
    pass
    # bestCells = db.query('rsquaredFit>{}'.format(studyparams.R2_CUTOFF))
    #
    # return bestCells


def calculate_cell_locations(db, filename=''):
    # We do not have this function in this file as it relies on the allensdk
    # module which must be installed in a virtual environment
    # The function is located in database_cell_locations.py
    pass


def merge_dataframes(df1, df2):
    """
    Takes two dataframes and concatenates them so we can process one mouse at a time
    instead of having to regenerate an entire database when we add on a new mouse
    Args:
        df1 (list): List of strings containing full paths to dataframe(s).
        df2 (string): Full path to second dataframe to which the list of dataframes will be appended to the end of

    Returns:
        new_df (pandas.DataFrame): Two given dataframes appended through index value

    """
    df2 = celldatabase.load_hdf(df2)
    for frame in df1:
        try:
            appendedFrame = celldatabase.load_hdf(frame)
        except OSError:
            print("Mouse {} does not have an h5 file")
        else:
            df2 = pd.concat([df2, appendedFrame], axis=0, ignore_index=True, sort=False)

    return df2


if __name__ == "__main__":
    # Cluster your data
    CLUSTER_DATA = 0  # We don't generally run this code. We kept this for documentation

    # Choosing which mice to do calculations for
    # Check for script arguements to decide what calculations are done
    dbLocation = os.path.join(settings.FIGURES_DATA_PATH, studyparams.STUDY_NAME)
    if sys.argv[1:] != []:
        calc_stats = 0
        calc_locations = 0
        concat_mice = False
        arguments = sys.argv[1:]
        if arguments[0] == "concat":
            concat_mice = True
        else:
            if arguments[2] == 'all':
                d1mice = studyparams.ASTR_D1_CHR2_MICE
                dbpath = os.path.join(dbLocation, '{}.h5'.format('direct_and_indirect_cells'))
            else:
                d1mice = arguments[2]
                dbpath = os.path.join(dbLocation, '{}.h5'.format(d1mice))
                d1mice = [d1mice]
            print('d1mice = {}'.format(d1mice))
            # Run behavior can either be 'all', 'hist', or 'stats'
            runBehavior = arguments[1]
            print('Run behavior is {}'.format(runBehavior))
            if runBehavior == 'all':
                calc_stats = 1
                calc_locations = 1
            elif runBehavior == 'locations':
                calc_locations = 1
            elif runBehavior == 'stats':
                calc_stats = 1

    else:
        # Calculates everything for all mice in studyparams
        calc_stats = 1
        calc_locations = 1
        d1mice = studyparams.ASTR_D1_CHR2_MICE
        dbpath = os.path.join(dbLocation, '{}.h5'.format(studyparams.DATABASE_NAME))

    if CLUSTER_DATA:  # SPIKE SORTING
        # TODO: Need to loop through d1mice as it is a list
        inforecFile = os.path.join(settings.INFOREC_PATH, '{}_inforec.py'.format(d1mice))
        clusteringObj = spikesorting.ClusterInforec(inforecFile)
        clusteringObj.process_all_experiments()
        pass

    # Generate_cell_database_filters cells with the followings: isi < 0.05, spike quality > 2
    basicDB = celldatabase.generate_cell_database_from_subjects(d1mice)
    firstDB = basicDB
    d1DBFilename = os.path.join(settings.FIGURES_DATA_PATH, '{}_d1mice.h5'.format(studyparams.STUDY_NAME))
    # Create and save a database, computing first the base stats and then the indices
    if calc_stats:
        firstDB = append_base_stats(basicDB, filename=d1DBFilename)
        # bestCells = calculate_indices(firstDB, filename = d1DBFilename)
        histDB = firstDB
        celldatabase.save_hdf(histDB, os.path.join(dbLocation, '{}.h5'.format('temp_rescue_db')))
    if calc_locations:
        histDB = histologyanalysis.cell_locations(firstDB, brainAreaDict=studyparams.BRAIN_AREA_DICT)

    if concat_mice:
        first_mouse, *list_of_mice = studyparams.ASTR_D1_CHR2_MICE
        histDB = merge_dataframes(list_of_mice, first_mouse)
        dbpath = os.path.join(dbLocation, '{}.h5'.format('direct_and_indirect_cells'))

    if SAVE:
        if os.path.isdir(dbLocation):
            celldatabase.save_hdf(histDB, dbpath)
            print("SAVED DATAFRAME to {}".format(dbpath))
        elif not os.path.isdir(dbLocation):
            answer = input_func("Save folder is not present. Would you like to make the desired directory now? (y/n) ")
            if answer.upper() in ['Y', 'YES']:
                os.mkdir(dbLocation)
                celldatabase.save_hdf(histDB, dbpath)
                print("SAVED DATAFRAME to {}".format(dbpath))
                print(u"\U0001F4A9"*10)
