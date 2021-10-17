




import numpy as np

import pickle

import os







from lux_utils import *






def fix_samples(dir_path):
  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = load_pickle(file_path)

    save_gzip_pickle(samples, file_path + '.gz')



fix_samples('samples/24')
fix_samples('samples/32')