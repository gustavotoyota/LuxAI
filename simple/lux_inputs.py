from luxai2021.game.city import City, CityTile
from luxai2021.game.game import Game
from luxai2021.game.unit import Unit



import numpy as np



from lux_inputs import *
from lux_units import *





# Input list

input_list = []



input_list.append('TileRoadLevel')



input_list.append('ResourceExists')

input_list.append('ResourceIsWood')
input_list.append('ResourceIsCoal')
input_list.append('ResourceIsUranium')

input_list.append('ResourceAmount')



input_list.append('TeamExists')

input_list.append('TeamIsPlayer')
input_list.append('TeamIsOpponent')



input_list.append('CityTileExists')

input_list.append('CityTileCooldown')
input_list.append('CityTileCanAct')



input_list.append('CityFuelAmount')
input_list.append('CityFuelUpkeep')



input_list.append('UnitCount')

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
  if not dep:
    return -1.0

  if callable(value):
    return float(value()) * 2.0 - 1.0
  
  return float(value) * 2.0 - 1.0





def get_observation(game: Game, team: int):
  input = np.zeros((INPUT_COUNT, game.map.configs['height'], game.map.configs['width']))



  considered_units_map = get_considered_units_map(game, team)




  for y in range(game.map.configs['height']):
    for x in range(game.map.configs['width']):
      cell = game.map.get_cell(x, y)




      # Tile

      input[input_map['TileRoadLevel'], y, x] = prep_input(cell.get_road() / 6.0)



      
      # Resources

      input[input_map['ResourceExists'], y, x] = prep_input(cell.has_resource())

      input[input_map['ResourceIsWood'], y, x] = prep_input(lambda: cell.resource.type == 'wood', cell.has_resource())
      input[input_map['ResourceIsCoal'], y, x] = prep_input(lambda: cell.resource.type == 'coal', cell.has_resource())
      input[input_map['ResourceIsUranium'], y, x] = prep_input(lambda: cell.resource.type == 'uranium', cell.has_resource())
      
      input[input_map['ResourceAmount'], y, x] = prep_input(lambda: cell.resource.amount / 350.0, cell.has_resource())


      
      
      # City tile

      citytile: CityTile = cell.city_tile

      input[input_map['CityTileExists'], y, x] = prep_input(citytile is not None)

      input[input_map['CityTileCooldown'], y, x] = prep_input(lambda: citytile.cooldown / 10.0, citytile)
      input[input_map['CityTileCanAct'], y, x] = prep_input(lambda: citytile.can_act(), citytile)



      
      # City

      city: City = None

      if citytile is not None:
        city = game.cities[citytile.city_id]

      input[input_map['CityFuelAmount'], y, x] = prep_input(lambda: city.fuel / 10000.0, citytile)
      input[input_map['CityFuelUpkeep'], y, x] = prep_input(lambda: city.get_light_upkeep() / 100.0, citytile)
      
      
      
      
      # Unit

      unit: Unit = considered_units_map[y][x]

      input[input_map['UnitCount'], y, x] = prep_input(len(cell.units))

      input[input_map['UnitIsWorker'], y, x] = prep_input(lambda: unit.type == 0, unit)
      input[input_map['UnitIsCart'], y, x] = prep_input(lambda: unit.type == 1, unit)

      if unit.type == 0:
        unit_capacity = 100.0
      else:
        unit_capacity = 2000.0

      input[input_map['UnitWoodAmount'], y, x] = prep_input(lambda: unit.cargo['wood'] / unit_capacity, unit)
      input[input_map['UnitCoalAmount'], y, x] = prep_input(lambda: unit.cargo['coal'] / unit_capacity, unit)
      input[input_map['UnitUraniumAmount'], y, x] = prep_input(lambda: unit.cargo['uranium'] / unit_capacity, unit)

      input[input_map['UnitResourceCapacity'], y, x] = prep_input(lambda: unit.get_cargo_space_left() / unit_capacity, unit)

      if unit.type == 0:
        unit_base_cooldown = 2.0
      else:
        unit_base_cooldown = 3.0

      input[input_map['UnitCooldown'], y, x] = prep_input(lambda: unit.cooldown / unit_base_cooldown, unit)
      input[input_map['UnitCanAct'], y, x] = prep_input(lambda: unit.can_act(), unit)


      
      
      # Team

      aux_team = -1
      
      if unit is not None:
        aux_team = int(unit.team != team)
      elif citytile is not None:
        aux_team = int(citytile.team != team)

      input[input_map['TeamExists'], y, x] = prep_input(aux_team != -1)

      input[input_map['TeamIsPlayer'], y, x] = prep_input(aux_team == 0)
      input[input_map['TeamIsOpponent'], y, x] = prep_input(aux_team == 1)




      # Player

      input[input_map['PlayerResearchPoints'], y, x] = prep_input(game.state['researchPoints'] / 200.0)
      input[input_map['PlayerResearchedCoal'], y, x] = prep_input(game.state['researched']['coal'])
      input[input_map['PlayerResearchedUranium'], y, x] = prep_input(game.state['researched']['uranium'])
      



      # Game

      input[input_map['GameCurrentTurn'], y, x] = prep_input(game.state['turn'] / 360.0)



      turn_mod_360 = game.state['turn'] % 360

      input[input_map['GameIsNight'], y, x] = prep_input(turn_mod_360 >= 30)

      if turn_mod_360 < 30:
        input[input_map['GameNightPercent'], y, x] = prep_input(turn_mod_360 / 30.0)
      else:
        input[input_map['GameNightPercent'], y, x] = prep_input(1.0 - (turn_mod_360 - 30.0) / 10.0)



      city_tile_count = [0, 0]
      for city in game.cities.values():
        city_tile_count[city.team] += len(city.city_cells)

      input[input_map['GameCityTileRatio'], y, x] = city_tile_count[team] / float(sum(city_tile_count))