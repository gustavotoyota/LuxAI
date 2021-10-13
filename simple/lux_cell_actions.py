from typing import List, Tuple
from luxai2021.game.actions import UNIT_TYPES
from luxai2021.game.cell import Cell
from luxai2021.game.city import City, CityTile
from luxai2021.game.game import DIRECTIONS, Game
from luxai2021.game.position import Position
from luxai2021.game.unit import Unit




import numpy as np




from lux_utils import *
from lux_units import *





# Unit action list

cell_action_list = []




cell_action_list.append('BuildWorker')
cell_action_list.append('BuildCart')

cell_action_list.append('Research')




cell_action_list.append('DoNothing')

cell_action_list.append('MoveNorth')
cell_action_list.append('MoveWest')
cell_action_list.append('MoveEast')
cell_action_list.append('MoveSouth')

cell_action_list.append('SmartTransfer')




cell_action_list.append('BuildCity')
cell_action_list.append('Pillage')




# Unit action map

cell_action_map = {}
for i in range(len(cell_action_list)):
  cell_action_map[cell_action_list[i]] = i




# Unit action count

UNIT_ACTION_COUNT = len(cell_action_list)





def get_valid_cell_actions(game: Game, team: int, considered_units_map) -> List[Tuple]:
  valid_cell_actions = []
  


  # Cities

  for _, city in game.cities:
    city: City



    if city.team != team:
      continue



    for city_tile in city.city_cells:
      city_tile: CityTile



      if not city_tile.can_act():
        continue



      valid_cell_actions.append((cell_action_map['BuildWorker'], city_tile.pos.y, city_tile.pos.x))
      valid_cell_actions.append((cell_action_map['BuildCart'], city_tile.pos.y, city_tile.pos.x))

      if game.state["teamStates"][team]["researchPoints"] < 200:
        valid_cell_actions.append((cell_action_map['Research'], city_tile.pos.y, city_tile.pos.x))




  # Units

  for unit in game.get_teams_units(team):
    unit: Unit



    if considered_units_map[unit.pos.y][unit.pos.x] != unit:
      continue



    if not unit.can_act():
      continue




    valid_cell_actions.append((cell_action_map['DoNothing'], unit.pos.y, unit.pos.x))
    
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.NORTH):
      valid_cell_actions.append((cell_action_map['MoveNorth'], unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.WEST):
      valid_cell_actions.append((cell_action_map['MoveWest'], unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.EAST):
      valid_cell_actions.append((cell_action_map['MoveEast'], unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.SOUTH):
      valid_cell_actions.append((cell_action_map['MoveSouth'], unit.pos.y, unit.pos.x))




    # Smart transfer
    
    unit_cell = game.map.get_cell(unit.pos.x, unit.pos.y)

    for adjacent_cell in game.map.get_adjacent_cells(unit_cell):
      adjacent_cell: Cell

      for adjacent_unit in adjacent_cell.units:
        adjacent_unit: Unit

        if adjacent_unit.team == team and adjacent_unit.get_cargo_space_left() > 0:
          valid_cell_actions.append((cell_action_map['SmartTransfer'], unit.pos.y, unit.pos.x))
          break
        

    

    if unit.type == UNIT_TYPES.WORKER:
      if not unit_cell.is_city_tile():
        valid_cell_actions.append((cell_action_map['BuildCity'], unit.pos.y, unit.pos.x))

      if unit_cell.get_road() >= 0.5:
        valid_cell_actions.append((cell_action_map['Pillage'], unit.pos.y, unit.pos.x))



  
  return valid_cell_actions







def is_move_action_valid(game: Game, team: int, pos: Position, dir: DIRECTIONS) -> bool:
  target_pos = pos.translate(dir, 1)




  if target_pos.x < 0 or target_pos.x >= game.map.width:
    return False

  if target_pos.y < 0 or target_pos.y >= game.map.height:
    return False




  cell = game.map.get_cell(target_pos)




  if cell.has_resource():
    return False



  if cell.city_tile:
    return cell.city_tile.team == team



  return cell.has_units()