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
 
exp = cellDB.Experiment(animalName='d1pi003', date ='2016-03-07', experimenter='lan', defaultParadigm='laser_tuning_curve') 


site1 = exp.add_site(depth=3360, tetrodes=[1,2,3,4,5,6,7,8]) #TT8 is ref
site1.add_session('14-04-43', None, sessionTypes['nb']) #amp=0.15
site1.add_session('14-06-59', None, sessionTypes['lp']) #power=1.5mW
site1.add_session('14-08-21', None, sessionTypes['lt']) #power=1.5mW
site1.add_session('14-09-54', 'a', sessionTypes['tc']) #2-40Hz chords, 50dB
site1.add_session('14-16-55', 'a', sessionTypes['2afc'], paradigm='2afc') 
#site1.add_session('14-56-08', None, sessionTypes['lt']) #power=1.5mW

sitefuncs.nick_lan_daily_report_v2(site1, 'site1', mainRasterInds=[0,1,2], mainTCind=3)
#sitefuncs.lan_2afc_ephys_plots(site1, 'site1', main2afcind=3, tetrodes=[1,2,3,5,8]) 
sitefuncs.lan_2afc_ephys_plots_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,2,3,4,5,6,7,8],trialLimit=[])
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=5, tetrodes=[3,5],trialLimit=[],choiceSide='both') 
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,2,4,5,6,7],trialLimit=[],choiceSide='left')
#sitefuncs.lan_2afc_ephys_plots_each_block_each_type(site1, 'site1', main2afcind=4, tetrodes=[1,2,4,5,6,7],trialLimit=[],choiceSide='right')
