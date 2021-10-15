


import json



from lux_inputs import *



from lux.game import Game
from lux.game_objects import Unit, City, CityTile
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate




def study_replay(file_path):
  with open(file_path) as f:
    replay = json.load(f)




  game = Game()

  game._initialize(replay['steps'][0][0]['observation']['updates'])

  for step in replay['steps']:
    game._update(step[0]['observation']['updates'])
    
    considered_units_map = get_replay_considered_units_map(game)

    team_observation = get_replay_team_observation(game, 0, considered_units_map)
    team_observation = get_replay_team_observation(game, 1, considered_units_map)





def get_replay_considered_units_map(game: Game) -> List[List[Unit]]:
  considered_units_map = []




  for _ in range(game.map.height):
    considered_units_row = []
    considered_units_map.append(considered_units_row)

    for _ in range(game.map.width):
      considered_units_row.append(None)



  for team in range(2):
    for unit in game.players[team].units:
      unit: Unit

      if considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      considered_units_map[unit.pos.y][unit.pos.x] = unit



  return considered_units_map



def get_replay_team_observation(game: Game, team: int, considered_units_map: List[List[Unit]]):
  team_observation = np.zeros((INPUT_COUNT, game.map.height, game.map.width))




  # Units map

  units_map: List[List[List[Unit]]] = [None] * game.map.height

  for y in range(game.map.height):
    units_row: List[List[Unit]] = [None] * game.map.width
    units_map[y] = units_row
    
    for x in range(game.map.width):
      units_cell: List[Unit] = []
      units_row[x] = units_cell

  for team in range(2):
    for unit in game.players[team].units:
      units_map[y][x].append(unit)




  for y in range(game.map.height):
    for x in range(game.map.width):
      cell = game.map.get_cell(x, y)




      # Tile

      team_observation[INPUT_TILE_ROAD_LEVEL, y, x] = cell.road / 6.0 * 2.0 - 1.0



      
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

      citytile: CityTile = cell.citytile

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
        city = game.players[0].cities.get(citytile.cityid)
        if not city:
          city = game.players[1].cities.get(citytile.cityid)

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
        
        cargo_fuel = considered_unit.cargo.wood
        cargo_fuel += considered_unit.cargo.coal * 10
        cargo_fuel += considered_unit.cargo.uranium * 40

        team_observation[INPUT_UNIT_FUEL_AMOUNT, y, x] = cargo_fuel / unit_fuel_capacity * 2.0 - 1.0

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

      for unit in units_map[y][x]:
        unit: Unit

        if unit.team != team:
          continue

        if unit == considered_unit:
          continue

        unit_count = unit_count + 1

        if unit.is_cart():
          cart_count = cart_count + 1
          
        cargo_fuel = unit.cargo.wood
        cargo_fuel += unit.cargo.coal * 10
        cargo_fuel += unit.cargo.uranium * 40

        total_fuel += cargo_fuel

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

      team_observation[INPUT_PLAYER_RESEARCH_POINTS, y, x] = game.players[team].research_points / 200.0 * 2.0 - 1.0
      team_observation[INPUT_PLAYER_RESEARCHED_COAL, y, x] = float(game.players[team].researched_coal()) * 2.0 - 1.0
      team_observation[INPUT_PLAYER_RESEARCHED_URANIUM, y, x] = float(game.players[team].researched_uranium()) * 2.0 - 1.0
      



      # Game

      team_observation[INPUT_GAME_CURRENT_TURN, y, x] = game.turn / 360.0 * 2.0 - 1.0



      
      turn_mod_40 = game.turn % 40

      team_observation[INPUT_GAME_IS_NIGHT, y, x] = float(turn_mod_40 >= 30) * 2.0 - 1.0

      if turn_mod_40 < 30:
        team_observation[INPUT_GAME_NIGHT_PERCENT, y, x] = turn_mod_40 / 30.0 * 2.0 - 1.0
      else:
        team_observation[INPUT_GAME_NIGHT_PERCENT, y, x] = (1.0 - (turn_mod_40 - 30.0) / 10.0) * 2.0 - 1.0



      team_observation[INPUT_GAME_CITY_TILE_RATIO, y, x] = game.players[team].city_tile_count / \
        (game.players[0].city_tile_count + game.players[1].city_tile_count) * 2.0 - 1.0



  return torch.Tensor(team_observation).unsqueeze(0)



study_replay('27583628.json')