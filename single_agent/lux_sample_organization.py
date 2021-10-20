from typing import List

import numpy as np

import os




import h5py
import hdf5plugin



import lux_utils



def organize_samples(dir_path):
  hdf5_file = h5py.File(f'{dir_path}.h5', 'w')

  hdf5_datasets = []

  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = lux_utils.load_lz4_pickle(file_path)

    if not hdf5_datasets:
      hdf5_datasets.append(hdf5_file.create_dataset('inputs', data=samples[0],
        maxshape=(None, None, None, None), **hdf5plugin.LZ4()))
      hdf5_datasets.append(hdf5_file.create_dataset('actions', data=samples[1],
        maxshape=(None, None, None, None), **hdf5plugin.LZ4()))
      hdf5_datasets.append(hdf5_file.create_dataset('values', data=samples[2],
        maxshape=(None, None), **hdf5plugin.LZ4()))
    else:
      for i in range(3):
        hdf5_datasets[i].resize((hdf5_datasets[i].shape[0] + samples[i].shape[0]), axis=0)
        hdf5_datasets[i][-samples[i].shape[0]:] = samples[i]
  



organize_samples('samples/12')
organize_samples('samples/16')
organize_samples('samples/24')
organize_samples('samples/32')