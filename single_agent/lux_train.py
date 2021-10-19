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





if __name__ == '__main__':
  map_size = 12




  # if torch.cuda.is_available():
  #   torch.set_default_tensor_type(torch.cuda.FloatTensor)





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




  if torch.cuda.is_available():
    model = model.cuda()
    observation_mean = observation_mean.cuda()
    observation_std = observation_std.cuda()




  # Create optimizer

  # optimizer = optim.Adam(model.parameters(), lr=3e-4, weight_decay=1e-5)
  # optimizer = optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-5)
  # optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
  optimizer = adabelief_pytorch.AdaBelief(
    model.parameters(), weight_decay=1e-4, print_change_log=False)




  # Data loader

  dataset = lux_datasets.get_dataset('samples', map_size)

  dataloader = torch.utils.data.dataloader.DataLoader(
    dataset=dataset,
    batch_size=256,
    shuffle=True,
    pin_memory=True,
    #num_workers=1,
  )




  avg_loss = 0.0

  while True:
    for minibatch in dataloader:
      standardized_input = (torch.Tensor(minibatch[0]).cuda() - observation_mean) / observation_std

      action_probs, values = model(standardized_input, False)
      
      policy_loss = F.binary_cross_entropy_with_logits(action_probs, torch.Tensor(minibatch[1]))
      value_loss = F.mse_loss(values, torch.Tensor(minibatch[2]))

      loss = policy_loss + value_loss

      avg_loss = avg_loss * 0.9 + loss.item() * 0.1

      print(avg_loss)

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()


    torch.save(model, f'{model_stem_path}_{round(avg_loss, 5)}.pt')