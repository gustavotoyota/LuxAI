from luxai2021.game.game import Game



import torch

import time
import pickle



from lux_actions import *
from lux_mcts import *
from lux_model import *



def selfplay(map_size: int, model: LuxModel):
  configs = {
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)
  
  mcts = MCTS(model)

  samples = []

  while not game.match_over():
    team_actions = mcts.run(game)
      
    target_value = mcts.root.cumul_value / mcts.root.num_visits
    
    considered_units_map = get_considered_units_map(game)

    for team in range(2):
      team_observation = get_team_observation(game, team, considered_units_map)

      target_policy = get_team_action_policy(game, team_actions[team])

      samples.append((team_observation, target_policy, target_value * (-team * 2 + 1)))

    env_actions = get_env_actions(game, team_actions, considered_units_map)

    game.run_turn_with_actions(env_actions)

    print('Turn:', game.state['turn'])
    print(game.map.get_map_string())

  print('Winner: ' + str(game.get_winning_team()))

  with open('samples/Samples ' + time.strftime('%Y.%m.%d - %H.%M.%S') + '.pickle', 'wb') as f:
    pickle.dump(samples, f)


if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)
  
while True:
  selfplay(12, LuxModel(12, 12))