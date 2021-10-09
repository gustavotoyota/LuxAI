import math, sys
from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate



import numpy as np



DIRECTIONS = Constants.DIRECTIONS
game_state = None



LUX_NUM_INPUTS = 19





def agent(observation, configuration):
  global game_state

  ### Do not edit ###
  if observation["step"] == 0:
    game_state = Game()
    game_state._initialize(observation["updates"])
    game_state._update(observation["updates"][2:])
    game_state.id = observation.player
  else:
    game_state._update(observation["updates"])
  
  actions = []

  ### AI Code goes down here! ### 

  

  player = game_state.players[observation.player]
  opponent = game_state.players[(observation.player + 1) % 2]



  def generate_input():
    game_state = Game()
    
      

    input = np.zeros((game_state.map.width, game_state.map.height, LUX_NUM_INPUTS))




    action_list = []

    action_list.append('TileIsEmpty')
    action_list.append('TileIsResource')
    action_list.append('TileIsCity')

    action_list.append('ResourceIsWood')
    action_list.append('ResourceIsCoal')
    action_list.append('ResourceIsUranium')
    
    action_list.append('TeamIsNone')
    action_list.append('TeamIsPlayer')
    action_list.append('TeamIsOpponent')

    action_list.append('CityFuelAmount')
    action_list.append('CityFuelUpkeep')
    
    action_list.append('UnitIsNone')
    action_list.append('UnitIsWorker')
    action_list.append('UnitIsCart')

    action_list.append('UnitWoodAmount')
    action_list.append('UnitCoalAmount')
    action_list.append('UnitUraniumAmount')
    
    action_list.append('UnitResourceCapacity')
    
    action_list.append('ActorCooldown')
    action_list.append('ActorCanAct')
    
    action_list.append('PlayerResourcePoints')
    action_list.append('PlayerCanCollectCoal')
    action_list.append('PlayerCanCollectUranium')
    
    action_list.append('GameCurrentTurn')
    action_list.append('GameIsNight')
    action_list.append('GameNightPercent')
    action_list.append('GameCityTileRatio')




    action_map = {}
    for i in range(len(action_list)):
      action_map[action_list[i]] = i

    


    for unit in player.units:
      input[unit.pos.y, unit.pos.x, action_map['UnitIsWorker']] = float(unit.type == 0) * 2.0 - 1.0
      input[unit.pos.y, unit.pos.x, action_map['UnitIsCart']] = float(unit.type == 1) * 2.0 - 1.0

    for unit in opponent.units:
      input[unit.pos.y, unit.pos.x, action_map['UnitIsWorker']] = float(unit.type == 0) * 2.0 - 1.0
      input[unit.pos.y, unit.pos.x, action_map['UnitIsCart']] = float(unit.type == 1) * 2.0 - 1.0
      

    
    for y in range(game_state.map.height):
      for x in range(game_state.map.width):
        input[y, x, action_map['TileIsResource']] = float(game_state.map.get_cell(x, y).has_resource()) * 2.0 - 1.0
        input[y, x, action_map['TileIsCity']] = float(game_state.map.get_cell(x, y).citytile is not None) * 2.0 - 1.0
        
        input[y, x, action_map['TeamIsPlayer']] = float(game_state.map.get_cell(x, y).has_resource()) * 2.0 - 1.0




  







  width, height = game_state.map.width, game_state.map.height

  resource_tiles: list[Cell] = []
  for y in range(height):
    for x in range(width):
      cell = game_state.map.get_cell(x, y)
      if cell.has_resource():
        resource_tiles.append(cell)

  # we iterate over all our units and do something with them
  for unit in player.units:
    if unit.is_worker() and unit.can_act():
      closest_dist = math.inf
      closest_resource_tile = None
      if unit.get_cargo_space_left() > 0:
        # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
        for resource_tile in resource_tiles:
          if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
          if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
          dist = resource_tile.pos.distance_to(unit.pos)
          if dist < closest_dist:
            closest_dist = dist
            closest_resource_tile = resource_tile
        if closest_resource_tile is not None:
          actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
      else:
        # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
        if len(player.cities) > 0:
          closest_dist = math.inf
          closest_city_tile = None
          for k, city in player.cities.items():
            for city_tile in city.citytiles:
              dist = city_tile.pos.distance_to(unit.pos)
              if dist < closest_dist:
                closest_dist = dist
                closest_city_tile = city_tile
          if closest_city_tile is not None:
            move_dir = unit.pos.direction_to(closest_city_tile.pos)
            actions.append(unit.move(move_dir))

  # you can add debug annotations using the functions in the annotate object
  # actions.append(annotate.circle(0, 0))
  
  return actions
