from random import randint
from lux_utils import load_lz4_pickle
from luxai2021.game.game import Game



import torch

import time
import pickle



from lux_actions import *
from lux_mcts import *
from lux_model import *



def run_selfplay_match(map_size: int, model: LuxModel):
  configs = {
    'seed': randint(20000000, 534024523),
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)
  game.start_replay_logging()
  
  mcts = MCTS(model)

  while not game.match_over():
    team_actions = mcts.run(game)
    
    considered_units_map = get_considered_units_map(game)
    env_actions = get_env_actions(game, team_actions, considered_units_map)

    game.run_turn_with_actions(env_actions)

    print('Turn:', game.state['turn'], 'Value:', mcts.root_cumul_value / mcts.root_num_visits)
    print(game.map.get_map_string())

  print('Winner: ' + str(game.get_winning_team()))


if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)




map_size = 12




model: LuxModel = torch.load('models/model_12.pt')
model.eval()




# Load input mean and standard deviation

mean_std = load_lz4_pickle('lux_mean_std.pickle.lz4')

model.input_mean = torch.Tensor(mean_std[0]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))
model.input_std = torch.Tensor(mean_std[1]) \
  .reshape((INPUT_COUNT, 1, 1)) \
  .broadcast_to((INPUT_COUNT, map_size, map_size))


  
while True:
  run_selfplay_match(map_size, model)