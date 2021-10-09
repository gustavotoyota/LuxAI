import math, sys



from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux.game_objects import City, Unit
from lux import annotate



import numpy as np

from submission.lux.game_objects import CityTile




# Input list

input_list = []



input_list.append('TileRoadLevel')



input_list.append('ResourceExists')

input_list.append('ResourceIsWood')
input_list.append('ResourceIsCoal')
input_list.append('ResourceIsUranium')



input_list.append('TeamExists')

input_list.append('TeamIsPlayer')
input_list.append('TeamIsOpponent')



input_list.append('CityTileExists')

input_list.append('CityTileCooldown')
input_list.append('CityTileCanAct')



input_list.append('CityFuelAmount')
input_list.append('CityFuelUpkeep')



input_list.append('UnitExists')

input_list.append('UnitIsWorker')
input_list.append('UnitIsCart')

input_list.append('UnitWoodAmount')
input_list.append('UnitCoalAmount')
input_list.append('UnitUraniumAmount')

input_list.append('UnitResourceCapacity')

input_list.append('UnitCooldown')
input_list.append('UnitCanAct')



input_list.append('PlayerResourcePoints')

input_list.append('PlayerResearchedCoal')
input_list.append('PlayerResearchedUranium')



input_list.append('GameCurrentTurn')

input_list.append('GameIsNight')
input_list.append('GameNightPercent')

input_list.append('GameCityTileRatio')




# Input map

input_map = {}
for i in range(len(input_list)):
  input_map[input_list[i]] = i




# Input count

INPUT_COUNT = len(input_list)





def prep_input(value, dep=True):
  if dep is None or not dep:
    return -1.0

  if callable(value):
    return float(value()) * 2.0 - 1.0
  
  return float(value) * 2.0 - 1.0





def get_game_state_input(game_state: Game, observation):
  player = game_state.players[observation.player]
  opponent = game_state.players[(observation.player + 1) % 2]



  
  input = np.zeros((game_state.map.width, game_state.map.height, INPUT_COUNT))




  aux_cells = []

  for y in range(game_state.map.height):
    row = []

    aux_cells.append(row)

    for x in range(game_state.map.width):
      aux_cell = {}

      row.append(aux_cell)





  for unit in player.units + opponent.units:
    aux_cell = aux_cells[unit.pos.y][unit.pos.x]
    
    aux_cell['Unit'] = unit




  
  for y in range(game_state.map.height):
    for x in range(game_state.map.width):
      cell = game_state.map.get_cell(x, y)
      aux_cell = aux_cells[y][x]




      # Tile

      input[input_map['TileRoadLevel'], y, x] = prep_input(cell.road / 6.0)




      # Resources

      input[input_map['ResourceExists'], y, x] = prep_input(cell.has_resource())

      input[input_map['ResourceIsWood'], y, x] = prep_input(lambda: cell.resource.type == 'wood', cell.has_resource())
      input[input_map['ResourceIsCoal'], y, x] = prep_input(lambda: cell.resource.type == 'coal', cell.has_resource())
      input[input_map['ResourceIsUranium'], y, x] = prep_input(lambda: cell.resource.type == 'uranium', cell.has_resource())




      # City tile
      
      citytile: CityTile = cell.citytile

      input[input_map['CityTileExists'], y, x] = prep_input(citytile is not None)

      input[input_map['CityTileCooldown'], y, x] = prep_input(lambda: citytile.cooldown / 10.0, citytile)
      input[input_map['CityTileCanAct'], y, x] = prep_input(lambda: citytile.can_act(), citytile)


      

      # City

      city: City = None
      
      if citytile is not None:
        if citytile.team == player.team:
          city = player.cities[citytile.cityid]
        else:
          city = opponent.cities[citytile.cityid]

      input[input_map['CityFuelAmount'], y, x] = prep_input(lambda: city.fuel / 10000.0, citytile)
      input[input_map['CityFuelUpkeep'], y, x] = prep_input(lambda: city.get_light_upkeep() / 100.0, citytile)




      # Unit

      unit: Unit = aux_cell['Unit']

      input[input_map['UnitExists'], y, x] = prep_input(unit is not None)

      input[input_map['UnitIsWorker'], y, x] = prep_input(lambda: unit.type == 0, unit)
      input[input_map['UnitIsCart'], y, x] = prep_input(lambda: unit.type == 1, unit)

      if unit.type == 0:
        unit_name = 'WORKER'
      else:
        unit_name = 'CART'

      unit_capacity = float(GAME_CONSTANTS['PARAMETERS']['RESOURCE_CAPACITY'][unit_name])

      input[input_map['UnitWoodAmount'], y, x] = prep_input(lambda: unit.cargo.wood / unit_capacity, unit)
      input[input_map['UnitCoalAmount'], y, x] = prep_input(lambda: unit.cargo.coal / unit_capacity, unit)
      input[input_map['UnitUraniumAmount'], y, x] = prep_input(lambda: unit.cargo.uranium / unit_capacity, unit)

      input[input_map['UnitResourceCapacity'], y, x] = prep_input(lambda: unit.get_cargo_space_left() / unit_capacity, unit)

      input[input_map['UnitCooldown'], y, x] = prep_input(lambda: unit.cooldown / GAME_CONSTANTS['PARAMETERS']['UNIT_ACTION_COOLDOWN'][unit_name], unit)
      input[input_map['UnitCanAct'], y, x] = prep_input(lambda: unit.can_act(), unit)


      

      # Team

      team = -1
      
      if unit is not None:
        team = int(unit.team == opponent.team)
      elif citytile is not None:
        team = int(citytile.team == opponent.team)

      input[input_map['TeamExists'], y, x] = prep_input(team != -1)
      input[input_map['TeamIsPlayer'], y, x] = prep_input(team == 0)
      input[input_map['TeamIsOpponent'], y, x] = prep_input(team == 1)




      # Player

      input[input_map['PlayerResearchPoints'], y, x] = prep_input(player.research_points / 200.0)
      input[input_map['PlayerResearchedCoal'], y, x] = prep_input(player.researched_coal())
      input[input_map['PlayerResearchedUranium'], y, x] = prep_input(player.researched_uranium())



      
      # Game

      input[input_map['GameCurrentTurn'], y, x] = prep_input(game_state.turn / 360.0)



      turn_mod_360 = game_state.turn % 360

      input[input_map['GameIsNight'], y, x] = prep_input(turn_mod_360 >= 30)

      if turn_mod_360 < 30:
        input[input_map['GameNightPercent'], y, x] = prep_input(turn_mod_360 / 30.0)
      else:
        input[input_map['GameNightPercent'], y, x] = prep_input(1.0 - (turn_mod_360 - 30.0) / 10.0)



      input[input_map['GameCityTileRatio'], y, x] = player.city_tile_count / max(1, player.city_tile_count + opponent.city_tile_count)




  return input