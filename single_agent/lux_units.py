from typing import List

import numpy as np



import luxai2021.game.game
import luxai2021.game.unit




def get_considered_units_map(engine_game: luxai2021.game.game.Game) -> np.array:
  considered_units_map = np.full(
    (engine_game.map.height, engine_game.map.width), None, dtype=object)



  for team in range(2):
    for unit in engine_game.get_teams_units(team).values():
      unit: luxai2021.game.unit.Unit

      if considered_units_map[unit.pos.y, unit.pos.x]:
        continue

      considered_units_map[unit.pos.y, unit.pos.x] = unit



  return considered_units_map