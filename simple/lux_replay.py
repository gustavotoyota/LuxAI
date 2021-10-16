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




  # replay_game: lux.game.Game = lux.game.Game()
  # replay_game._initialize(replay_obj['steps'][0][0]['observation']['updates'])
  # replay_game._update(replay_obj['steps'][0][0]['observation']['updates'])




  team_histories = ([], [])

  error = None

  try:
    for step_obj in replay_obj['steps'][1:]:
      # Update replay game
      
      step_obj = replay_obj['steps'][env_game.state['turn'] + 1]

      # replay_game._update(step_obj[0]['observation']['updates'])




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

        team_cell_actions = get_replay_team_cell_actions(
          env_game, team, team_env_actions, considered_units_map)

        team_histories[team].append((team_observation, team_cell_actions))




      # Execute actions

      env_game.run_turn_with_actions(env_actions)




      # Validate game state

      # if not replay_validate_game_state(env_game, replay_game):
      #   error = True
      #   break

      


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





def get_replay_team_cell_actions(game: Game, team: int,
team_env_actions: List[Action], considered_units_map: List[List[Unit]]):
  city_tile_actions_map = {}

  for city in game.cities.values():
    city: City

    if city.team != team:
      continue

    for city_cell in city.city_cells:
      city_cell: Cell
      city_tile: CityTile = city_cell.city_tile

      if not city_tile.can_act():
        continue

      city_tile_actions_map[(city_tile.pos.y, city_tile.pos.x)] = CELL_ACTION_CITY_TILE_DO_NOTHING




  unit_actions_map = {}

  for unit in game.get_teams_units(team).values():
    unit: Unit

    if not unit.can_act():
      continue

    if unit != considered_units_map[unit.pos.y][unit.pos.x]:
      continue

    unit_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_DO_NOTHING




  for team_env_action in team_env_actions:
    is_city_tile = team_env_action.action == Constants.ACTIONS.BUILD_WORKER \
      or team_env_action.action == Constants.ACTIONS.BUILD_CART \
      or team_env_action.action == Constants.ACTIONS.RESEARCH

    if is_city_tile:
      if team_env_action.action == Constants.ACTIONS.BUILD_WORKER:
        city_tile_actions_map[(team_env_action.y, team_env_action.x)] = CELL_ACTION_CITY_TILE_BUILD_WORKER
      elif team_env_action.action == Constants.ACTIONS.BUILD_CART:
        city_tile_actions_map[(team_env_action.y, team_env_action.x)] = CELL_ACTION_CITY_TILE_BUILD_CART
      elif team_env_action.action == Constants.ACTIONS.RESEARCH:
        city_tile_actions_map[(team_env_action.y, team_env_action.x)] = CELL_ACTION_CITY_TILE_RESEARCH
      else:
        raise Exception('Unknown city tile action.')
    else:
      if team_env_action.action == Constants.ACTIONS.TRANSFER:
        unit: Unit = game.get_unit(team_env_action.team, team_env_action.source_id)
      else:
        unit: Unit = game.get_unit(team_env_action.team, team_env_action.unit_id)

      if unit != considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      if team_env_action.action == Constants.ACTIONS.MOVE:
        if team_env_action.direction == Constants.DIRECTIONS.CENTER:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_DO_NOTHING
        elif team_env_action.direction == Constants.DIRECTIONS.NORTH:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_NORTH
        elif team_env_action.direction == Constants.DIRECTIONS.WEST:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_WEST
        elif team_env_action.direction == Constants.DIRECTIONS.SOUTH:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_SOUTH
        elif team_env_action.direction == Constants.DIRECTIONS.EAST:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_EAST
        else:
          raise Exception('Unknown unit action.')
      elif team_env_action.action == Constants.ACTIONS.TRANSFER:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_SMART_TRANSFER
      elif team_env_action.action == Constants.ACTIONS.BUILD_CITY:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_BUILD_CITY
      elif team_env_action.action == Constants.ACTIONS.PILLAGE:
          city_tile_actions_map[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_PILLAGE
      else:
        raise Exception('Unknown unit action.')




  team_cell_actions = np.zeros((CELL_ACTION_COUNT, game.map.height, game.map.width))

  for city_tile_pos, city_tile_action in city_tile_actions_map.items():
    team_cell_actions[(city_tile_action, ) + city_tile_pos] = 1.0

  for unit_pos, unit_action in city_tile_actions_map.items():
    team_cell_actions[(unit_action, ) + unit_pos] = 1.0

  return team_cell_actions
  



dir_path = 'C:/Users/gusta/Desktop/Lux AI/Replays/Replays'

for file_name in os.listdir(dir_path):
  file_path = f'{dir_path}/{file_name}'

  if os.path.isfile(file_path):
    analyze_replay(file_path)