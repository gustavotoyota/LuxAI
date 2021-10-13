from luxai2021.game.cell import Cell
from luxai2021.game.unit import Unit



def get_cell_team(cell: Cell) -> int:
  if cell.city_tile:
    return cell.city_tile.team

  for _, unit in cell.units:
    unit: Unit
    return unit.team

  return None