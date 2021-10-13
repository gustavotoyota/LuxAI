import torch
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




input_list.append('UnitIsWorker')
input_list.append('UnitIsCart')

input_list.append('UnitResourceSpace')
input_list.append('UnitFuelAmount')

input_list.append('UnitCooldown')
input_list.append('UnitCanAct')




input_list.append('OtherUnitsCount')
input_list.append('OtherUnitsWorkerCartRatio')

input_list.append('OtherUnitsResourceSpace')
input_list.append('OtherUnitsFuelAmount')




input_list.append('PlayerResearchPoints')

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





def get_team_observation(game: Game, team: int):
  team_observation = np.zeros((INPUT_COUNT, game.map.configs['height'], game.map.configs['width']))




  team_considered_units_map = get_team_considered_units_map(game, team)




  for y in range(game.map.configs['height']):
    for x in range(game.map.configs['width']):
      cell = game.map.get_cell(x, y)




      # Tile

      team_observation[input_map['TileRoadLevel'], y, x] = prep_input(cell.get_road() / 6.0)



      
      # Resources

      team_observation[input_map['ResourceExists'], y, x] = prep_input(cell.has_resource())

      team_observation[input_map['ResourceIsWood'], y, x] = prep_input(lambda: cell.resource.type == 'wood', cell.has_resource())
      team_observation[input_map['ResourceIsCoal'], y, x] = prep_input(lambda: cell.resource.type == 'coal', cell.has_resource())
      team_observation[input_map['ResourceIsUranium'], y, x] = prep_input(lambda: cell.resource.type == 'uranium', cell.has_resource())
      
      team_observation[input_map['ResourceAmount'], y, x] = prep_input(lambda: cell.resource.amount / 350.0, cell.has_resource())


      
      
      # City tile

      citytile: CityTile = cell.city_tile

      team_observation[input_map['CityTileExists'], y, x] = prep_input(citytile is not None)

      team_observation[input_map['CityTileCooldown'], y, x] = prep_input(lambda: citytile.cooldown / 10.0, citytile)
      team_observation[input_map['CityTileCanAct'], y, x] = prep_input(lambda: citytile.can_act(), citytile)



      
      # City

      city: City = None

      if citytile is not None:
        city = game.cities[citytile.city_id]

      team_observation[input_map['CityFuelAmount'], y, x] = prep_input(lambda: city.fuel / 10000.0, citytile)
      team_observation[input_map['CityFuelUpkeep'], y, x] = prep_input(lambda: city.get_light_upkeep() / 100.0, citytile)
      
      
      
      
      # Unit

      considered_unit: Unit = team_considered_units_map[y][x]

      if considered_unit:
        if considered_unit.is_worker():
          unit_resource_capacity = 100.0
          unit_base_cooldown = 2.0
        else:
          unit_resource_capacity = 2000.0
          unit_base_cooldown = 3.0

        unit_fuel_capacity = 40.0 * unit_resource_capacity

      team_observation[input_map['UnitIsWorker'], y, x] = prep_input(lambda: considered_unit.is_worker(), considered_unit)
      team_observation[input_map['UnitIsCart'], y, x] = prep_input(lambda: considered_unit.is_cart(), considered_unit)

      team_observation[input_map['UnitResourceSpace'], y, x] = prep_input(lambda: considered_unit.get_cargo_space_left() / unit_resource_capacity, considered_unit)
      team_observation[input_map['UnitFuelAmount'], y, x] = prep_input(lambda: considered_unit.get_cargo_fuel_value() / unit_fuel_capacity, considered_unit)

      team_observation[input_map['UnitCooldown'], y, x] = prep_input(lambda: considered_unit.cooldown / unit_base_cooldown, considered_unit)
      team_observation[input_map['UnitCanAct'], y, x] = prep_input(lambda: considered_unit.can_act(), considered_unit)




      # Other units

      unit_count = 0
      cart_count = 0

      total_resource_space = 0
      total_resource_capacity = 0.0

      total_fuel = 0

      for unit in cell.units.values():
        unit: Unit

        if unit.team != team:
          continue

        if unit == considered_unit:
          continue

        unit_count = unit_count + 1

        if unit.is_cart():
          cart_count = cart_count + 1

        total_fuel += unit.get_cargo_fuel_value()

        total_resource_space += unit.get_cargo_space_left()
        
        if unit.is_worker():
          total_resource_capacity += 100.0
        else:
          total_resource_capacity += 2000.0

      total_fuel_capacity = 40.0 * total_resource_capacity
      
      team_observation[input_map['OtherUnitsCount'], y, x] = prep_input(unit_count)
      team_observation[input_map['OtherUnitsWorkerCartRatio'], y, x] = prep_input(cart_count / max(1.0, unit_count))

      team_observation[input_map['OtherUnitsResourceSpace'], y, x] = prep_input(total_resource_space / max(1.0, total_resource_capacity))
      team_observation[input_map['OtherUnitsFuelAmount'], y, x] = prep_input(total_fuel / max(1.0, total_fuel_capacity))


      
      
      # Team

      aux_team = -1
      
      if considered_unit is not None:
        aux_team = int(considered_unit.team == team)
      elif citytile is not None:
        aux_team = int(citytile.team == team)

      team_observation[input_map['TeamExists'], y, x] = prep_input(aux_team != -1)

      team_observation[input_map['TeamIsPlayer'], y, x] = prep_input(aux_team == 1)
      team_observation[input_map['TeamIsOpponent'], y, x] = prep_input(aux_team == 0)




      # Player

      team_state = game.state['teamStates'][team]

      team_observation[input_map['PlayerResearchPoints'], y, x] = prep_input(team_state['researchPoints'] / 200.0)
      team_observation[input_map['PlayerResearchedCoal'], y, x] = prep_input(team_state['researched']['coal'])
      team_observation[input_map['PlayerResearchedUranium'], y, x] = prep_input(team_state['researched']['uranium'])
      



      # Game

      team_observation[input_map['GameCurrentTurn'], y, x] = prep_input(game.state['turn'] / 360.0)




      team_observation[input_map['GameIsNight'], y, x] = prep_input(game.is_night())
      
      turn_mod_40 = game.state['turn'] % 40

      if turn_mod_40 < 30:
        team_observation[input_map['GameNightPercent'], y, x] = prep_input(turn_mod_40 / 30.0)
      else:
        team_observation[input_map['GameNightPercent'], y, x] = prep_input(1.0 - (turn_mod_40 - 30.0) / 10.0)



      city_tile_count = [0, 0]
      for city in game.cities.values():
        city_tile_count[city.team] += len(city.city_cells)

      team_observation[input_map['GameCityTileRatio'], y, x] = prep_input(city_tile_count[team] / float(sum(city_tile_count)))



  return torch.Tensor(team_observation).unsqueeze(0)