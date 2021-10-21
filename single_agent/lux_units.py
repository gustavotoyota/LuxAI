from typing import List




import luxai2021.game.game
import luxai2021.game.unit




def get_considered_units_map(engine_game: luxai2021.game.game.Game) -> List[List[luxai2021.game.unit.Unit]]:
  considered_units_map = [
    [
      [None] for _ in range(engine_game.map.width)
    ] for _ in range(engine_game.map.height)
  ]



  for team in range(2):
    for unit in engine_game.get_teams_units(team).values():
      unit: luxai2021.game.unit.Unit

      if considered_units_map[unit.pos.y][unit.pos.x]:
        continue

      considered_units_map[unit.pos.y][unit.pos.x] = unit



  return considered_units_map