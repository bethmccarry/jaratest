from jaratoolbox import celldatabase

subject = 'chad016'
experiments=[]

exp0 = celldatabase.Experiment(subject, '2019-08-29', 'left AC', info=['farLateral' 'facingLeft' 'soundRight'])
experiments.append(exp0)
# Using probe D65D

exp0.add_site(900, tetrodes=[1,2,4,7,8])

exp0.add_session('13-36-25', None, 'noiseburst', 'am_tuning_curve')
# Behavior suffix 'a'
# Reference set to 3 (Tetrode 6, channel 1)

exp0.add_session('13-48-05', 'b', 'tc', 'am_tuning_curve')
# Reference set to 3 (Tetrode 6, channel 1)

exp0.add_session('14-05-54', 'c', 'ascending', 'threetones_sequence')
# Reference set to 3 (Tetrode 6, channel 1)
# Frequencies chosen based on tetrode 2,4,7,8.

exp0.add_session('14-15-45', 'd', 'descending', 'threetones_sequence')
# Reference set to 3 (Tetrode 6, channel 1)
# Frequencies chosen based on tetrode 2,4,7,8.

exp0.add_site(975, tetrodes=[1,2,3,4,5,6,7,8])

exp0.add_session('15-05-21', None, 'noiseburst', 'am_tuning_curve')
# Behavior suffix 'e'
# Reference set to 18 (Tetrode 1, channel 1)


exp0.add_site(1051, tetrodes=[2,4,6,7,8])

exp0.add_session('15-16-43', None, 'noiseburst', 'am_tuning_curve')
# Behavior suffix 'f'
# Reference set to 18 (Tetrode 1, channel 1)

exp0.add_session('15-21-27', 'g', 'tc', 'am_tuning_curve')
# Reference set to 18 (Tetrode 1, channel 1)

exp0.add_session('15-38-03', 'h', 'ascending', 'threetones_sequence')
# Reference set to 3 (Tetrode 6, channel 1)
# Frequencies chosen based on tetrode 2,4,6,7,8.

exp0.add_session('15-48-40', 'i', 'descending', 'threetones_sequence')
# Reference set to 3 (Tetrode 6, channel 1)
# Frequencies chosen based on tetrode 2,4,6,7,8.

exp0.add_site(1155, tetrodes=[2,4,6,7,8])

exp0.add_session('16-16-50', None, 'noiseburst', 'am_tuning_curve')
# Behavior suffix 'j'
# Reference set to 25 (Tetrode 3, channel 1)

exp0.add_session('16-23-46', 'k', 'tc', 'am_tuning_curve')
# Reference set to 25 (Tetrode 3, channel 1)

exp0.add_session('16-39-49', 'l', 'ascending', 'threetones_sequence')
# Reference set to 25 (Tetrode 3, channel 1)
# Frequencies chosen based on tetrode 2,6,8.

exp0.add_session('16-49-09', 'm', 'descending', 'threetones_sequence')
# Reference set to 25 (Tetrode 3, channel 1)
# Frequencies chosen based on tetrode 2,6,8.

exp0.maxDepth = 1155





