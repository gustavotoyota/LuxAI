from typing import Dict

from lux_actions import get_env_actions, get_team_env_actions
from lux_inputs import get_team_observation
from lux_mcts import MCTS
from luxai2021.game.constants import LuxMatchConfigs_Default
from luxai2021.game.game import Game



from lux_model import LuxModel



def selfplay(map_size: int, model: LuxModel):
  configs = {
    'width': map_size,
    'height': map_size,
  }

  game = Game(configs)
  
  mcts = MCTS(game, model)

  while not game.match_over():
    team_actions = mcts.run()

    env_actions = get_env_actions(team_actions, game)

    game.run_turn_with_actions(env_actions)

    print(game.state['turn'])


selfplay(12, LuxModel(12, 12))