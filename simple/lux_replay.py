import json
import os
from os import makedirs
import time
import pickle




from luxai2021.game.actions import Action
from luxai2021.game.constants import Constants



from lux_inputs import *
from lux_env_actions import *
from lux_cell_actions import *




def study_replay(file_path):
  with open(file_path) as f:
    replay = json.load(f)




  game = Game({'seed': replay['configuration']['seed']})

  team_histories = ([], [])

  #for step_obj in replay['steps'][1:]:
  while not game.match_over():
    step_obj = replay['steps'][game.state['turn'] + 1]

    env_actions = []
    
    considered_units_map = get_considered_units_map(game)

    for team in range(2):
      team_observation = get_team_observation(game, team, considered_units_map).numpy().squeeze()

      team_env_actions = []
      
      for action in step_obj[team]['action']:
        env_action = game.action_from_string(action, team)

        if not is_env_action_valid(env_action, game, env_actions):
          continue

        team_env_actions.append(env_action)
        env_actions.append(env_action)

      team_cell_actions = get_replay_team_cell_actions(game, team, team_env_actions, considered_units_map)

      team_histories[team].append((team_observation, team_cell_actions))

    game.run_turn_with_actions(env_actions)

    print('Turn:', game.state['turn'])
    # print(game.map.get_map_string())




  # if (game.state['turn'] == 359 and len(replay['steps']) == 361) \
  # or game.state['turn'] == len(replay['steps']) - 1:
  #   print('Success!')
  # else:
  #   print('Fail!')




  # Create samples

  samples = []

  winning_team = game.get_winning_team()

  for team in range(2):
    target_value = float(winning_team == team) * 2.0 - 1.0

    for experience in team_histories[team]:
      samples.append((experience[0], experience[1], target_value))




  # Save samples

  replay_id = os.path.splitext(os.path.basename(file_path))[0]

  if not os.path.isdir(f'samples/{game.map.width}'):
    makedirs(f'samples/{game.map.width}')

  with open(f'samples/{game.map.width}/{replay_id}.pickle', 'wb') as f:
    pickle.dump(samples, f)




def get_replay_team_cell_actions(game: Game, team: int,
team_env_actions: List[Action], considered_units_map: List[List[Unit]]):
  team_cell_actions = np.zeros((CELL_ACTION_COUNT, game.map.height, game.map.width))



  for team_env_action in team_env_actions:
    if team_env_action.action == Constants.ACTIONS.BUILD_WORKER:
      team_cell_actions[CELL_ACTION_BUILD_WORKER, team_env_action.y, team_env_action.x] = 1.0
    elif team_env_action.action == Constants.ACTIONS.BUILD_CART:
      team_cell_actions[CELL_ACTION_BUILD_CART, team_env_action.y, team_env_action.x] = 1.0
    elif team_env_action.action == Constants.ACTIONS.RESEARCH:
      team_cell_actions[CELL_ACTION_RESEARCH, team_env_action.y, team_env_action.x] = 1.0
    else:
      if team_env_action.action == Constants.ACTIONS.TRANSFER:
        unit: Unit = game.get_unit(team, team_env_action.source_id)
      else:
        unit: Unit = game.get_unit(team, team_env_action.unit_id)

      if unit != considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      if team_env_action.action == Constants.ACTIONS.MOVE:
        if team_env_action.direction == Constants.DIRECTIONS.CENTER:
          team_cell_actions[CELL_ACTION_DO_NOTHING, unit.pos.y, unit.pos.x] = 1.0
        elif team_env_action.direction == Constants.DIRECTIONS.NORTH:
          team_cell_actions[CELL_ACTION_MOVE_NORTH, unit.pos.y, unit.pos.x] = 1.0
        elif team_env_action.direction == Constants.DIRECTIONS.WEST:
          team_cell_actions[CELL_ACTION_MOVE_WEST, unit.pos.y, unit.pos.x] = 1.0
        elif team_env_action.direction == Constants.DIRECTIONS.SOUTH:
          team_cell_actions[CELL_ACTION_MOVE_SOUTH, unit.pos.y, unit.pos.x] = 1.0
        elif team_env_action.direction == Constants.DIRECTIONS.EAST:
          team_cell_actions[CELL_ACTION_MOVE_EAST, unit.pos.y, unit.pos.x] = 1.0
      elif team_env_action.action == Constants.ACTIONS.TRANSFER:
          team_cell_actions[CELL_ACTION_SMART_TRANSFER, unit.pos.y, unit.pos.x] = 1.0
      elif team_env_action.action == Constants.ACTIONS.BUILD_CITY:
          team_cell_actions[CELL_ACTION_BUILD_CITY, unit.pos.y, unit.pos.x] = 1.0
      elif team_env_action.action == Constants.ACTIONS.PILLAGE:
          team_cell_actions[CELL_ACTION_PILLAGE, unit.pos.y, unit.pos.x] = 1.0



  return team_cell_actions
  


for file_name in os.listdir('C:/Users/gusta/Desktop/Lux AI/Replays/Toad Brigade'):
  study_replay('C:/Users/gusta/Desktop/Lux AI/Replays/Toad Brigade/' + file_name)