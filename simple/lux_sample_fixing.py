




from typing import List
import numpy as np

import pickle

import os

from numpy.random.mtrand import sample







from lux_utils import *




def fix_samples(dir_path):
  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = load_lz4_pickle(file_path)

    for i in range(len(samples)):
      sample_list = list(samples[i])

      sample_list[2] = np.array([sample_list[2]])

      samples[i] = sample_list

    samples = organize_samples(samples)

    save_lz4_pickle(samples, file_path)





def organize_samples(samples: List[tuple]):
  inputs = np.array([sample[0] for sample in samples])
  policy_targets = np.array([sample[1] for sample in samples])
  value_targets = np.array([sample[2] for sample in samples])

  return inputs, policy_targets, value_targets
  



fix_samples('samples/12')
fix_samples('samples/16')
fix_samples('samples/24')
fix_samples('samples/32')