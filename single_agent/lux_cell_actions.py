from typing import List, Tuple




import luxai2021.game.cell as lux_engine_cell
import luxai2021.game.city as lux_engine_city
import luxai2021.game.game as lux_engine_game
import luxai2021.game.position as lux_engine_position
import luxai2021.game.unit as lux_engine_unit




import numpy as np





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





def get_team_valid_cell_actions(game: lux_engine_game.Game, team: int,
considered_units_map: List[List[lux_engine_unit.Unit]]) -> List[Tuple]:
  team_valid_cell_actions = []
  


  # Cities

  for city in game.cities.values():
    city: lux_engine_city.City



    if city.team != team:
      continue



    for city_cell in city.city_cells:
      city_cell: lux_engine_cell.Cell
      city_tile: lux_engine_city.CityTile = city_cell.city_tile



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
    unit: lux_engine_unit.Unit



    if considered_units_map[unit.pos.y][unit.pos.x] != unit:
      continue



    if not unit.can_act():
      continue



    team_valid_cell_actions.append((CELL_ACTION_UNIT_DO_NOTHING, unit.pos.y, unit.pos.x))
    
    if is_move_action_valid(game, team, unit.pos, lux_engine_game.DIRECTIONS.NORTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_NORTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, lux_engine_game.DIRECTIONS.WEST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_WEST, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, lux_engine_game.DIRECTIONS.SOUTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_SOUTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, lux_engine_game.DIRECTIONS.EAST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_EAST, unit.pos.y, unit.pos.x))




    # Smart transfer
    
    unit_cell = game.map.get_cell(unit.pos.x, unit.pos.y)

    for adjacent_cell in game.map.get_adjacent_cells(unit_cell):
      adjacent_cell: lux_engine_cell.Cell

      for adjacent_unit in adjacent_cell.units.values():
        adjacent_unit: lux_engine_unit.Unit

        if adjacent_unit.team != team:
          continue

        if adjacent_unit.get_cargo_space_left() == 0:
          continue

        team_valid_cell_actions.append((CELL_ACTION_UNIT_SMART_TRANSFER, unit.pos.y, unit.pos.x))

        break
        

    

    if unit.type == lux_engine_unit.UNIT_TYPES.WORKER:
      if not unit_cell.is_city_tile():
        team_valid_cell_actions.append((CELL_ACTION_UNIT_BUILD_CITY, unit.pos.y, unit.pos.x))

        if unit_cell.get_road() > 0:
          team_valid_cell_actions.append((CELL_ACTION_UNIT_PILLAGE, unit.pos.y, unit.pos.x))



  
  return team_valid_cell_actions







def is_move_action_valid(game: lux_engine_game.Game, team: int, pos: lux_engine_position.Position, dir: lux_engine_game.DIRECTIONS) -> bool:
  target_pos = pos.translate(dir, 1)




  if target_pos.x < 0 or target_pos.x >= game.map.width:
    return False

  if target_pos.y < 0 or target_pos.y >= game.map.height:
    return False




  cell: lux_engine_cell.Cell = game.map.get_cell_by_pos(target_pos)



  if cell.city_tile:
    return cell.city_tile.team == team



  return not cell.has_units()
  




def get_cell_action_mask(game: lux_engine_game.Game, valid_cell_actions):
  cell_action_mask = np.zeros((CELL_ACTION_COUNT, game.map.height, game.map.width), np.float32)


  for valid_cell_action in valid_cell_actions:
    cell_action_mask[valid_cell_action] = 1.0


  return cell_action_mask





def normalize_cell_action_probs(cell_action_probs, cell_action_mask):
  cell_action_probs *= cell_action_mask
  cell_action_probs /= max(1.0, np.sum(cell_action_probs).item())

  return cell_action_probs