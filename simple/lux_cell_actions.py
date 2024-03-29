from typing import List, Tuple




from luxai2021.game.constants import Constants
from luxai2021.game.actions import *
from luxai2021.game.cell import Cell
from luxai2021.game.city import City, CityTile
from luxai2021.game.game import DIRECTIONS, Game
from luxai2021.game.position import Position
from luxai2021.game.unit import Unit




import numpy as np




from lux_units import *





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





def get_team_valid_cell_actions(game: Game, team: int,
considered_units_map: List[List[Unit]]) -> List[Tuple]:
  team_valid_cell_actions = []
  


  # Cities

  for city in game.cities.values():
    city: City



    if city.team != team:
      continue



    for city_cell in city.city_cells:
      city_cell: Cell
      city_tile: CityTile = city_cell.city_tile



      if not city_tile.can_act():
        continue



      if not game.worker_unit_cap_reached(team):
        team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_BUILD_WORKER, city_tile.pos.y, city_tile.pos.x))
        team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_BUILD_CART, city_tile.pos.y, city_tile.pos.x))

      # if game.state["teamStates"][team]["researchPoints"] < 200:
      team_valid_cell_actions.append((CELL_ACTION_CITY_TILE_RESEARCH, city_tile.pos.y, city_tile.pos.x))




  # Units

  for unit in game.get_teams_units(team).values():
    unit: Unit



    if considered_units_map[unit.pos.y][unit.pos.x] != unit:
      continue



    if not unit.can_act():
      continue




    team_valid_cell_actions.append((CELL_ACTION_UNIT_DO_NOTHING, unit.pos.y, unit.pos.x))
    
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.NORTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_NORTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.WEST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_WEST, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.SOUTH):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_SOUTH, unit.pos.y, unit.pos.x))
    if is_move_action_valid(game, team, unit.pos, DIRECTIONS.EAST):
      team_valid_cell_actions.append((CELL_ACTION_UNIT_MOVE_EAST, unit.pos.y, unit.pos.x))




    # Smart transfer
    
    unit_cell = game.map.get_cell(unit.pos.x, unit.pos.y)

    for adjacent_cell in game.map.get_adjacent_cells(unit_cell):
      adjacent_cell: Cell

      for adjacent_unit in adjacent_cell.units.values():
        adjacent_unit: Unit

        if adjacent_unit.team != team:
          continue

        if adjacent_unit.get_cargo_space_left() == 0:
          continue

        team_valid_cell_actions.append((CELL_ACTION_UNIT_SMART_TRANSFER, unit.pos.y, unit.pos.x))

        break
        

    

    if unit.type == UNIT_TYPES.WORKER:
      if not unit_cell.is_city_tile():
        team_valid_cell_actions.append((CELL_ACTION_UNIT_BUILD_CITY, unit.pos.y, unit.pos.x))

        if unit_cell.get_road() > 0:
          team_valid_cell_actions.append((CELL_ACTION_UNIT_PILLAGE, unit.pos.y, unit.pos.x))



  
  return team_valid_cell_actions







def is_move_action_valid(game: Game, team: int, pos: Position, dir: DIRECTIONS) -> bool:
  target_pos = pos.translate(dir, 1)




  if target_pos.x < 0 or target_pos.x >= game.map.width:
    return False

  if target_pos.y < 0 or target_pos.y >= game.map.height:
    return False




  cell: Cell = game.map.get_cell_by_pos(target_pos)



  if cell.city_tile:
    return cell.city_tile.team == team



  return not cell.has_units()
  




def get_cell_action_mask(game: Game, valid_cell_actions):
  cell_action_mask = np.zeros((CELL_ACTION_COUNT, game.map.height, game.map.width), np.float32)


  for valid_cell_action in valid_cell_actions:
    cell_action_mask[valid_cell_action] = 1.0


  return cell_action_mask





def normalize_cell_action_probs(cell_action_probs, cell_action_mask):
  cell_action_probs *= cell_action_mask
  cell_action_probs /= max(1.0, np.sum(cell_action_probs).item())

  return cell_action_probs





def get_team_env_cell_action(cell_action: tuple, game: Game,
team: int, considered_units_map: List[List[Unit]]) -> Action:
  considered_unit = considered_units_map[cell_action[1]][cell_action[2]]




  # City tile actions

  game_action: Action = None

  if cell_action[0] == CELL_ACTION_CITY_TILE_BUILD_WORKER:
    game_action = SpawnWorkerAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == CELL_ACTION_CITY_TILE_BUILD_CART:
    game_action = SpawnCartAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == CELL_ACTION_CITY_TILE_RESEARCH:
    game_action = ResearchAction(team, cell_action[2], cell_action[1], 0)

  
  
  
  # Unit actions

  if considered_unit:
    if cell_action[0] == CELL_ACTION_UNIT_DO_NOTHING:
      game_action = MoveAction(team, considered_unit.id, DIRECTIONS.CENTER)

    elif cell_action[0] == CELL_ACTION_UNIT_MOVE_NORTH:
      game_action = MoveAction(team, considered_unit.id, DIRECTIONS.NORTH)
    elif cell_action[0] == CELL_ACTION_UNIT_MOVE_WEST:
      game_action = MoveAction(team, considered_unit.id, DIRECTIONS.WEST)
    elif cell_action[0] == CELL_ACTION_UNIT_MOVE_SOUTH:
      game_action = MoveAction(team, considered_unit.id, DIRECTIONS.SOUTH)
    elif cell_action[0] == CELL_ACTION_UNIT_MOVE_EAST:
      game_action = MoveAction(team, considered_unit.id, DIRECTIONS.EAST)

    elif cell_action[0] == CELL_ACTION_UNIT_SMART_TRANSFER:
      game_action = smart_transfer(game, team, considered_unit)



    elif cell_action[0] == CELL_ACTION_UNIT_BUILD_CITY: 
      game_action = SpawnCityAction(team, considered_unit.id)
    elif cell_action[0] == CELL_ACTION_UNIT_PILLAGE:
      game_action = PillageAction(team, considered_unit.id)



  return game_action





def smart_transfer(game: Game, team: int, unit: Unit, target_type_restriction=None, **kwarg):
  """
  Smart-transfers from the specified unit to a nearby neighbor. Prioritizes any
  nearby carts first, then any worker. Transfers the resource type which the unit
  has most of. Picks which cart/worker based on choosing a target that is most-full
  but able to take the most amount of resources.

  Args:
    team ([type]): [description]
    unit_id ([type]): [description]

  Returns:
    Action: Returns a TransferAction object, even if the request is an invalid
        transfer. Use TransferAction.is_valid() to check validity.
  """

  # Calculate how much resources could at-most be transferred
  resource_type = None
  resource_amount = 0
  target_unit: Unit = None

  if unit != None:
    for type, amount in unit.cargo.items():
      if amount > resource_amount:
        resource_type = type
        resource_amount = amount

    # Find the best nearby unit to transfer to
    unit_cell = game.map.get_cell_by_pos(unit.pos)
    adjacent_cells = game.map.get_adjacent_cells(unit_cell)

    
    for c in adjacent_cells:
      c: Cell

      for id, u in c.units.items():
        u: Unit

        # Apply the unit type target restriction
        if target_type_restriction == None or u.type == target_type_restriction:
          if u.team == team:
            # This unit belongs to our team, set it as the winning transfer target
            # if it's the best match.
            if target_unit is None:
              target_unit = u
            else:
              # Compare this unit to the existing target
              if target_unit.type == u.type:
                # Transfer to the target with the least capacity, but can accept
                # all of our resources
                if( u.get_cargo_space_left() >= resource_amount and 
                  target_unit.get_cargo_space_left() >= resource_amount ):
                  # Both units can accept all our resources. Prioritize one that is most-full.
                  if u.get_cargo_space_left() < target_unit.get_cargo_space_left():
                    # This new target it better, it has less space left and can take all our
                    # resources
                    target_unit = u
                  
                elif( target_unit.get_cargo_space_left() >= resource_amount ):
                  # Don't change targets. Current one is best since it can take all
                  # the resources, but new target can't.
                  pass
                  
                elif( u.get_cargo_space_left() > target_unit.get_cargo_space_left() ):
                  # Change targets, because neither target can accept all our resources and 
                  # this target can take more resources.
                  target_unit = u
              elif u.type == Constants.UNIT_TYPES.CART:
                # Transfer to this cart instead of the current worker target
                target_unit = u
  
  # Build the transfer action request
  target_unit_id = None
  if target_unit is not None:
    target_unit_id = target_unit.id

    # Update the transfer amount based on the room of the target
    if target_unit.get_cargo_space_left() < resource_amount:
      resource_amount = target_unit.get_cargo_space_left()
  
  return TransferAction(team, unit.id, target_unit_id, resource_type, resource_amount)