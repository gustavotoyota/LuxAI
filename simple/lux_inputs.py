import torch
from luxai2021.game.city import City, CityTile
from luxai2021.game.game import Game
from luxai2021.game.unit import Unit



import numpy as np



from lux_inputs import *
from lux_units import *





# Input list

input_list = []



INPUT_TILE_ROAD_LEVEL = len(input_list); input_list.append('TileRoadLevel')



INPUT_RESOURCE_EXISTS = len(input_list); input_list.append('ResourceExists')

INPUT_RESOURCE_IS_WOOD = len(input_list); input_list.append('ResourceIsWood')
INPUT_RESOURCE_IS_COAL = len(input_list); input_list.append('ResourceIsCoal')
INPUT_RESOURCE_IS_URANIUM = len(input_list); input_list.append('ResourceIsUranium')

INPUT_RESOURCE_AMOUNT = len(input_list); input_list.append('ResourceAmount')




INPUT_TEAM_EXISTS = len(input_list); input_list.append('TeamExists')

INPUT_TEAM_IS_PLAYER = len(input_list); input_list.append('TeamIsPlayer')
INPUT_TEAM_IS_OPPONENT = len(input_list); input_list.append('TeamIsOpponent')




INPUT_CITY_TILE_EXISTS = len(input_list); input_list.append('CityTileExists')

INPUT_CITY_TILE_COOLDOWN = len(input_list); input_list.append('CityTileCooldown')
INPUT_CITY_TILE_CAN_ACT = len(input_list); input_list.append('CityTileCanAct')




INPUT_CITY_FUEL_AMOUNT = len(input_list); input_list.append('CityFuelAmount')
INPUT_CITY_FUEL_UPKEEP = len(input_list); input_list.append('CityFuelUpkeep')




INPUT_UNIT_IS_WORKER = len(input_list); input_list.append('UnitIsWorker')
INPUT_UNIT_IS_CART = len(input_list); input_list.append('UnitIsCart')

INPUT_UNIT_RESOURCE_SPACE = len(input_list); input_list.append('UnitResourceSpace')
INPUT_UNIT_FUEL_AMOUNT = len(input_list); input_list.append('UnitFuelAmount')

INPUT_UNIT_COOLDOWN = len(input_list); input_list.append('UnitCooldown')
INPUT_UNIT_CAN_ACT = len(input_list); input_list.append('UnitCanAct')




INPUT_OTHER_UNITS_COUNT = len(input_list); input_list.append('OtherUnitsCount')
INPUT_OTHER_UNITS_WORKER_CART_RATIO = len(input_list); input_list.append('OtherUnitsWorkerCartRatio')

INPUT_OTHER_UNITS_RESOURCE_SPACE = len(input_list); input_list.append('OtherUnitsResourceSpace')
INPUT_OTHER_UNITS_FUEL_AMOUNT = len(input_list); input_list.append('OtherUnitsFuelAmount')




INPUT_PLAYER_RESEARCH_POINTS = len(input_list); input_list.append('PlayerResearchPoints')

INPUT_PLAYER_RESEARCHED_COAL = len(input_list); input_list.append('PlayerResearchedCoal')
INPUT_PLAYER_RESEARCHED_URANIUM = len(input_list); input_list.append('PlayerResearchedUranium')




INPUT_GAME_CURRENT_TURN = len(input_list); input_list.append('GameCurrentTurn')

INPUT_GAME_IS_NIGHT = len(input_list); input_list.append('GameIsNight')
INPUT_GAME_NIGHT_PERCENT = len(input_list); input_list.append('GameNightPercent')

INPUT_GAME_CITY_TILE_RATIO = len(input_list); input_list.append('GameCityTileRatio')




# Input map

input_map = {}
for i in range(len(input_list)):
  input_map[input_list[i]] = i




# Input count

INPUT_COUNT = len(input_list)





def get_team_observation(game: Game, team: int, team_considered_units_map: List[List[Unit]]):
  team_observation = np.zeros((INPUT_COUNT, game.map.configs['height'], game.map.configs['width']))




  for y in range(game.map.configs['height']):
    for x in range(game.map.configs['width']):
      cell = game.map.get_cell(x, y)




      # Tile

      team_observation[INPUT_TILE_ROAD_LEVEL, y, x] = cell.get_road() / 6.0 * 2.0 - 1.0



      
      # Resources
      
      if cell.has_resource():
        team_observation[INPUT_RESOURCE_EXISTS, y, x] = 1.0
        
        team_observation[INPUT_RESOURCE_IS_WOOD, y, x] = float(cell.resource.type == 'wood') * 2.0 - 1.0
        team_observation[INPUT_RESOURCE_IS_COAL, y, x] = float(cell.resource.type == 'coal') * 2.0 - 1.0
        team_observation[INPUT_RESOURCE_IS_URANIUM, y, x] = float(cell.resource.type == 'uranium') * 2.0 - 1.0
        
        team_observation[INPUT_RESOURCE_AMOUNT, y, x] = cell.resource.amount / 350.0 * 2.0 - 1.0
      else:
        team_observation[INPUT_RESOURCE_EXISTS, y, x] = -1.0
        
        team_observation[INPUT_RESOURCE_IS_WOOD, y, x] = -1.0
        team_observation[INPUT_RESOURCE_IS_COAL, y, x] = -1.0
        team_observation[INPUT_RESOURCE_IS_URANIUM, y, x] = -1.0
        
        team_observation[INPUT_RESOURCE_AMOUNT, y, x] = -1.0


      
      
      # City tile

      citytile: CityTile = cell.city_tile

      if citytile:
        team_observation[INPUT_CITY_TILE_EXISTS, y, x] = 1.0

        team_observation[INPUT_CITY_TILE_COOLDOWN, y, x] = citytile.cooldown / 10.0 * 2.0 - 1.0
        team_observation[INPUT_CITY_TILE_CAN_ACT, y, x] = float(citytile.can_act()) * 2.0 - 1.0
      else:
        team_observation[INPUT_CITY_TILE_EXISTS, y, x] = -1.0

        team_observation[INPUT_CITY_TILE_COOLDOWN, y, x] = -1.0
        team_observation[INPUT_CITY_TILE_CAN_ACT, y, x] = -1.0



      
      # City

      city: City = None

      if citytile:
        city = game.cities[citytile.city_id]

        team_observation[INPUT_CITY_FUEL_AMOUNT, y, x] = city.fuel / 10000.0 * 2.0 - 1.0
        team_observation[INPUT_CITY_FUEL_UPKEEP, y, x] = city.get_light_upkeep() / 100.0 * 2.0 - 1.0
      else:
        team_observation[INPUT_CITY_FUEL_AMOUNT, y, x] = -1.0
        team_observation[INPUT_CITY_FUEL_UPKEEP, y, x] = -1.0
      
      
      
      
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

        team_observation[INPUT_UNIT_IS_WORKER, y, x] = float(considered_unit.is_worker()) * 2.0 - 1.0
        team_observation[INPUT_UNIT_IS_CART, y, x] = float(considered_unit.is_cart()) * 2.0 - 1.0

        team_observation[INPUT_UNIT_RESOURCE_SPACE, y, x] = considered_unit.get_cargo_space_left() / unit_resource_capacity * 2.0 - 1.0
        team_observation[INPUT_UNIT_FUEL_AMOUNT, y, x] = considered_unit.get_cargo_fuel_value() / unit_fuel_capacity * 2.0 - 1.0

        team_observation[INPUT_UNIT_COOLDOWN, y, x] = considered_unit.cooldown / unit_base_cooldown * 2.0 - 1.0
        team_observation[INPUT_UNIT_CAN_ACT, y, x] = float(considered_unit.can_act()) * 2.0 - 1.0
      else:

        team_observation[INPUT_UNIT_IS_WORKER, y, x] = -1.0
        team_observation[INPUT_UNIT_IS_CART, y, x] = -1.0

        team_observation[INPUT_UNIT_RESOURCE_SPACE, y, x] = -1.0
        team_observation[INPUT_UNIT_FUEL_AMOUNT, y, x] = -1.0

        team_observation[INPUT_UNIT_COOLDOWN, y, x] = -1.0
        team_observation[INPUT_UNIT_CAN_ACT, y, x] = -1.0




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
      
      team_observation[INPUT_OTHER_UNITS_COUNT, y, x] = unit_count
      team_observation[INPUT_OTHER_UNITS_WORKER_CART_RATIO, y, x] = cart_count / max(1.0, unit_count) * 2.0 - 1.0

      team_observation[INPUT_OTHER_UNITS_RESOURCE_SPACE, y, x] = total_resource_space / max(1.0, total_resource_capacity) * 2.0 - 1.0
      team_observation[INPUT_OTHER_UNITS_FUEL_AMOUNT, y, x] = total_fuel / max(1.0, total_fuel_capacity) * 2.0 - 1.0


      
      
      # Team

      aux_team = -1
      
      if considered_unit is not None:
        aux_team = int(considered_unit.team == team)
      elif citytile is not None:
        aux_team = int(citytile.team == team)

      team_observation[INPUT_TEAM_EXISTS, y, x] = float(aux_team != -1) * 2.0 - 1.0

      team_observation[INPUT_TEAM_IS_PLAYER, y, x] = float(aux_team == 1) * 2.0 - 1.0
      team_observation[INPUT_TEAM_IS_OPPONENT, y, x] = float(aux_team == 0) * 2.0 - 1.0




      # Player

      team_state = game.state['teamStates'][team]

      team_observation[INPUT_PLAYER_RESEARCH_POINTS, y, x] = team_state['researchPoints'] / 200.0 * 2.0 - 1.0
      team_observation[INPUT_PLAYER_RESEARCHED_COAL, y, x] = float(team_state['researched']['coal']) * 2.0 - 1.0
      team_observation[INPUT_PLAYER_RESEARCHED_URANIUM, y, x] = float(team_state['researched']['uranium']) * 2.0 - 1.0
      



      # Game

      team_observation[INPUT_GAME_CURRENT_TURN, y, x] = game.state['turn'] / 360.0 * 2.0 - 1.0




      team_observation[INPUT_GAME_IS_NIGHT, y, x] = float(game.is_night()) * 2.0 - 1.0
      
      turn_mod_40 = game.state['turn'] % 40

      if turn_mod_40 < 30:
        team_observation[INPUT_GAME_NIGHT_PERCENT, y, x] = turn_mod_40 / 30.0 * 2.0 - 1.0
      else:
        team_observation[INPUT_GAME_NIGHT_PERCENT, y, x] = (1.0 - (turn_mod_40 - 30.0) / 10.0) * 2.0 - 1.0



      city_tile_count = [0, 0]
      for city in game.cities.values():
        city_tile_count[city.team] += len(city.city_cells)

      team_observation[INPUT_GAME_CITY_TILE_RATIO, y, x] = (city_tile_count[team] / float(sum(city_tile_count))) * 2.0 - 1.0



  return torch.Tensor(team_observation).unsqueeze(0)