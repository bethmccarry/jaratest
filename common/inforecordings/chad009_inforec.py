from jaratoolbox import celldatabase

subject = 'chad009'
experiments = []

exp0 = celldatabase.Experiment(subject,
                               '2018-10-03',
                               brainarea='rightAC',
                               info='mid')
experiments.append(exp0)

exp0.add_site(894, tetrodes=[1,2,3,4,5,6,8]) #tetrode 7 has reference
#exp0.add_session('13-28-05', None, 'noiseburst', 'am_tuning_curve')


exp1 = celldatabase.Experiment(subject,
                               '2018-10-04',
                               brainarea='rightAC',
                               info='mid')
experiments.append(exp1)

exp1.add_site(1250, tetrodes=[1,2,3,4,8]) #tetrode 6 (channel 3) has reference
#exp1.add_site(1250, tetrodes=[2]) #Limit just to TT2 for cluster color plotting
exp1.add_session('13-49-05', None, 'noiseburst', 'am_tuning_curve') #Good sound responses on TT2


exp0 = celldatabase.Experiment('chad009', '18-11-15', 'right_AC', info=['midMedial' 'facingAnterior' 'soundLeft'])
experiments.append(exp0)

exp0.add_site(1100, tetrodes=[1,2,3,4,5,7,8])
exp0.add_session('12-48-25', 'a', 'noiseburst', 'am_tuning_curve')

exp0.add_site(1150, tetrodes=[1,2,3,4,5,7,8])
exp0.add_session('12-50-37', 'b', 'noiseburst', 'am_tuning_curve')

