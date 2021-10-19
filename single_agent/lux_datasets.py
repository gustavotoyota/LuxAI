import os
import torch.utils.data
import torch.utils.data.dataset




import lux_utils




class LuxEpisodeDataset(torch.utils.data.dataset.Dataset):
  def __init__(self, file_path):
    self.file_path = file_path




  def __len__(self):
    samples = lux_utils.load_lz4_pickle(self.file_path)

    return samples.shape[0]




  def __getitem__(self, index):
    samples = lux_utils.load_lz4_pickle(self.file_path)

    return samples[index]




def get_dataset(map_size):
  episode_datasets = []

  dir_path = f'samples/{map_size}'

  for file_name in os.listdir(dir_path):
    file_path = f'{dir_path}/{file_name}'
    
    episode_datasets.append(LuxEpisodeDataset(file_path))

  return torch.utils.data.ConcatDataset(episode_datasets)