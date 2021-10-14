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



    if num_actions <= max(16, len(cell_actions)):
      break



    # Remove the worst unit action according to the action probabilities
  
    aux_list.pop()


  

  # Sort cell actions by descending max probabilty
  
  sorted_cell_actions = sorted(list(cell_actions.items()), key=lambda item: item[1][0])




  # Create list of actions

  team_action = [None] * len(sorted_cell_actions)
  team_actions = []

  return get_team_actions_aux(sorted_cell_actions, team_action, team_actions)
  




def get_team_actions_aux(sorted_cell_actions: List[Tuple[Tuple[int, int], List[Tuple[float, int]]]],
team_action: list, team_actions: list, depth: int = 0):
  if depth >= len(sorted_cell_actions):
    team_actions.append(team_action.copy())
    
    return team_actions

  for cell_action in sorted_cell_actions[depth][1]:
    cell_key = sorted_cell_actions[depth][0]

    team_action[depth] = (cell_action[1], cell_key[0], cell_key[1])

    get_team_actions_aux(sorted_cell_actions, team_action, team_actions, depth + 1)

  return team_actions





def get_team_env_action(team_action: List[tuple], game: Game, team: int,
considered_units_map: List[List[Unit]]) -> List[Action]:
  team_env_action = []


  for cell_action in team_action:
    team_env_action.append(get_team_env_cell_action(cell_action, game, team, considered_units_map))


  return team_env_action




def get_team_env_actions(team_actions: List[List[tuple]], game: Game, team: int,
considered_units_map: List[List[Unit]]) -> List[List[Action]]:
  team_env_actions = []


  for team_action in team_actions:
    team_env_actions.append(get_team_env_cell_action(team_action, game, team, considered_units_map))


  return team_env_actions




def get_env_actions(team_actions: Tuple[list, list], game: Game) -> Tuple[List[Action], List[Action]]:
  env_actions = []


  for team in range(2):
    team_considered_units_map = get_team_considered_units_map(game, team)
    
    env_actions += get_team_env_actions(team_actions[team], game, team, team_considered_units_map)


  return env_actions




def get_team_action_probs(team_actions: List[List[tuple]], cell_action_probs):
  team_action_probs = np.zeros(len(team_actions))



  for i in range(len(team_actions)):
    team_action = team_actions[i]

    team_action_prob = 1.0
    for cell_action in team_action:
      team_action_prob *= cell_action_probs[cell_action]

    team_action_probs[i] = team_action_prob



  return team_action_probs / np.sum(team_action_probs)