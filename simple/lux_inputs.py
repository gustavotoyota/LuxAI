import torch
from luxai2021.game.city import City, CityTile
from luxai2021.game.game import Game
from luxai2021.game.unit import Unit



import numpy as np



from lux_inputs import *
from lux_units import *





# Inputs

INPUT_COUNT = 0

def add_input():
  global INPUT_COUNT
  INPUT_COUNT += 1
  return INPUT_COUNT - 1



INPUT_TILE_ROAD_LEVEL = add_input()



INPUT_RESOURCE_EXISTS = add_input()

INPUT_RESOURCE_IS_WOOD = add_input()
INPUT_RESOURCE_IS_COAL = add_input()
INPUT_RESOURCE_IS_URANIUM = add_input()

INPUT_RESOURCE_AMOUNT = add_input()




INPUT_TEAM_EXISTS = add_input()

INPUT_TEAM_IS_PLAYER = add_input()
INPUT_TEAM_IS_OPPONENT = add_input()




INPUT_CITY_TILE_EXISTS = add_input()

INPUT_CITY_TILE_COOLDOWN = add_input()
INPUT_CITY_TILE_CAN_ACT = add_input()




INPUT_CITY_FUEL_AMOUNT = add_input()
INPUT_CITY_FUEL_UPKEEP = add_input()




INPUT_UNIT_IS_WORKER = add_input()
INPUT_UNIT_IS_CART = add_input()

INPUT_UNIT_RESOURCE_SPACE = add_input()
INPUT_UNIT_FUEL_AMOUNT = add_input()

INPUT_UNIT_COOLDOWN = add_input()
INPUT_UNIT_CAN_ACT = add_input()




INPUT_OTHER_UNITS_COUNT = add_input()
INPUT_OTHER_UNITS_WORKER_CART_RATIO = add_input()

INPUT_OTHER_UNITS_RESOURCE_SPACE = add_input()
INPUT_OTHER_UNITS_FUEL_AMOUNT = add_input()




INPUT_PLAYER_RESEARCH_POINTS = add_input()

INPUT_PLAYER_RESEARCHED_COAL = add_input()
INPUT_PLAYER_RESEARCHED_URANIUM = add_input()




INPUT_GAME_CURRENT_TURN = add_input()

INPUT_GAME_IS_NIGHT = add_input()
INPUT_GAME_NIGHT_PERCENT = add_input()

INPUT_GAME_CITY_TILE_RATIO = add_input()





def get_team_observation(game: Game, team: int, considered_units_map: List[List[Unit]]):
  team_observation = np.zeros((INPUT_COUNT, game.map.height, game.map.width))




  for y in range(game.map.height):
    for x in range(game.map.width):
      cell = game.map.get_cell(x, y)




      # Tile

      team_observation[INPUT_TILE_ROAD_LEVEL, y, x] = cell.get_road() / 6.0 * 2.0 - 1.0



      
      # Resources
      
      if cell.has_resource():
        team_observation[INPUT_RESOURCE_EXISTS, y, x] = 1.0
        
        team_observation[INPUT_RESOURCE_IS_WOOD, y, x] = float(cell.resource.type == 'wood') * 2.0 - 1.0
        team_observation[INPUT_RESOURCE_IS_COAL, y, x] = float(cell.resource.type == 'coal') * 2.0 - 1.0
        team_observation[INPUT_RESOURCE_IS_URANIUM, y, x] = float(cell.resource.type == 'uranium') * 2.0 - 1.0
        
        team_observation[INPUT_RESOURCE_AMOUNT, y, x] = cell.resource.amount / 800.0 * 2.0 - 1.0
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

      considered_unit: Unit = considered_units_map[y][x]

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

      team_observation[INPUT_GAME_CITY_TILE_RATIO, y, x] = city_tile_count[team] / max(1.0, sum(city_tile_count)) * 2.0 - 1.0



  return torch.Tensor(team_observation).unsqueeze(0)