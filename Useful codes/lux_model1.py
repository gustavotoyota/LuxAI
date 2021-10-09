import numpy as np




import torch.nn as nn
import torch.nn.functional as F




LUX_NUM_INPUTS = 19
LUX_NUM_ACTIONS = 12





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




class LuxResNet(nn.Module):
  def __init__(self, width, height):
    super().__init__()




    # Settings

    self.width = width
    self.height = height
    self.pixels = width * height




    self.residual_channels = 128
    self.residual_layers = 12



    self.value_channels = 2
    self.value_neurons = 64




    self.policy_channels = 4





    # Input

    self.in_conv = nn.Conv2d(LUX_NUM_INPUTS, self.residual_channels, 3, padding=1, bias=False)
    self.in_bn = nn.BatchNorm2d(self.residual_channels)




    # Residual

    self.residual_blocks = nn.ModuleList()
    for _ in range(self.residual_layers):
      self.residual_blocks.append(ResidualBlock(self.residual_channels, self.residual_channels))




    # Value

    self.value_conv = nn.Conv2d(self.residual_channels, self.value_channels, 1)
    self.value_bn = nn.BatchNorm2d(self.value_channels)

    self.value_fc1 = nn.Linear(self.pixels * self.value_channels, self.value_neurons)
    self.value_fc2 = nn.Linear(self.value_neurons, 1)




    # Policy

    self.policy_conv = nn.Conv2d(self.residual_channels, self.policy_channels, 1)
    self.policy_bn = nn.BatchNorm2d(self.policy_channels)

    self.policy_fc = nn.Linear(self.pixels * self.policy_channels, self.pixels * LUX_NUM_ACTIONS)
    

  

  def forward(self, x):
    # Input

    out = self.in_conv(x)
    out = self.in_bn(out)
    out = F.relu(out)




    # Residual blocks

    for block in self.residual_blocks:
      out = block(out)
      



    # Value

    value = self.value_conv(out)
    value = self.value_bn(value)
    value = F.relu(value)

    value = value.view(-1, self.pixels * self.value_channels)
    value = self.value_fc1(value)
    value = F.relu(value)

    value = self.value_fc2(value)
    value = F.tanh(value)




    # Policy

    policy = self.policy_conv(out)
    policy = self.policy_bn(policy)
    policy = F.relu(policy)

    policy = policy.view(-1, self.pixels * self.policy_channels)
    policy = self.policy_fc(value)
    policy = F.log_softmax(policy)




    return policy, value