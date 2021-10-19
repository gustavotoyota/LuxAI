import json
import os
from typing import List

import numpy as np




import luxai2021.game.game
import luxai2021.game.actions
import luxai2021.game.constants
import luxai2021.game.unit
import luxai2021.game.cell
import luxai2021.game.city




import lux.game




import lux_inputs
import lux_units
import lux_cell_actions
import lux_utils
import lux_engine_actions





def analyze_replay(file_path):
  replay_id = os.path.splitext(os.path.basename(file_path))[0]

  print('Replay:', replay_id)
  




  # Load replay object

  with open(file_path) as file:
    replay_obj = json.load(file)





  engine_game = luxai2021.game.game.Game({'seed': replay_obj['configuration']['seed']})





  replay_game: lux.game.Game = lux.game.Game()
  replay_game._initialize(replay_obj['steps'][0][0]['observation']['updates'])
  replay_game._update(replay_obj['steps'][0][0]['observation']['updates'])





  team_histories = ([], [])

  error = None

  try:
    for step_obj in replay_obj['steps'][1:]:
      step_obj = replay_obj['steps'][engine_game.state['turn'] + 1]




      # Update replay game

      replay_game._update(step_obj[0]['observation']['updates'])




      # Get actions

      engine_actions = []
      
      considered_units_map = lux_units.get_considered_units_map(engine_game)

      for team in range(2):
        team_observation = lux_inputs.get_team_observation(
          engine_game, team, considered_units_map).numpy().squeeze()

        team_engine_actions = []

        if step_obj[team]['action']:
          for action in step_obj[team]['action']:
            engine_action = engine_game.action_from_string(action, team)

            if not lux_engine_actions.is_engine_action_valid(
            engine_action, engine_game, team_engine_actions):
              continue

            team_engine_actions.append(engine_action)

        team_cell_actions = lux_cell_actions.get_team_cell_actions(
          engine_game, team, team_engine_actions, considered_units_map)

        team_histories[team].append((team_observation, team_cell_actions))
          
        engine_actions += team_engine_actions




      # Execute actions

      engine_game.run_turn_with_actions(engine_actions)




      # Validate game state

      if not replay_validate_game(engine_game, replay_game):
        error = True
        break

      


      print('Turn:', engine_game.state['turn'])
      #print(engine_game.map.get_map_string())
  except Exception as exception:
    error = exception
    print(exception)




  # Validate and move replay

  dir_path = os.path.dirname(file_path)

  if error or not engine_game.match_over() or \
  (engine_game.state['turn'] != len(replay_obj['steps']) - 1 and \
  not (engine_game.state['turn'] == 359 and len(replay_obj['steps']) == 361)):
    os.makedirs(f'{dir_path}/failures', exist_ok=True)
    os.replace(file_path, f'{dir_path}/failures/{file_name}')

    print('Fail!')

    return
  
  os.makedirs(f'{dir_path}/successes', exist_ok=True)
  os.replace(file_path, f'{dir_path}/successes/{file_name}')

  print('Success!')




  # Create samples

  samples = []

  for team in range(2):
    target_value = np.array([float(engine_game.get_winning_team() == team) * 2.0 - 1.0], np.float32)

    team_history = team_histories[team]
    
    samples.append((team_history[0][0], team_history[0][1], np.array([0.0], np.float32)))

    for experience in team_history[1:]:
      samples.append((experience[0], experience[1], target_value))




  # Organize samples

  inputs = np.array([sample[0] for sample in samples], np.float32)
  policy_targets = np.array([sample[1] for sample in samples], np.float32)
  value_targets = np.array([sample[2] for sample in samples], np.float32)

  samples = (inputs, policy_targets, value_targets)




  # Save samples

  dir_path = f'samples/{engine_game.map.width}'

  os.makedirs(dir_path, exist_ok=True)

  lux_utils.save_lz4_pickle(samples, f'{dir_path}/{replay_id}.pickle')





def replay_validate_game(engine_game: luxai2021.game.game.Game, replay_game: lux.game.Game):
  replay_units_map = np.zeros((engine_game.map.height, engine_game.map.width), np.int32)

  for team in range(2):
    for unit in replay_game.players[team].units:
      replay_units_map[unit.pos.y][unit.pos.x] += 1




  for y in range(engine_game.map.height):
    for x in range(engine_game.map.width):
      engine_cell = engine_game.map.get_cell(x, y)
      replay_cell = replay_game.map.get_cell(x, y)




      # Test resource

      if bool(engine_cell.resource and engine_cell.resource.amount > 0) != bool(replay_cell.resource):
        return False




      # Test city tile

      if bool(engine_cell.city_tile) != bool(replay_cell.citytile):
        return False




      # Test units

      if len(engine_cell.units) != replay_units_map[y][x]:
        return False




  return True
  



dir_path = 'expert_replays/replays'

for file_name in os.listdir(dir_path):
  file_path = f'{dir_path}/{file_name}'

  if os.path.isfile(file_path):
    analyze_replay(file_path)