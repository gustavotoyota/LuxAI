from typing import Tuple
from scipy.special import softmax



from lux_valid_cell_actions import *
from lux_units import *





def get_action_list(game: Game, team: int):
  valid_cell_actions = get_valid_cell_actions(game, team)




  # Make dictionary of unit action lists

  cell_action_list_dict: Dict[Tuple[int, int], List[int]] = {}

  for valid_cell_action in valid_cell_actions:
    unit_key = (valid_cell_action[1], valid_cell_action[2])

    if not unit_key in cell_action_list_dict:
      cell_action_list_dict[unit_key] = []

    cell_action_list_dict[unit_key].append(valid_cell_action[0])




  # Limit amount of actions

  while True:
    num_actions = 1

    aux_list_len = 0
    aux_list: List[int] = None



    for _, cell_action_list in cell_action_list_dict:
      list_len = len(cell_action_list)

      num_actions *= list_len

      if aux_list_len < list_len:
        aux_list_len = list_len
        aux_list = cell_action_list



    if num_actions <= 32:
      break



    # Remove the worst unit action according to the action probabilities
  
    aux_list.remove(min(aux_list))




  # Create list of actions

  return 
  



def get_action_list_aux():


  

  





def get_action_mask(game: Game, team: int):
  valid_cell_actions = get_valid_cell_actions(game, team)



  get_action_mask = np.zeros((UNIT_ACTION_COUNT, game.map.height, game.map.width), bool)

  for valid_cell_action in valid_cell_actions:
    get_action_mask[valid_cell_action] = True

  return get_action_mask