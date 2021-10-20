from typing import List, Tuple




import luxai2021.game.cell
import luxai2021.game.city
import luxai2021.game.game
import luxai2021.game.position
import luxai2021.game.unit
import luxai2021.game.constants




import numpy as np




import lux_engine_actions





# Unit action list

CELL_ACTION_COUNT = 0

def add_cell_action():
  global CELL_ACTION_COUNT
  CELL_ACTION_COUNT += 1
  return CELL_ACTION_COUNT - 1




CELL_ACTION_CITY_TILE_DO_NOTHING = add_cell_action()

CELL_ACTION_CITY_TILE_BUILD_WORKER = add_cell_action()
CELL_ACTION_CITY_TILE_BUILD_CART = add_cell_action()

CELL_ACTION_CITY_TILE_RESEARCH = add_cell_action()




CELL_ACTION_UNIT_DO_NOTHING = add_cell_action()

CELL_ACTION_UNIT_MOVE_NORTH = add_cell_action()
CELL_ACTION_UNIT_MOVE_WEST = add_cell_action()
CELL_ACTION_UNIT_MOVE_SOUTH = add_cell_action()
CELL_ACTION_UNIT_MOVE_EAST = add_cell_action()

CELL_ACTION_UNIT_SMART_TRANSFER = add_cell_action()

CELL_ACTION_UNIT_BUILD_CITY = add_cell_action()
CELL_ACTION_UNIT_PILLAGE = add_cell_action()





def get_team_valid_cell_actions(game: luxai2021.game.game.Game, team: int,
considered_units_map: List[List[luxai2021.game.unit.Unit]]) -> List[Tuple]:
  team_valid_cell_actions = []
  


  # Cities

  for city in game.cities.values():
    city: luxai2021.game.city.City



    if city.team != team:
      continue



    for city_cell in city.city_cells:
      city_cell: luxai2021.game.cell.Cell
      city_tile: luxai2021.game.city.CityTile = city_cell.city_tile



      if not city_tile.can_act():
        continue
      


      team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_DO_NOTHING, city_tile.pos.y, city_tile.pos.x))

      if not game.worker_unit_cap_reached(team):
        team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_BUILD_WORKER, city_tile.pos.y, city_tile.pos.x))
        team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_BUILD_CART, city_tile.pos.y, city_tile.pos.x))

      if game.state["teamStates"][team]["researchPoints"] < 200:
        team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_RESEARCH, city_tile.pos.y, city_tile.pos.x))




  # Units

  for unit in game.get_teams_units(team).values():
    unit: luxai2021.game.unit.Unit



    if considered_units_map[unit.pos.y][unit.pos.x] != unit:
      continue



    if not unit.can_act():
      continue



    team_valid_cell_actions.append((CELL_ACTION_UNIT_DO_NOTHING, unit.pos.y, unit.pos.x))
    
    if is_move_action_valid(game, team, unit.pos, luxai2021.game.game.DIRECTIONS.NORTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_NORTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, luxai2021.game.game.DIRECTIONS.WEST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_WEST, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, luxai2021.game.game.DIRECTIONS.SOUTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_SOUTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, luxai2021.game.game.DIRECTIONS.EAST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_EAST, unit.pos.y, unit.pos.x))




    # Smart transfer
    
    unit_cell = game.map.get_cell(unit.pos.x, unit.pos.y)

    for adjacent_cell in game.map.get_adjacent_cells(unit_cell):
      adjacent_cell: luxai2021.game.cell.Cell

      for adjacent_unit in adjacent_cell.units.values():
        adjacent_unit: luxai2021.game.unit.Unit

        if adjacent_unit.team != team:
          continue

        if adjacent_unit.get_cargo_space_left() == 0:
          continue

        team_valid_cell_actions.append((CELL_ACTION_UNIT_SMART_TRANSFER, unit.pos.y, unit.pos.x))

        break
        

    

    if unit.type == luxai2021.game.unit.UNIT_TYPES.WORKER:
      if not unit_cell.is_city_tile():
        team_valid_cell_actions.append((CELL_ACTION_UNIT_BUILD_CITY, unit.pos.y, unit.pos.x))

        if unit_cell.get_road() > 0:
          team_valid_cell_actions.append((CELL_ACTION_UNIT_PILLAGE, unit.pos.y, unit.pos.x))



  
  return team_valid_cell_actions






def is_move_action_valid(game: luxai2021.game.game.Game, team: int,
pos: luxai2021.game.position.Position, dir: luxai2021.game.game.DIRECTIONS) -> bool:
  target_pos = pos.translate(dir, 1)




  if target_pos.x < 0 or target_pos.x >= game.map.width:
    return False

  if target_pos.y < 0 or target_pos.y >= game.map.height:
    return False




  cell: luxai2021.game.cell.Cell = game.map.get_cell_by_pos(target_pos)



  if cell.city_tile:
    return cell.city_tile.team == team



  return not cell.has_units()
  




def get_cell_action_mask(game: luxai2021.game.game.Game, valid_cell_actions):
  cell_action_mask = np.zeros((CELL_ACTION_COUNT, game.map.height, game.map.width), np.float32)


  for valid_cell_action in valid_cell_actions:
    cell_action_mask[valid_cell_action] = 1.0


  return cell_action_mask





def normalize_cell_action_probs(cell_action_probs, cell_action_mask):
  cell_action_probs *= cell_action_mask
  cell_action_probs /= max(1.0, np.sum(cell_action_probs).item())

  return cell_action_probs





def get_team_cell_actions(game: luxai2021.game.game.Game, team: int,
team_engine_actions: List[luxai2021.game.actions.Action],
considered_units_map: List[List[luxai2021.game.unit.Unit]]):
  # Dictionary for city tile actions

  city_tile_actions_dict = {}

  for city in game.cities.values():
    city: luxai2021.game.city.City

    if city.team != team:
      continue

    for city_cell in city.city_cells:
      city_cell: luxai2021.game.cell.Cell
      city_tile: luxai2021.game.city.CityTile = city_cell.city_tile

      if not city_tile.can_act():
        continue

      city_tile_actions_dict[(city_tile.pos.y, city_tile.pos.x)] = \
        CELL_ACTION_CITY_TILE_DO_NOTHING



  # Dictionary for unit actions

  unit_actions_dict = {}

  for unit in game.get_teams_units(team).values():
    unit: luxai2021.game.unit.Unit

    if not unit.can_act():
      continue

    if unit != considered_units_map[unit.pos.y][unit.pos.x]:
      continue

    unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_DO_NOTHING




  for team_engine_action in team_engine_actions:
    is_city_tile = team_engine_action.action in lux_engine_actions.CITY_ENGINE_ACTIONS

    if is_city_tile:
      if team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.BUILD_WORKER:
        city_tile_actions_dict[(team_engine_action.y, team_engine_action.x)] = \
          CELL_ACTION_CITY_TILE_BUILD_WORKER
      elif team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.BUILD_CART:
        city_tile_actions_dict[(team_engine_action.y, team_engine_action.x)] = \
          CELL_ACTION_CITY_TILE_BUILD_CART
      elif team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.RESEARCH:
        city_tile_actions_dict[(team_engine_action.y, team_engine_action.x)] = \
          CELL_ACTION_CITY_TILE_RESEARCH
      else:
        raise Exception('Unknown city tile action.')
    else:
      if team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.TRANSFER:
        unit: luxai2021.game.unit.Unit = game.get_unit(team_engine_action.team, team_engine_action.source_id)
      else:
        unit: luxai2021.game.unit.Unit = game.get_unit(team_engine_action.team, team_engine_action.unit_id)

      if unit != considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      if team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.MOVE:
        if team_engine_action.direction == luxai2021.game.constants.Constants.DIRECTIONS.CENTER:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_DO_NOTHING
        elif team_engine_action.direction == luxai2021.game.constants.Constants.DIRECTIONS.NORTH:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_NORTH
        elif team_engine_action.direction == luxai2021.game.constants.Constants.DIRECTIONS.WEST:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_WEST
        elif team_engine_action.direction == luxai2021.game.constants.Constants.DIRECTIONS.SOUTH:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_SOUTH
        elif team_engine_action.direction == luxai2021.game.constants.Constants.DIRECTIONS.EAST:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_MOVE_EAST
        else:
          raise Exception('Unknown unit move action.')
      elif team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.TRANSFER:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_SMART_TRANSFER
      elif team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.BUILD_CITY:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_BUILD_CITY
      elif team_engine_action.action == luxai2021.game.constants.Constants.ACTIONS.PILLAGE:
          unit_actions_dict[(unit.pos.y, unit.pos.x)] = CELL_ACTION_UNIT_PILLAGE
      else:
        raise Exception('Unknown unit action.')




  # Fill the matrix of cell actions of the team

  team_cell_actions = np.zeros((CELL_ACTION_COUNT,
    game.map.height, game.map.width), np.float32)

  for city_tile_pos, city_tile_action in city_tile_actions_dict.items():
    team_cell_actions[(city_tile_action, ) + city_tile_pos] = 1.0

  for unit_pos, unit_action in unit_actions_dict.items():
    team_cell_actions[(unit_action, ) + unit_pos] = 1.0




  return team_cell_actions