import os
import numpy as np
from jaratoolbox import settings
from jaratoolbox import behavioranalysis
from jaratoolbox import loadbehavior
from jaratoolbox import extraplots
from matplotlib import pyplot as plt

'''
Behavior steps:
0: Sides direct AM
1: Direct AM
2: Next correct AM
3: If correct AM
4: AM psychometric
5: If correct Tones
6: Tones psychometric
7: If correct Mixed tones
8: Mixed tones psychometric
9: Ready for experiment
'''

ytickLabels = ['SD AM', 'D AM', 'NC AM', 'IC AM', 'P AM', 'IC F', 'P F', 'IC M', 'P M', 'R']
ytickInds = range(len(ytickLabels))


class BehavStepError(Exception):
    '''
    Raised if there is an error we can't account for in the behavior step program.
    '''
    pass

class NoSoundTypeMode(Exception):
    '''
    Raised if there is no soundTypeMode
    '''
    pass

def behavior_step(sessionData, readyThresh=0.75):
    '''
    Calculate the training step given a bdata object
    '''
    outcomeMode = sessionData.labels['outcomeMode'][sessionData['outcomeMode'][0]]
    try:
        soundTypeMode = sessionData.labels['soundTypeMode'][sessionData['soundTypeMode'][0]]
    except KeyError as e:
        #Some initial sessions were run with a diff. paradigm (should only be SD)
        if outcomeMode in ['sides_direct', 'direct']:
            step = 0
            return step, np.nan
        else:
            print e
            raise NoSoundTypeMode('No soundTypeMode outside of sides/direct')

    psycurveMode = sessionData.labels['psycurveMode'][sessionData['psycurveMode'][0]]
    if outcomeMode == 'sides_direct':
        assert soundTypeMode == 'amp_mod'
        step = 0
    elif outcomeMode == 'direct':
        assert soundTypeMode == 'amp_mod'
        step = 1
    elif outcomeMode == 'on_next_correct':
        assert soundTypeMode == 'amp_mod'
        step = 2
    elif outcomeMode == 'only_if_correct':
        if soundTypeMode == 'amp_mod':
            if psycurveMode == 'off':
                step=3
            elif psycurveMode == 'uniform':
                step=4
            else:
                raise BehavStepError('Psycurve mode not listed: {}'.format(psycurveMode))
        elif soundTypeMode in ['tones', 'chords']:
            if psycurveMode == 'off':
                step=5
            elif psycurveMode == 'uniform':
                step=6
            else:
                raise BehavStepError('Psycurve mode not listed: {}'.format(psycurveMode))
        elif soundTypeMode in ['mixed_tones', 'mixed_chords']:
            if psycurveMode == 'off':
                step=7
            elif psycurveMode == 'uniform':
                # NOTE: percentCorrect now calculated for all sessions and returned
                # if percentCorrect > readyThresh:
                #     step = 9
                # else:
                step = 8
            else:
                raise BehavStepError('Psycurve mode not listed: {}'.format(psycurveMode))
        else:
            raise BehavStepError('Sound mode not listed: {}'.format(soundTypeMode))
    else:
        raise BehavStepError('Outcome mode not listed: {}'.format(outcomeMode))

    #Now we need to calculate performance to see if the animal is
    #starting, or is ready to begin expeiments.
    correctTrials = sessionData['outcome'] == sessionData.labels['outcome']['correct']
    validCorrect = correctTrials[sessionData['valid']]
    percentCorrect = sum(validCorrect)/float(len(validCorrect))
    return step, percentCorrect

# subjects = ['amod007', 'amod008', 'amod009', 'amod010', 'amod011', 'amod012', 'amod013', 'amod014']
# subjects = ['amod007']

#Amod animals 002 through 014
subjects = ['amod{:03d}'.format(i) for i in range(7, 15)]

stepArrays = []
trialNumArrays = []
performanceArrays = []
for subject in subjects:
    dataDir = os.path.join(settings.BEHAVIOR_PATH, subject)
    sessions = sorted(os.listdir(dataDir))
    trainingSteps = np.empty(len(sessions))
    trialStartEachSession = np.empty(len(sessions))
    percentCorrect = np.empty(len(sessions))
    trials = 0
    highestStep = 0
    for indSession, sessionFn in enumerate(sessions):
        sessionFullPath = os.path.join(dataDir, sessionFn)
        try:
            bdata = loadbehavior.BehaviorData(sessionFullPath)
        except KeyError:
            print "Key Error with session: {}".format(sessionFullPath)

        try:
            step, percentCorrectThisSession = behavior_step(bdata)
        except NoSoundTypeMode as e: #Using the animal for other paradigms throws key errors
            if highestStep==8: #If we are at the end of the animal's career
                step, percentCorrectThisSession = -1, 0 #Animal was being used for different things
            else:
                print e
                raise KeyError('Problem before end of animal career')

        #Keep track of the highest step the animal has acheived.
        if step > highestStep:
            highestStep = step

        trialStartEachSession[indSession] = trials
        trainingSteps[indSession] = step
        percentCorrect[indSession] = percentCorrectThisSession
        trials += len(bdata['valid']) #Using total length, not just valid trials
    stepArrays.append(trainingSteps)
    trialNumArrays.append(trialStartEachSession)
    performanceArrays.append(percentCorrect)

saveFn = '/home/nick/data/dissertation_amod/sessions_per_step.npz'
np.savez(saveFn, subjects=subjects,
         stepArrays=stepArrays,
         trialNumArrays=trialNumArrays,
         performanceArrays=performanceArrays)

# plt.clf()
# for indArray, stepArray in enumerate(stepArrays):
#     # changePointsToShow = np.concatenate([np.array([True]), np.diff(stepArray)==1])
#     changePointsToShow = find_change_points(stepArray)
#     plt.plot(trialNumArrays[indArray][changePointsToShow],
#              stepArray[changePointsToShow], '-o')
# ax = plt.gca()
# ax.set_yticks(ytickInds)
# ax.set_yticklabels(ytickLabels)
# ax.set_xlabel('Number of trials')
# plt.show()
