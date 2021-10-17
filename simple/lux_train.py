from typing import List
from numpy.random.mtrand import sample

import os




import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim




from lux_model import *
from lux_utils import *
  




def fit_minibatches(model: LuxModel, samples: tuple):
  minibatches = create_minibatches(samples)

  for minibatch in minibatches:
    fit_minibatch(model, optimizer, minibatch)





def fit_minibatch(model: LuxModel, optimizer: optim.Optimizer, minibatch: tuple):
  standardized_input = (torch.Tensor(minibatch[0]) - observation_mean) / observation_std

  action_probs, values = model(standardized_input, False)
  
  policy_loss = F.binary_cross_entropy_with_logits(action_probs, torch.Tensor(minibatch[1]))
  value_loss = F.mse_loss(values, torch.Tensor(minibatch[2]))

  loss = policy_loss + value_loss
  print(loss)

  optimizer.zero_grad()
  loss.backward()
  optimizer.step()

  



def create_minibatches(samples: tuple, minibatch_size=256):
  num_samples = samples[0].shape[0]

  permutation = list(np.random.permutation(num_samples))

  inputs = samples[0][permutation]
  policy_targets = samples[1][permutation]
  value_targets = samples[2][permutation]

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






map_size = 16





if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)





# Get samples

samples = [[], [], []]

dir_path = f'samples/{map_size}'

for file_name in os.listdir(dir_path):
  file_path = f'{dir_path}/{file_name}'

  if not os.path.isfile(file_path):
    continue
  
  samples_aux = load_lz4_pickle(file_path)
  for i in range(3):
    samples[i].append(samples_aux[i])

for i in range(3):
  samples[i] = np.concatenate(samples[i])





mean_std = load_pickle('lux_mean_std.pickle')

observation_mean = torch.Tensor(mean_std[0]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))
observation_std = torch.Tensor(mean_std[1]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))






if os.path.isfile(f'models/model_{map_size}.pt'):
  model = torch.load(f'models/model_{map_size}.pt')
else:
  model = LuxModel(map_size, map_size)

optimizer = optim.Adam(model.parameters(), lr=1e-4)
#optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)





while True:
  fit_minibatches(model, samples)

  torch.save(model, 'model.pt')