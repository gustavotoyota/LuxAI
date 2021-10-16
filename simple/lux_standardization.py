




import numpy as np

import pickle

import os







def get_mean_std(dir_path):
  samples = []

  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    with open(file_path, 'rb') as file:
      samples += pickle.load(file)



  observations = []
  for sample in samples:
    observations.append(sample[0])


  observations = np.array(observations)

  observation_mean = observations.mean((0, 2, 3))
  observation_std = observations.std((0, 2, 3))

  return observation_mean, observation_std



mean_12, std_12 = get_mean_std('samples/12')
mean_16, std_16 = get_mean_std('samples/16')
#mean_24, std_24 = get_mean_std('samples/24')
#mean_32, std_32 = get_mean_std('samples/32')

observation_mean = (mean_12 + mean_16) / 2.0
observation_std = (mean_12 + mean_16) / 2.0

observation_std[observation_std == 0.0] = 1.0

with open('lux_mean_std.pickle', 'wb') as file:
  pickle.dump((observation_mean, observation_std), file)