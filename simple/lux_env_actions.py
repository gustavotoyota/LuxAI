from typing import List
from luxai2021.game.actions import Action
from luxai2021.game.constants import Constants
from luxai2021.game.game import Game


def is_env_action_valid(env_action: Action, game: Game, env_actions: List[Action]):
  if not env_action:
    return False

  if env_action.action in {Constants.ACTIONS.BUILD_WORKER, Constants.ACTIONS.BUILD_CART, Constants.ACTIONS.RESEARCH}:
    if not game.map.get_cell(env_action.x, env_action.y).city_tile:
      return False
  else:
    if env_action.action == Constants.ACTIONS.TRANSFER:
      if not env_action.source_id in game.get_teams_units(env_action.team):
        return False
      
      if not env_action.destination_id in game.get_teams_units(env_action.team):
        return False
    else:
      if not env_action.unit_id in game.get_teams_units(env_action.team):
        return False

  if not env_action.is_valid(game, env_actions):
    return False

  return True