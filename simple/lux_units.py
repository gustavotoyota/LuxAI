from typing import List
from luxai2021.game.game import Game
from luxai2021.game.unit import Unit




def get_team_considered_units_map(game: Game, team: int) -> List[List[Unit]]:
  considered_units_map = []




  for _ in range(game.map.configs['height']):
    considered_units_row = []
    considered_units_map.append(considered_units_row)

    for _ in range(game.map.configs['width']):
      considered_units_row.append(None)



  for unit in game.get_teams_units(team):
    unit: Unit

    if unit.team != team:
      continue

    if considered_units_map[unit.pos.y][unit.pos.x]:
      continue

    considered_units_map[unit.pos.y][unit.pos.x] = unit



  return considered_units_map