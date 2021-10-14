from lux_actions import get_env_actions
from lux_mcts import MCTS
from luxai2021.game.game import Game



from lux_model import LuxModel



def selfplay(map_size: int, model: LuxModel):
  configs = {
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)
  
  mcts = MCTS(model)

  while not game.match_over():
    mcts.run(game)

    team_actions = mcts.get_best_actions()

    env_actions = get_env_actions(team_actions, game)

    game.run_turn_with_actions(env_actions)

    print(game.state['turn'])

  print('Winner: ' + str(game.get_winning_team()))


selfplay(12, LuxModel(12, 12))