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
 
exp = cellDB.Experiment(animalName='d1pi003', date ='2016-02-15', experimenter='lan', defaultParadigm='laser_tuning_curve') 


site1 = exp.add_site(depth=3080, tetrodes=[1,2,3,4,5,6,7]) #TT8 is ref
site1.add_session('14-55-38', None, sessionTypes['nb']) #amp=0.15
site1.add_session('14-58-06', None, sessionTypes['lp']) #power=1.5mW
site1.add_session('14-59-46', None, sessionTypes['lt']) #power=1.5mW
site1.add_session('15-01-25', 'a', sessionTypes['tc']) #2-40Hz chords, 50dB
site1.add_session('15-10-34', 'a', sessionTypes['2afc'], paradigm='2afc') 
site1.add_session('17-06-31', None, sessionTypes['lt']) #power=1.5mW

sitefuncs.nick_lan_daily_report(site1, 'site1', mainRasterInds=[0,1,2,5], mainTCind=3, mainSTRind=3)
#sitefuncs.lan_2afc_ephys_plots(site1, 'site1', main2afcind=3, tetrodes=[1,2,3,5,8]) 
sitefuncs.lan_2afc_ephys_plots_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,2,3,4,5,6,7],trialLimit=[])
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=5, tetrodes=[3,5],trialLimit=[],choiceSide='both') 
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,4,6,7],trialLimit=[],choiceSide='left')
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,4,6,7],trialLimit=[],choiceSide='right')
