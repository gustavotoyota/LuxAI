from typing import List




import luxai2021.game.game as lux_engine_game
import luxai2021.game.constants as lux_engine_constants
import luxai2021.game.unit as lux_engine_unit
import luxai2021.game.actions as lux_engine_actions
import luxai2021.game.cell as lux_engine_cell




import lux_cell_actions






def is_env_action_valid(env_action: lux_engine_actions.Action,
game: lux_engine_game.Game, lux_engine_actions: List[lux_engine_actions.Action]):
  if not env_action:
    return False




  if env_action.action in {lux_engine_constants.Constants.ACTIONS.BUILD_WORKER,
    lux_engine_constants.Constants.ACTIONS.BUILD_CART, lux_engine_constants.Constants.ACTIONS.RESEARCH}:
    if not game.map.get_cell(env_action.x, env_action.y).city_tile:
      return False
  else:
    if env_action.action == lux_engine_constants.Constants.ACTIONS.TRANSFER:
      if not env_action.source_id in game.get_teams_units(env_action.team):
        return False
      
      if not env_action.destination_id in game.get_teams_units(env_action.team):
        return False
    else:
      if not env_action.unit_id in game.get_teams_units(env_action.team):
        return False

  if not env_action.is_valid(game, lux_engine_actions):
    return False




  if env_action.action == lux_engine_constants.Constants.ACTIONS.MOVE:
    src_unit: lux_engine_unit.Unit = game.get_unit(env_action.team, env_action.unit_id)

    target_pos = src_unit.pos.translate(env_action.direction, 1)
    target_cell = game.map.get_cell_by_pos(target_pos)

    if target_cell.city_tile and target_cell.city_tile.team != src_unit.team:
      return False




  return True





def get_team_env_cell_action(cell_action: tuple, game: lux_engine_game.Game,
team: int, considered_units_map: List[List[lux_engine_unit.Unit]]) -> lux_engine_actions.Action:
  considered_unit = considered_units_map[cell_action[1]][cell_action[2]]




  # env_city.City tile actions

  game_action: lux_engine_actions.Action = None

  if cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_BUILD_WORKER:
    game_action = lux_engine_actions.SpawnWorkerAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_BUILD_CART:
    game_action = lux_engine_actions.SpawnCartAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_RESEARCH:
    game_action = lux_engine_actions.ResearchAction(team, cell_action[2], cell_action[1], 0)

  
  
  
  # Unit actions

  if considered_unit:
    if cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_DO_NOTHING:
      game_action = lux_engine_actions.MoveAction(team, considered_unit.id, lux_engine_game.DIRECTIONS.CENTER)

    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_NORTH:
      game_action = lux_engine_actions.MoveAction(team, considered_unit.id, lux_engine_game.DIRECTIONS.NORTH)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_WEST:
      game_action = lux_engine_actions.MoveAction(team, considered_unit.id, lux_engine_game.DIRECTIONS.WEST)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_SOUTH:
      game_action = lux_engine_actions.MoveAction(team, considered_unit.id, lux_engine_game.DIRECTIONS.SOUTH)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_EAST:
      game_action = lux_engine_actions.MoveAction(team, considered_unit.id, lux_engine_game.DIRECTIONS.EAST)

    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_SMART_TRANSFER:
      game_action = smart_transfer(game, team, considered_unit)



    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_BUILD_CITY: 
      game_action = lux_engine_actions.SpawnCityAction(team, considered_unit.id)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_PILLAGE:
      game_action = lux_engine_actions.PillageAction(team, considered_unit.id)



  return game_action





def smart_transfer(game: lux_engine_game.Game, team: int, unit: lux_engine_unit.Unit, target_type_restriction=None, **kwarg):
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
  target_unit: lux_engine_unit.Unit = None

  if unit != None:
    for type, amount in unit.cargo.items():
      if amount > resource_amount:
        resource_type = type
        resource_amount = amount

    # Find the best nearby unit to transfer to
    unit_cell = game.map.get_cell_by_pos(unit.pos)
    adjacent_cells = game.map.get_adjacent_cells(unit_cell)

    
    for c in adjacent_cells:
      c: lux_engine_cell.Cell

      for id, u in c.units.items():
        u: lux_engine_unit.Unit

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
              elif u.type == lux_engine_constants.Constants.UNIT_TYPES.CART:
                # Transfer to this cart instead of the current worker target
                target_unit = u
  
  # Build the transfer action request
  target_unit_id = None
  if target_unit is not None:
    target_unit_id = target_unit.id

    # Update the transfer amount based on the room of the target
    if target_unit.get_cargo_space_left() < resource_amount:
      resource_amount = target_unit.get_cargo_space_left()
  
  return lux_engine_actions.TransferAction(team, unit.id, target_unit_id, resource_type, resource_amount)