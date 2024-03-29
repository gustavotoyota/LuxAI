from typing import List
from luxai2021.game.game import Game
from luxai2021.game.unit import Unit




def get_considered_units_map(game: Game) -> List[List[Unit]]:
  considered_units_map = []




  for _ in range(game.map.height):
    considered_units_row = []
    considered_units_map.append(considered_units_row)

    for _ in range(game.map.width):
      considered_units_row.append(None)



  for team in range(2):
    for unit in game.get_teams_units(team).values():
      unit: Unit

      if considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      considered_units_map[unit.pos.y][unit.pos.x] = unit



  return considered_units_map