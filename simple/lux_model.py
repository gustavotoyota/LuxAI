import numpy as np
from torch.functional import Tensor




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
    self.residual_num_blocks = 8



    self.value_num_channels = 1
    self.value_num_neurons = 32



    self.policy_num_channels = 32





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

    self.policy_conv1 = nn.Conv2d(self.residual_num_channels, self.policy_num_channels, 1)
    self.policy_bn1 = nn.BatchNorm2d(self.policy_num_channels)

    self.policy_conv2 = nn.Conv2d(self.policy_num_channels, CELL_ACTION_COUNT, 1)
    

  

  def forward(self, x):
    # Input layers

    out = self.in_conv(x)
    out = self.in_bn(out)
    out = F.relu(out)




    # Residual blocks

    for residual_block in self.residual_blocks:
      out = residual_block(out)
      



    # Value head

    value = self.value_conv(out)
    value = self.value_bn(value)
    value = F.relu(value)

    value = value.view(-1, self.num_pixels * self.value_num_channels)
    value = self.value_fc1(value)
    value = F.relu(value)

    value = self.value_fc2(value)
    value = torch.tanh(value)




    # Policy head

    cell_action_probs = self.policy_conv1(out)
    cell_action_probs = self.policy_bn1(cell_action_probs)
    cell_action_probs = F.relu(cell_action_probs)

    cell_action_probs = self.policy_conv2(cell_action_probs)
    cell_action_probs = F.sigmoid(cell_action_probs)




    return cell_action_probs, value