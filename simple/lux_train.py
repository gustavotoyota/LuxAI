import math
from typing import List
from numpy.random.mtrand import sample




import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim.adam import Adam
from torch.optim.optimizer import Optimizer




from lux_model import *




def organize_samples(samples: List[tuple]):
  inputs = np.array([sample[0] for sample in samples])
  policy_targets = np.array([sample[1] for sample in samples])
  value_targets = np.array([sample[2] for sample in samples])

  return inputs, policy_targets, value_targets
  




def fit_minibatches(model: LuxModel, samples: tuple):
  minibatches = get_minibatches(samples)

  for minibatch in minibatches:
    fit_minibatch(model, optimizer, minibatch)





def fit_minibatch(model: LuxModel, optimizer: Optimizer, minibatch: tuple):
  log_probs, values = model(minibatch[0])

  policy_loss = F.nll_loss(log_probs, minibatch[1])
  value_loss = F.mse_loss(values, minibatch[2])

  loss = policy_loss + value_loss

  optimizer.zero_grad()
  loss.backward()
  optimizer.step()

  



def get_minibatches(samples: tuple, minibatch_size=256):
  num_samples = samples[0][0].shape[0]

  permutation = list(np.random.permutation(num_samples))

  inputs = samples[0][:, permutation]
  policy_targets = samples[1][:, permutation]
  value_targets = samples[2][:, permutation]

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






model = LuxModel(12, 12)

optimizer = Adam(model.parameters())

samples = []

while True:
  fit_minibatches(model, samples)

  torch.save(model, 'model.pt')