from lux_actions import get_env_actions
from lux_mcts import MCTS
from luxai2021.game.game import Game



import torch



from lux_model import LuxModel



def selfplay(map_size: int, model: LuxModel):
  configs = {
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)
  
  mcts = MCTS(model)

  while not game.match_over():
    team_actions = mcts.run(game)

    env_actions = get_env_actions(team_actions, game)

    game.run_turn_with_actions(env_actions)

    print(game.state['turn'])

  print('Winner: ' + str(game.get_winning_team()))


if torch.cuda.is_available():
  torch.set_default_tensor_type(torch.cuda.FloatTensor)
  
selfplay(12, LuxModel(12, 12))