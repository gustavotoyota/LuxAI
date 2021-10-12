import numpy as np




import torch.nn as nn
import torch.nn.functional as F




from lux_inputs import *
from lux_cell_actions import *





class ResidualBlock(nn.Module):
  def __init__(self, in_channels, out_channels):
    super().__init__()

    self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False)
    self.bn1 = nn.BatchNorm2d(out_channels)

    self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False)
    self.bn2 = nn.BatchNorm2d(out_channels)

    

  def forward(self, x):
    identity = x

    out = self.conv1(x)
    out = self.bn1(out)
    
    out = F.relu(out)

    out = self.conv2(out)
    out = self.bn2(out)

    out += identity

    out = F.relu(out)

    return out




class LuxModel(nn.Module):
  def __init__(self, width, height):
    super().__init__()




    # Settings

    self.width = width
    self.height = height
    self.num_pixels = width * height



    self.residual_num_channels = 128
    self.residual_num_blocks = 12



    self.value_num_channels = 2
    self.value_num_neurons = 64



    self.policy_num_channels = 4





    # Input layers

    self.in_conv = nn.Conv2d(INPUT_COUNT, self.residual_num_channels, 3, padding=1, bias=False)
    self.in_bn = nn.BatchNorm2d(self.residual_num_channels)




    # Residual blocks

    self.residual_blocks = nn.ModuleList()
    for _ in range(self.residual_num_blocks):
      self.residual_blocks.append(ResidualBlock(self.residual_num_channels, self.residual_num_channels))




    # Value head

    self.value_conv = nn.Conv2d(self.residual_num_channels, self.value_num_channels, 1)
    self.value_bn = nn.BatchNorm2d(self.value_num_channels)

    self.value_fc1 = nn.Linear(self.num_pixels * self.value_num_channels, self.value_num_neurons)
    self.value_fc2 = nn.Linear(self.value_num_neurons, 1)




    # Policy head

    self.policy_conv = nn.Conv2d(self.residual_num_channels, self.policy_num_channels, 1)
    self.policy_bn = nn.BatchNorm2d(self.policy_num_channels)

    self.policy_fc = nn.Linear(self.num_pixels * self.policy_num_channels, self.num_pixels * UNIT_ACTION_COUNT)
    

  

  def forward(self, x):
    # Input layers

    out = self.in_conv(x)
    out = self.in_bn(out)
    out = F.relu(out)




    # Residual blocks

    for block in self.residual_blocks:
      out = block(out)
      



    # Value head

    value = self.value_conv(out)
    value = self.value_bn(value)
    value = F.relu(value)

    value = value.view(-1, self.num_pixels * self.value_num_channels)
    value = self.value_fc1(value)
    value = F.relu(value)

    value = self.value_fc2(value)
    value = F.tanh(value)




    # Policy head

    action_probs = self.policy_conv(out)
    action_probs = self.policy_bn(action_probs)
    action_probs = F.relu(action_probs)

    action_probs = action_probs.view(-1, self.num_pixels * self.policy_num_channels)
    action_probs = self.policy_fc(action_probs)
    action_probs = F.log_softmax(action_probs)

    action_probs = action_probs.view(-1, self.policy_num_channels, self.height, self.width)




    return action_probs, value