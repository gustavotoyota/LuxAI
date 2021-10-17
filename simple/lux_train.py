import math
from typing import List
from numpy.random.mtrand import sample

import os
import pickle




import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.adam import Adam
from torch.optim.optimizer import Optimizer




from lux_model import *
from lux_utils import *




def organize_samples(samples: List[tuple]):
  inputs = np.array([sample[0] for sample in samples])
  policy_targets = np.array([sample[1] for sample in samples])
  value_targets = np.array([sample[2] for sample in samples])

  return inputs, policy_targets, value_targets
  




def fit_minibatches(model: LuxModel, samples: tuple):
  minibatches = create_minibatches(samples)

  for minibatch in minibatches:
    fit_minibatch(model, optimizer, minibatch)





def fit_minibatch(model: LuxModel, optimizer: Optimizer, minibatch: tuple):
  standardized_input = (minibatch[0] - observation_mean) / observation_std
  standardized_input = standardized_input

  action_probs, values = model(standardized_input, True)
  
  policy_loss = F.binary_cross_entropy_with_logits(action_probs, minibatch[1])
  value_loss = F.mse_loss(values, minibatch[2].unsqueeze(1))

  loss = policy_loss + value_loss
  print(loss)

  optimizer.zero_grad()
  loss.backward()
  optimizer.step()

  



def create_minibatches(samples: tuple, minibatch_size=256):
  num_samples = samples[0].shape[0]

  permutation = list(np.random.permutation(num_samples))

  inputs = torch.Tensor(samples[0][permutation])
  policy_targets = torch.Tensor(samples[1][permutation])
  value_targets = torch.Tensor(samples[2][permutation])

  minibatches = []

  minibatch_start = 0

  while True:
    minibatch_end = minibatch_start + minibatch_size

    if minibatch_end >= num_samples:
      break

    minibatch = (
      inputs[minibatch_start:minibatch_end],
      policy_targets[minibatch_start:minibatch_end],
      value_targets[minibatch_start:minibatch_end],
    )

    minibatches.append(minibatch)

    minibatch_start = minibatch_end

  return minibatches






map_size = 12





if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)





# Get samples

samples = []

dir_path = f'samples/{map_size}'

for file_name in os.listdir(dir_path):
  file_path = f'{dir_path}/{file_name}'

  if not os.path.isfile(file_path):
    continue

  samples += load_gzip_pickle(file_path)

samples = organize_samples(samples)





mean_std = load_gzip_pickle('lux_mean_std.pickle.gz')

observation_mean = torch.Tensor(mean_std[0]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))
observation_std = torch.Tensor(mean_std[1]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))






if os.path.isfile('model.pt'):
  model = torch.load('model.pt')
else:
  model = LuxModel(map_size, map_size)

optimizer = Adam(model.parameters(), lr=1e-4)





while True:
  fit_minibatches(model, samples)

  torch.save(model, 'model.pt')