from typing import Dict, Tuple



from lux_cell_actions import *
from lux_units import *
from luxai2021.game.actions import Action





def get_team_actions(game: Game, team: int, cell_action_probs, valid_cell_actions):
  # Make dictionary of cell action lists

  cell_actions: Dict[Tuple[int, int], List[Tuple[float, int]]] = {}

  for valid_cell_action in valid_cell_actions:
    cell_key = (valid_cell_action[1], valid_cell_action[2])

    if not cell_key in cell_actions:
      cell_actions[cell_key] = []

    cell_actions[cell_key].append((cell_action_probs[valid_cell_action], valid_cell_action[0]))




  # Sort each cell actions list by descending probability

  for cell_actions_list in cell_actions.values():
    cell_actions_list.sort(reverse=True)




  # Limit amount of actions

  while True:
    num_actions = 1

    aux_list_len = 0
    aux_list: List[int] = None



    for cell_actions_list in cell_actions.values():
      list_len = len(cell_actions_list)

      num_actions *= list_len

      if aux_list_len < list_len:
        aux_list_len = list_len
        aux_list = cell_actions_list



    if num_actions <= 32:
      break



    # Remove the worst unit action according to the action probabilities
  
    aux_list.pop()


  

  # Sort cell actions by descending max probabilty
  
  sorted_cell_actions = sorted(cell_actions.items(), key=lambda item: -max(item[1]))




  # Create list of actions

  return get_team_actions_aux(sorted_cell_actions)
  




def get_team_actions_aux(sorted_cell_actions: List[Tuple[Tuple[int, int], List[Tuple[float, int]]]],
depth: int = 0, team_action: list = [], team_actions: list = []):
  if depth >= len(sorted_cell_actions):
    team_actions.append(team_action.copy())
    
    return team_actions

  for cell_action in sorted_cell_actions[depth][1]:
    cell_key = sorted_cell_actions[depth][0]

    team_action[depth] = (cell_action, cell_key[0], cell_key[1])

    get_team_actions_aux(sorted_cell_actions, depth + 1, team_action, team_actions)

  return team_actions




def get_game_actions(action: List[tuple], game: Game, team: int,
considered_units_map: List[List[Unit]]) -> List[Action]:
  game_actions = []


  for cell_action in action:
    game_actions.append(get_game_action(cell_action, game, team, considered_units_map))


  return game_actions




def get_action_probs(actions: List[List[tuple]], cell_action_probs):
  action_probs = np.zeros(len(actions))



  for i in range(len(actions)):
    action = actions[i]

    action_prob = 1.0
    for cell_action in action:
      action_prob *= cell_action_probs[cell_action]

    action_probs[i] = action_prob



  return action_probs / np.sum(action_probs)