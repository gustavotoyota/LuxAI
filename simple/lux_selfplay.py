from luxai2021.game.game import Game



import torch

import time
import pickle



from lux_actions import *
from lux_mcts import *
from lux_model import *



def run_selfplay_match(map_size: int, model: LuxModel):
  configs = {
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)

  game.a
  
  mcts = MCTS(model)

  while not game.match_over():
    team_actions = mcts.run(game)
    
    considered_units_map = get_considered_units_map(game)

    env_actions = get_env_actions(game, team_actions, considered_units_map)

    game.run_turn_with_actions(env_actions)

    print('Turn:', game.state['turn'])
    print(game.map.get_map_string())

  print('Winner: ' + str(game.get_winning_team()))


if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)
  
while True:
  run_selfplay_match(12, LuxModel(12, 12))