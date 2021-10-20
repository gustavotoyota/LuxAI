import os

import numpy as np



import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import torch.utils.data.dataloader

import adabelief_pytorch




import lux_datasets
import lux_model
import lux_utils
import lux_inputs




import hdf5plugin





if __name__ == '__main__':
  map_size = 12




  # Load input mean and standard deviation

  mean_std = lux_utils.load_lz4_pickle('lux_mean_std.pickle.lz4')

  observation_mean = torch.Tensor(mean_std[0]) \
    .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
    .broadcast_to((lux_inputs.INPUT_COUNT, map_size, map_size))
  observation_std = torch.Tensor(mean_std[1]) \
    .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
    .broadcast_to((lux_inputs.INPUT_COUNT, map_size, map_size))




  # Get model

  model_dir_path = 'models'
  model_stem_path = f'{model_dir_path}/model_{map_size}'
  model_file_path = f'{model_stem_path}.pt'

  if os.path.isfile(model_file_path):
    model = torch.load(model_file_path)
  else:
    model = lux_model.LuxModel(map_size, map_size)




  # Create optimizer

  optimizer = adabelief_pytorch.AdaBelief(
    model.parameters(),
    lr=1e-3,
    weight_decay=1e-4,
    print_change_log=False
  )




  # Data loader

  dataset = lux_datasets.HDF5Dataset(f'samples/{map_size}.h5')

  dataloader = torch.utils.data.dataloader.DataLoader(
    dataset=dataset,
    batch_size=128,
    shuffle=True,
    pin_memory=True,
  )




  # CUDA

  if torch.cuda.is_available():
    model = model.cuda()
    observation_mean = observation_mean.cuda()
    observation_std = observation_std.cuda()




  while True:
    for minibatch in dataloader:
      standardized_input = (torch.Tensor(minibatch[0]).cuda() - observation_mean) / observation_std

      action_probs, values = model(standardized_input, False)
      
      policy_loss = F.binary_cross_entropy_with_logits(action_probs, torch.Tensor(minibatch[1]).cuda())
      value_loss = F.mse_loss(values, torch.Tensor(minibatch[2]).cuda())

      loss = policy_loss + value_loss
      print('Loss:', loss.item())

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()

    torch.save(model, model_file_path)
    
    print('Finished batch')