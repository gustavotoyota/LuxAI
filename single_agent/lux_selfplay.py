from random import randint

import torch

import luxai2021.game.game



import lux_mcts
import lux_engine_actions
import lux_units
import lux_model



def run_selfplay_match(map_size: int, model: lux_model.LuxModel):
  configs = {
    'seed': randint(20000000, 534024523),
    'width': map_size,
    'height': map_size,
  }

  engine_game = luxai2021.game.game.Game(configs)
  engine_game.start_replay_logging()
  
  mcts = lux_mcts.MCTS(engine_game, model)

  while not engine_game.match_over():
    team_actions = mcts.run()
    
    considered_units_map = lux_units.get_considered_units_map(engine_game)
    engine_actions = lux_engine_actions.get_engine_actions(
      team_actions, engine_game, considered_units_map)

    engine_game.run_turn_with_actions(engine_actions)

    print('Turn:', engine_game.state['turn'], 'Value:', mcts.root_cumul_value / mcts.root_num_visits)
    print(engine_game.map.get_map_string())

  print('Winner: ' + str(engine_game.get_winning_team()))


if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)




map_size = 12




model: lux_model.LuxModel = torch.load('models/model_12.pt')
model.eval()


  
while True:
  run_selfplay_match(map_size, model)