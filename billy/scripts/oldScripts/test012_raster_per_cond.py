'''
Show a raster for each condition
and maybe a PSTH?

For test055
20150228a_T3c11 9781 and 7821 Hz  (OK behavior)

For test017
20150301a_T4c3 reversing freq (but bad behavior, not reversing)


TO CHANGE:
- [DONE] Use settings instead of ephysRootDir, ephysRoot
- Don't import loadopenephys, use ephyscore directly
'''


from jaratoolbox import loadbehavior
from jaratoolbox import settings
from jaratoolbox import ephyscore
import os
import numpy as np
from jaratoolbox import loadopenephys
from jaratoolbox import spikesanalysis
from jaratoolbox import extraplots
import matplotlib.pyplot as plt

reload(spikesanalysis)
reload(extraplots)

SAMPLING_RATE=30000.0
soundTriggerChannel = 0 # channel 0 is the sound presentation, 1 is the trial
binWidth = 0.010 # Size of each bin in histogram in seconds

timeRange = [-0.2,0.8] # In seconds. Time range for rastor plot to plot spikes (around some event onset as 0)

ephysRootDir = settings.EPHYS_PATH

experimenter = 'santiago'
paradigm = '2afc'

CASE = 2
if CASE==1:
    import allcells_test055 as allcells
    cellID = allcells.cellDB.findcell('test055','20150228a',3,11)
elif CASE==2:
    import allcells_test017 as allcells
    cellID = allcells.cellDB.findcell('test017','20150309a',6,10)

oneCell = allcells.cellDB[cellID]

subject = oneCell.animalName
behavSession = oneCell.behavSession
ephysSession = oneCell.ephysSession
ephysRoot = os.path.join(ephysRootDir,subject)

# -- Load Behavior Data --
behaviorFilename = loadbehavior.path_to_behavior_data(subject,experimenter,paradigm,behavSession)
bdata = loadbehavior.BehaviorData(behaviorFilename)

# -- Load event data and convert event timestamps to ms --
ephysDir = os.path.join(ephysRoot, ephysSession)
eventFilename=os.path.join(ephysDir, 'all_channels.events')
events = loadopenephys.Events(eventFilename) # Load events data
eventTimes=np.array(events.timestamps)/SAMPLING_RATE #get array of timestamps for each event and convert to seconds by dividing by sampling rate (Hz). matches with eventID and 

soundOnsetEvents = (events.eventID==1) & (events.eventChannel==soundTriggerChannel)

# -- Load Spike Data From Certain Cluster --
spkData = ephyscore.CellData(oneCell)
spkTimeStamps = spkData.spikes.timestamps

eventOnsetTimes = eventTimes[soundOnsetEvents]

rightward = bdata['choice']==bdata.labels['choice']['right']
leftward = bdata['choice']==bdata.labels['choice']['left']
invalid = bdata['outcome']==bdata.labels['outcome']['invalid']
correct = bdata['outcome']==bdata.labels['outcome']['correct']

#oneFreq = bdata['targetFrequency']==9781
#oneFreq = bdata['targetFrequency']==7821
#oneFreq = bdata['targetFrequency']==12233
possibleFreq = np.unique(bdata['targetFrequency'])
oneFreq = bdata['targetFrequency'] == possibleFreq[1]

rightward = (bdata['choice']==bdata.labels['choice']['right']) & oneFreq
leftward = (bdata['choice']==bdata.labels['choice']['left']) & oneFreq

# Set this to 1 to plot only correct trials
if 0:
    rightward &= correct
    leftward &= correct

trialsEachCond = np.c_[invalid,leftward,rightward]; colorEachCond = ['0.75','g','r']
#trialsEachCond = np.c_[leftward,rightward]; colorEachCond = ['0.5','0.7','0']

(spikeTimesFromEventOnset,trialIndexForEachSpike,indexLimitsEachTrial) = \
    spikesanalysis.eventlocked_spiketimes(spkTimeStamps,eventOnsetTimes,timeRange)

#plot(spikeTimesFromEventOnset,trialIndexForEachSpike,'.')

plt.clf()
ax1 =  plt.subplot2grid((3,1), (0, 0), rowspan=2)
extraplots.raster_plot(spikeTimesFromEventOnset,indexLimitsEachTrial,timeRange,trialsEachCond=trialsEachCond,
                       colorEachCond=colorEachCond,fillWidth=None,labels=None)
#plt.yticks([0,trialsEachCond.sum()])
#ax1.set_xticklabels([])
plt.ylabel('Trials')

timeVec = np.arange(timeRange[0],timeRange[-1],binWidth)
spikeCountMat = spikesanalysis.spiketimes_to_spikecounts(spikeTimesFromEventOnset,indexLimitsEachTrial,timeVec)

smoothWinSize = 3
ax2 = plt.subplot2grid((3,1), (2, 0), sharex=ax1)

extraplots.plot_psth(spikeCountMat/binWidth,smoothWinSize,timeVec,trialsEachCond=trialsEachCond,
                     colorEachCond=colorEachCond,linestyle=None,linewidth=3,downsamplefactor=1)

plt.xlabel('Time from sound onset (s)')
plt.ylabel('Firing rate (spk/sec)')

plt.show()

