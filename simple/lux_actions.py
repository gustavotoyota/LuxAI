from typing import Tuple



from lux_cell_actions import *
from lux_units import *





def get_action_list(game: Game, team: int, action_probs):
  valid_cell_actions = get_valid_cell_actions(game, team)




  # Make dictionary of cell action lists

  cell_actions: Dict[Tuple[int, int], List[Tuple[float, int]]] = {}

  for valid_cell_action in valid_cell_actions:
    cell_key = (valid_cell_action[1], valid_cell_action[2])

    if not cell_key in cell_actions:
      cell_actions[cell_key] = []

    cell_actions[cell_key].append((action_probs[valid_cell_action], valid_cell_action[0]))




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


  

  # Sort items by descending max probabilty
  
  sorted_cell_actions = sorted(cell_actions.items(), key=lambda item: -max(item[1]))




  # Create list of actions

  return create_action_list(sorted_cell_actions)
  




def create_action_list(sorted_cell_actions: List[Tuple[Tuple[int, int], List[Tuple[float, int]]]],
depth: int = 0, action: list = [], action_list: list = []):
  if depth >= len(sorted_cell_actions):
    action_list.append(action.copy())
    return action_list

  for cell_action in sorted_cell_actions[depth][1]:
    cell_key = sorted_cell_actions[depth][0]

    action[depth] = (cell_action, cell_key[0], cell_key[1])

    create_action_list(sorted_cell_actions, depth + 1, action, action_list)

  return action_list
  




def get_action_mask(game: Game, team: int):
  valid_cell_actions = get_valid_cell_actions(game, team)



  get_action_mask = np.zeros((UNIT_ACTION_COUNT, game.map.height, game.map.width), bool)

  for valid_cell_action in valid_cell_actions:
    get_action_mask[valid_cell_action] = True

  return get_action_mask