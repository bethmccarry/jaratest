from jaratoolbox.test.nick.database import cellDB
reload(cellDB)
from jaratest.lan.Ephys import sitefuncs_vlan as sitefuncs
reload(sitefuncs)


sessionTypes = {'nb':'noiseBurst',
                'lp':'laserPulse',
                'lt':'laserTrain',
                'tc':'tuningCurve',
                'bf':'bestFreq',
                '3p':'3mWpulse',
                '1p':'1mWpulse',
                '2afc':'2afc'}
 
exp = cellDB.Experiment(animalName='adap012', date ='2016-03-21', experimenter='lan', defaultParadigm='laser_tuning_curve') 


site1 = exp.add_site(depth=2900, tetrodes=[1,2,3,4,5,6,7])
site1.add_session('13-33-40', None, sessionTypes['nb']) #amp=0.1
site1.add_session('13-36-34', 'a', sessionTypes['tc']) #2-40Hz chords, 50dB
site1.add_session('13-43-09', 'a', sessionTypes['2afc'], paradigm='2afc')

#sitefuncs.nick_lan_daily_report_v2(site1, 'site1', mainRasterInds=[0], mainTCind=1)
#sitefuncs.lan_2afc_ephys_plots(site1, 'site1', main2afcind=3, tetrodes=[1,2,3,5,8]) 
sitefuncs.lan_2afc_ephys_plots_each_type(site1, 'site1', main2afcind=2, tetrodes=[1,2,3,4,5,6,7,8],trialLimit=[]) 
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=2, tetrodes=[1,2,3,4,5,6,7,8],trialLimit=[0,1145],choiceSide='both') 
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=2, tetrodes=[1,2,3,4,5,6,7,8],trialLimit=[],choiceSide='left')
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=2, tetrodes=[1,2,3,4,5,6,7,8],trialLimit=[],choiceSide='right')
