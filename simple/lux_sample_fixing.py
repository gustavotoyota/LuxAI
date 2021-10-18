




from typing import List
import numpy as np

import os

from numpy.random.mtrand import sample







from lux_utils import *




def fix_samples(dir_path):
  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'

    samples = load_lz4_pickle(file_path)

    # Do something

    save_lz4_pickle(samples, file_path)
  



fix_samples('samples/12')
fix_samples('samples/16')
fix_samples('samples/24')
fix_samples('samples/32')