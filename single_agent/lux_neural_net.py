import torch
import torch.nn as nn
import torch.nn.functional as F




import lux_inputs
import lux_cell_actions
import lux_utils





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




class LuxNet(nn.Module):
  def __init__(self, width, height):
    super().__init__()




    # Settings

    self.width = width
    self.height = height
    self.num_pixels = width * height



    self.residual_num_channels = 128
    self.residual_num_blocks = 10



    self.value_num_channels = 1
    self.value_num_neurons = 32



    self.policy_num_channels = 32





    # Input layers

    self.in_conv = nn.Conv2d(lux_inputs.INPUT_COUNT, self.residual_num_channels, 3, padding=1, bias=False)
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

    self.policy_conv2 = nn.Conv2d(self.policy_num_channels, lux_cell_actions.CELL_ACTION_COUNT, 1)



    
    # Load input mean and standard deviation

    self.load_mean_std()
    
  


  def load_mean_std(self):
    mean_std = lux_utils.load_lz4_pickle('lux_mean_std.pickle.lz4')

    self.input_mean = torch.Tensor(mean_std[0]) \
      .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
      .broadcast_to((lux_inputs.INPUT_COUNT, self.width, self.height)).cuda()
    self.input_std = torch.Tensor(mean_std[1]) \
      .reshape((lux_inputs.INPUT_COUNT, 1, 1)) \
      .broadcast_to((lux_inputs.INPUT_COUNT, self.width, self.height)).cuda()
    

  

  def forward(self, x, with_sigmoid=True):
    # Standardize input

    x = (x - self.input_mean) / self.input_std



    
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
    if with_sigmoid:
      cell_action_probs = torch.sigmoid(cell_action_probs)




    return cell_action_probs, value