from typing import List




import luxai2021.game.game
import luxai2021.game.constants
import luxai2021.game.unit
import luxai2021.game.actions
import luxai2021.game.cell




import lux_cell_actions





CITY_ENGINE_ACTIONS = {
  luxai2021.game.constants.Constants.ACTIONS.BUILD_WORKER,
  luxai2021.game.constants.Constants.ACTIONS.BUILD_CART,
  luxai2021.game.constants.Constants.ACTIONS.RESEARCH }





def is_engine_action_valid(engine_action: luxai2021.game.actions.Action,
game: luxai2021.game.game.Game, engine_actions: List[luxai2021.game.actions.Action]):
  if not engine_action:
    return False




  if engine_action.action in CITY_ENGINE_ACTIONS:
    if not game.map.get_cell(engine_action.x, engine_action.y).city_tile:
      return False
  else:
    if engine_action.action == luxai2021.game.constants.Constants.ACTIONS.TRANSFER:
      if not engine_action.source_id in game.get_teams_units(engine_action.team):
        return False
      
      if not engine_action.destination_id in game.get_teams_units(engine_action.team):
        return False
    else:
      if not engine_action.unit_id in game.get_teams_units(engine_action.team):
        return False




  if not engine_action.is_valid(game, engine_actions):
    return False




  if engine_action.action == luxai2021.game.constants.Constants.ACTIONS.MOVE:
    src_unit: luxai2021.game.unit.Unit = game.get_unit(engine_action.team, engine_action.unit_id)

    target_pos = src_unit.pos.translate(engine_action.direction, 1)
    target_cell = game.map.get_cell_by_pos(target_pos)

    if target_cell.city_tile and target_cell.city_tile.team != src_unit.team:
      return False




  return True





def get_team_engine_actions(cell_actions: List[tuple], engine_game: luxai2021.game.game.Game,
team: int, considered_units_map: List[List[luxai2021.game.unit.Unit]]) -> List[luxai2021.game.actions.Action]:
  team_engine_actions = []



  for cell_action in cell_actions:
    team_engine_action = get_team_engine_action(cell_action, engine_game, team, considered_units_map)

    if team_engine_action:
      team_engine_actions.append(team_engine_action)



  return team_engine_actions





def get_team_engine_action(cell_action: tuple, game: luxai2021.game.game.Game,
team: int, considered_units_map: List[List[luxai2021.game.unit.Unit]]) -> luxai2021.game.actions.Action:
  team_engine_action: luxai2021.game.actions.Action = None




  # City tile actions

  if cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_BUILD_WORKER:
    team_engine_action = luxai2021.game.actions.SpawnWorkerAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_BUILD_CART:
    team_engine_action = luxai2021.game.actions.SpawnCartAction(team, 0, cell_action[2], cell_action[1])
  elif cell_action[0] == lux_cell_actions.CELL_ACTION_CITY_TILE_RESEARCH:
    team_engine_action = luxai2021.game.actions.ResearchAction(team, cell_action[2], cell_action[1], 0)

  
  
  
  # Unit actions

  considered_unit = considered_units_map[cell_action[1]][cell_action[2]]

  if considered_unit:
    if cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_DO_NOTHING:
      team_engine_action = luxai2021.game.actions.MoveAction(team, considered_unit.id, luxai2021.game.game.DIRECTIONS.CENTER)

    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_NORTH:
      team_engine_action = luxai2021.game.actions.MoveAction(team, considered_unit.id, luxai2021.game.game.DIRECTIONS.NORTH)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_WEST:
      team_engine_action = luxai2021.game.actions.MoveAction(team, considered_unit.id, luxai2021.game.game.DIRECTIONS.WEST)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_SOUTH:
      team_engine_action = luxai2021.game.actions.MoveAction(team, considered_unit.id, luxai2021.game.game.DIRECTIONS.SOUTH)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_MOVE_EAST:
      team_engine_action = luxai2021.game.actions.MoveAction(team, considered_unit.id, luxai2021.game.game.DIRECTIONS.EAST)

    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_SMART_TRANSFER:
      team_engine_action = smart_transfer(game, team, considered_unit)



    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_BUILD_CITY: 
      team_engine_action = luxai2021.game.actions.SpawnCityAction(team, considered_unit.id)
    elif cell_action[0] == lux_cell_actions.CELL_ACTION_UNIT_PILLAGE:
      team_engine_action = luxai2021.game.actions.PillageAction(team, considered_unit.id)




  return team_engine_action





def smart_transfer(game: luxai2021.game.game.Game, team: int, unit: luxai2021.game.unit.Unit, target_type_restriction=None, **kwarg):
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
  target_unit: luxai2021.game.unit.Unit = None

  if unit != None:
    for type, amount in unit.cargo.items():
      if amount > resource_amount:
        resource_type = type
        resource_amount = amount

    # Find the best nearby unit to transfer to
    unit_cell = game.map.get_cell_by_pos(unit.pos)
    adjacent_cells = game.map.get_adjacent_cells(unit_cell)

    
    for c in adjacent_cells:
      c: luxai2021.game.cell.Cell

      for id, u in c.units.items():
        u: luxai2021.game.unit.Unit

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
              elif u.type == luxai2021.game.constants.Constants.UNIT_TYPES.CART:
                # Transfer to this cart instead of the current worker target
                target_unit = u
  
  # Build the transfer action request
  target_unit_id = None
  if target_unit is not None:
    target_unit_id = target_unit.id

    # Update the transfer amount based on the room of the target
    if target_unit.get_cargo_space_left() < resource_amount:
      resource_amount = target_unit.get_cargo_space_left()
  
  return luxai2021.game.actions.TransferAction(team, unit.id, target_unit_id, resource_type, resource_amount)