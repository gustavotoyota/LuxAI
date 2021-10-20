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
  map_size = 32




  # Load input mean and standard deviation

  mean_std = lux_utils.load_lz4_pickle('lux_mean_std.pickle.lz4')

  observation_mean = torch.Tensor(mean_std[0]) \
    .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
    .broadcast_to((lux_inputs.INPUT_COUNT, map_size, map_size))
  observation_std = torch.Tensor(mean_std[1]) \
    .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
    .broadcast_to((lux_inputs.INPUT_COUNT, map_size, map_size))




  # Get model

  model_dir_path = f'models'
  model_file_path = f'{model_dir_path}/model_{map_size}.pt'

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
    sampler=torch.utils.data.dataloader.BatchSampler(
      sampler=torch.utils.data.dataloader.RandomSampler(dataset),
      batch_size=256,
      drop_last=True,
    ),
    pin_memory=True,
    num_workers=2,
  )




  # CUDA

  if torch.cuda.is_available():
    model = model.cuda()
    observation_mean = observation_mean.cuda()
    observation_std = observation_std.cuda()




  while True:
    for minibatch in dataloader:
      observation = torch.Tensor(minibatch[0]).cuda().squeeze(0)
      policy_target = torch.Tensor(minibatch[1]).cuda().squeeze(0)
      value_target = torch.Tensor(minibatch[2]).cuda().squeeze(0)

      observation = (observation - observation_mean) / observation_std

      action_probs, values = model(observation, False)
      
      policy_loss = F.binary_cross_entropy_with_logits(action_probs, policy_target)
      value_loss = F.mse_loss(values, value_target)

      loss = policy_loss + value_loss
      print('Loss:', loss.item())

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()



    os.makedirs(model_dir_path, exist_ok=True)
    torch.save(model, model_file_path)


    
    print('Finished batch')