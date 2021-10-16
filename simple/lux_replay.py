import json
import os
import time
import pickle




from luxai2021.game.actions import Action
from luxai2021.game.constants import Constants



import lux.game



from lux_inputs import *
from lux_env_actions import *
from lux_cell_actions import *




def analyze_replay(file_path):
  replay_id = os.path.splitext(os.path.basename(file_path))[0]

  print('Replay:', replay_id)
  



  # Load replay object

  with open(file_path) as f:
    replay_obj = json.load(f)




  env_game = Game({'seed': replay_obj['configuration']['seed']})




  replay_game: lux.game.Game = lux.game.Game()
  replay_game._initialize(replay_obj['steps'][0][0]['observation']['updates'])
  replay_game._update(replay_obj['steps'][0][0]['observation']['updates'])




  team_histories = ([], [])

  error = None

  try:
    for step_obj in replay_obj['steps'][1:]:
      # Update replay game
      
      step_obj = replay_obj['steps'][env_game.state['turn'] + 1]
      replay_game._update(step_obj[0]['observation']['updates'])




      # Get actions

      env_actions = []
      
      considered_units_map = get_considered_units_map(env_game)

      for team in range(2):
        team_observation = get_team_observation(env_game, team, considered_units_map).numpy().squeeze()

        team_env_actions = []

        if not step_obj[team]['action']:
          continue
        
        for action in step_obj[team]['action']:
          env_action = env_game.action_from_string(action, team)

          if not is_env_action_valid(env_action, env_game, env_actions):
            continue

          team_env_actions.append(env_action)
          env_actions.append(env_action)

        team_cell_actions = get_replay_team_cell_actions(env_game, team_env_actions, considered_units_map)

        team_histories[team].append((team_observation, team_cell_actions))




      # Execute actions

      env_game.run_turn_with_actions(env_actions)




      # Validate game state

      if not replay_validate_game_state(env_game, replay_game):
        error = True
        break

      


      print('Turn:', env_game.state['turn'])
      # print(game.map.get_map_string())
  except Exception as exception:
    error = exception
    print(exception)




  # Validate and move replay

  dir_path = os.path.dirname(file_path)

  if error or not env_game.match_over() or \
  (env_game.state['turn'] != len(replay_obj['steps']) - 1 and \
  not (env_game.state['turn'] == 359 and len(replay_obj['steps']) == 361)):
    os.makedirs(f'{dir_path}/failures', exist_ok=True)
    os.replace(file_path, f'{dir_path}/failures/{file_name}')

    print('Fail!')

    return
  
  os.makedirs(f'{dir_path}/successes', exist_ok=True)
  os.replace(file_path, f'{dir_path}/successes/{file_name}')

  print('Success!')




  # Organize samples

  samples = []

  winning_team = env_game.get_winning_team()

  for team in range(2):
    target_value = float(winning_team == team) * 2.0 - 1.0

    for experience in team_histories[team]:
      samples.append((experience[0], experience[1], target_value))




  # Save samples

  dir_path = f'samples/{env_game.map.width}'

  os.makedirs(dir_path, exist_ok=True)

  with open(f'{dir_path}/{replay_id}.pickle', 'wb') as f:
    pickle.dump(samples, f)





def replay_validate_game_state(env_game: Game, replay_game: lux.game.Game):
  replay_units_map = np.zeros((env_game.map.height, env_game.map.width), np.int32)

  for team in range(2):
    for unit in replay_game.players[team].units:
      replay_units_map[unit.pos.y][unit.pos.x] += 1




  for y in range(env_game.map.height):
    for x in range(env_game.map.width):
      env_cell = env_game.map.get_cell(x, y)
      replay_cell = replay_game.map.get_cell(x, y)




      # Test resource

      if bool(env_cell.resource and env_cell.resource.amount > 0) != bool(replay_cell.resource):
        return False




      # Test city tile

      if bool(env_cell.city_tile) != bool(replay_cell.citytile):
        return False




      # Test units

      if len(env_cell.units) != replay_units_map[y][x]:
        return False




  return True





def get_replay_team_cell_actions(game: Game, team_env_actions: List[Action],
considered_units_map: List[List[Unit]]):
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
        unit: Unit = game.get_unit(team_env_action.team, team_env_action.source_id)
      else:
        unit: Unit = game.get_unit(team_env_action.team, team_env_action.unit_id)

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
  



dir_path = 'C:/Users/gusta/Desktop/Lux AI/Replays/Replays'

for file_name in os.listdir(dir_path):
  file_path = f'{dir_path}/{file_name}'

  if os.path.isfile(file_path):
    analyze_replay(file_path)