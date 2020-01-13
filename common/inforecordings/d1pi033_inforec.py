from jaratoolbox import celldatabase
reload(celldatabase)

subject = 'd1pi033'
experiments=[]

exp0 = celldatabase.Experiment(subject, '2019-04-17', 'right_AudStr', info=['FacingPosterior', 'PosteriorDiD'])
experiments.append(exp0)

#50 noiseburst, 50 laser pulse, 40 laser train, 160 tuningTest, 1760 tc, 220 AM
#Used left speaker;laser (445 nm) set to 2.5 mW; Probe CEC2; Rig 2

exp0.laserCalibration = {
    '0.5':1.48,
    '1.0':1.93,
    '1.5':2.50,
    '2.0':3.10,
    '2.5':3.58,
    '3.0':4.50,
    '3.5':5.55,
    '4.0':6.75
}


#Tetrode 3 has reference; threshold set to 55mV
exp0.add_site(2900, tetrodes=[8])
exp0.add_session('13-45-51', None, 'noiseburst', 'am_tuning_curve')
exp0.add_session('13-48-40', None, 'lasertrain', 'am_tuning_curve')
exp0.add_session('13-50-39', None, 'laserpulse', 'am_tuning_curve')
exp0.add_session('13-52-22', 'a', 'tuningTest', 'am_tuning_curve')
exp0.add_session('14-00-16', 'b', 'tuningCurve(tc)', 'am_tuning_curve')
exp0.add_session('14-35-58', 'c', 'AM', 'am_tuning_curve')
#Sound response and tuning, but no real laser response

exp0.add_site(3000, tetrodes=[1,2,7,8])
exp0.add_session('15-02-13', None, 'noiseburst', 'am_tuning_curve')
exp0.add_session('15-06-34', None, 'lasertrain', 'am_tuning_curve')
exp0.add_session('15-11-01', None, 'laserpulse', 'am_tuning_curve')
exp0.add_session('15-12-34', 'd', 'tuningTest', 'am_tuning_curve')
exp0.add_session('15-20-26', 'e', 'tuningCurve(tc)', 'am_tuning_curve')
exp0.add_session('15-50-20', 'f', 'AM', 'am_tuning_curve')
#Sound and laser response on 2 and 8

exp0.add_site(3100, tetrodes=[1,2])
exp0.add_session('16-43-34', None, 'noiseburst', 'am_tuning_curve')
exp0.add_session('16-46-00', None, 'lasertrain', 'am_tuning_curve')
exp0.add_session('16-51-36', None, 'laserpulse', 'am_tuning_curve')
exp0.add_session('16-55-47', 'g', 'tuningTest', 'am_tuning_curve')
exp0.add_session('17-02-24', 'h', 'tuningCurve(tc)', 'am_tuning_curve')
exp0.add_session('17-31-50', 'i', 'AM', 'am_tuning_curve')
#Sound and laser responsive, though laser may have been phtoelectric effect

#Shank 4 broke off in brain, likely from adhereing to the bone it was close to
exp0.maxDepth = 3100


# exp1 = celldatabase.Experiment(subject, '2019-04-18', 'right_AudStr', info=['FacingPosterior', 'middleDiI'])
# experiments.append(exp1)
# #Shank 4 is now missing
#
# #50 noiseburst, 50 laser pulse, 40 laser train, 160 tuningTest, 1760 tc, 220 AM
# #Used left speaker;laser (445 nm) set to 2.5 mW; Probe CEC2; Rig 2
#
# exp1.laserCalibration = {
#     '0.5':1.40,
#     '1.0':1.87,
#     '1.5':2.45,
#     '2.0':3.00,
#     '2.5':3.60,
#     '3.0':4.45,
#     '3.5':5.40,
#     '4.0':6.55
# }

#Noticed saline was emptying very quickly. Possible hole has formed in glue of right well


exp2 = celldatabase.Experiment(subject, '2019-04-24', 'left_AudStr', info=['FacingPosterior', 'middleDiD'])
experiments.append(exp2)

#50 noiseburst, 50 laser pulse, 40 laser train, 160 tuningTest, 1760 tc, 220 AM
#Used right speaker;laser (445 nm) set to 2.5 mW; Probe CEC2; Rig 2
# No reference wire in as there is no room in the well

exp2.laserCalibration = {
    '0.5':1.45,
    '1.0':1.94,
    '1.5':2.45,
    '2.0':3.05,
    '2.5':3.55,
    '3.0':4.40,
    '3.5':5.35,
    '4.0':6.45
}


#Tetrode 5 has reference; threshold set to 55mV
#exp2.add_site(2800, tetrodes=[1,3,4,6])
#exp2.add_session('12-31-54', None, 'noiseburst', 'am_tuning_curve')

#Tetrode 3 has reference
exp2.add_site(2900, tetrodes=[1,2,4,5,6])
exp2.add_session('12-45-28', None, 'noiseburst', 'am_tuning_curve')
exp2.add_session('12-48-03', None, 'lasertrain', 'am_tuning_curve')
exp2.add_session('12-49-46', None, 'laserpulse', 'am_tuning_curve')
exp2.add_session('12-51-03', 'a', 'tuningTest', 'am_tuning_curve')
exp2.add_session('13-40-24', 'c', 'tuningCurve(tc)', 'am_tuning_curve')

exp2.add_site(3100, tetrodes=[5,6])
exp2.add_session('14-27-10', None, 'noiseburst', 'am_tuning_curve')
exp2.add_session('14-30-32', None, 'lasertrain', 'am_tuning_curve')
exp2.add_session('14-33-41', None, 'laserpulse', 'am_tuning_curve')
exp2.add_session('14-35-23', 'd', 'tuningTest', 'am_tuning_curve')
exp2.add_session('14-42-04', 'e', 'tuningCurve(tc)', 'am_tuning_curve')
exp2.add_session('15-17-52', 'f', 'AM', 'am_tuning_curve')

exp2.maxDepth = 3100


# exp3 = celldatabase.Experiment(subject, '2019-05-01', 'left_AudStr', info=['shank1Ant', 'middleDiI'])
# experiments.append(exp3)
#
# #50 noiseburst, 50 laser pulse, 40 laser train, 160 tuningTest, 1760 tc, 220 AM
# #Used right speaker;laser (445 nm) set to 2.5 mW; Probe CEC2; Rig 2
# # No reference wire in as there is no room in the well
#
# #looks like dye is on the optical fiber
# exp3.laserCalibration = {
#     '0.5':1.60,
#     '1.0':2.35,
#     '1.5':3.20,
#     '2.0':4.15,
#     '2.5':5.10,
#     '3.0':6.90,
#     '3.5':9.95,
#
# }
#
# #No way of fitting probe in