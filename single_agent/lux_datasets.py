import torch.utils.data
import torch.utils.data.dataset

import numpy as np



import h5py




class HDF5SingleSamplingDataset(torch.utils.data.dataset.Dataset):
  def __init__(self, file_path):
    self.hdf5_file = h5py.File(file_path, 'r')



  def __len__(self):
    return self.hdf5_file['inputs'].shape[0]



  def __getitem__(self, index):
    result = (
      self.hdf5_file['inputs'][index],
      self.hdf5_file['actions'][index],
      self.hdf5_file['values'][index]
    )

    return result




class HDF5BatchDataset(torch.utils.data.dataset.Dataset):
  def __init__(self, file_path):
    self.hdf5_file = h5py.File(file_path, 'r')



  def __len__(self):
    return self.hdf5_file['inputs'].shape[0]



  def __getitem__(self, index):
    index = sorted(index)

    result = (
      self.hdf5_file['inputs'][index],
      self.hdf5_file['actions'][index],
      self.hdf5_file['values'][index]
    )

    # original_indices = np.argsort(index)
    # current_indices = np.arange(0, len(index))

    # result[0][original_indices] = result[0][current_indices]
    # result[1][original_indices] = result[1][current_indices]
    # result[2][original_indices] = result[2][current_indices]

    return result