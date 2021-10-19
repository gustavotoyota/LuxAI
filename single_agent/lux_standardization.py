import numpy as np

import os



import lux_utils
import lux_datasets




weights = []
means = []
stds = []

def add_samples(dir_path):
  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = lux_utils.load_lz4_pickle(file_path)

    weights.append(np.array([samples[0].shape[0]], np.float32))
    means.append(samples[0].mean((0, 2, 3)))
    stds.append(samples[0].std((0, 2, 3)))

  print(f'Finished {dir_path}')

add_samples('samples/12')
add_samples('samples/16')
add_samples('samples/24')
add_samples('samples/32')

weights = np.array(weights, np.float32)
means = np.array(means, np.float32)
stds = np.array(stds, np.float32)

avg_mean = (means * weights).mean(axis=0) / weights.mean()
avg_std = (stds * weights).mean(axis=0) / weights.mean()

avg_std[avg_std == 0.0] = 1.0

lux_utils.save_lz4_pickle((avg_mean, avg_std), 'lux_mean_std.pickle.lz4')