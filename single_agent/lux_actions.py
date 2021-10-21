from typing import Dict, List, Tuple

import numpy as np

import sortedcontainers





def get_team_actions(cell_action_probs, valid_cell_actions):
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



  
  sorted_cell_actions = sortedcontainers.SortedList(cell_actions.items(), key=lambda item: -len(item[1]))




  # Limit amount of actions

  num_actions = 1
  for _, cell_actions_list in sorted_cell_actions:
    num_actions *= len(cell_actions_list)



    
  while True:
    if num_actions <= 16:
      break



    # Remove the worst unit action according to the action probabilities

    cell_actions = sorted_cell_actions[0]

    sorted_cell_actions.remove(cell_actions)

    num_actions //= len(cell_actions[1])
    cell_actions[1].pop()
    num_actions *= len(cell_actions[1])

    sorted_cell_actions.add(cell_actions)
    


  
  # Sort cell actions by descending max probabilty
  
  sorted_cell_actions = sorted(list(sorted_cell_actions), key=lambda item: item[1][0])




  # Create list of actions

  team_action = [None] * len(sorted_cell_actions)
  team_actions = []

  create_team_actions_aux(sorted_cell_actions, team_action, team_actions)

  return team_actions
  




def create_team_actions_aux(sorted_cell_actions: List[Tuple[Tuple[int, int],
List[Tuple[float, int]]]], team_action: list, team_actions: list, depth: int = 0):
  if depth >= len(sorted_cell_actions):
    team_actions.append(team_action.copy())
    
    return

  for cell_action in sorted_cell_actions[depth][1]:
    cell_key = sorted_cell_actions[depth][0]

    team_action[depth] = (cell_action[1], cell_key[0], cell_key[1])

    create_team_actions_aux(sorted_cell_actions, team_action, team_actions, depth + 1)






def get_team_action_probs(team_actions: List[List[tuple]], cell_action_probs):
  team_action_probs = np.zeros(len(team_actions), np.float32)



  for i in range(len(team_actions)):
    team_action = team_actions[i]

    team_action_prob = 1.0
    for cell_action in team_action:
      team_action_prob *= cell_action_probs[cell_action]

    team_action_probs[i] = team_action_prob



  return team_action_probs / np.sum(team_action_probs)