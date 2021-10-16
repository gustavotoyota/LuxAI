




import numpy as np

import pickle

import os







from lux_utils import *






def fix_samples(dir_path):
  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = load_pickle(file_path)

    for i in range(len(samples)):
      sample = samples[i]

      action_probs = np.array(sample[1])
      action_probs[action_probs > 0.0] = 1.0

      sample = (sample[0], action_probs, sample[2])

      samples[i] = sample

    save_pickle(samples, file_path)



fix_samples('samples/24')