# Input list

input_list = []



input_list.append('TileRoadLevel')



input_list.append('ResourceExists')

input_list.append('ResourceIsWood')
input_list.append('ResourceIsCoal')
input_list.append('ResourceIsUranium')

input_list.append('ResourceAmount')



input_list.append('TeamExists')

input_list.append('TeamIsPlayer')
input_list.append('TeamIsOpponent')



input_list.append('CityTileExists')

input_list.append('CityTileCooldown')
input_list.append('CityTileCanAct')



input_list.append('CityFuelAmount')
input_list.append('CityFuelUpkeep')



input_list.append('UnitExists')

input_list.append('UnitIsWorker')
input_list.append('UnitIsCart')

input_list.append('UnitWoodAmount')
input_list.append('UnitCoalAmount')
input_list.append('UnitUraniumAmount')

input_list.append('UnitResourceCapacity')

input_list.append('UnitCooldown')
input_list.append('UnitCanAct')



input_list.append('PlayerResourcePoints')

input_list.append('PlayerResearchedCoal')
input_list.append('PlayerResearchedUranium')



input_list.append('GameCurrentTurn')

input_list.append('GameIsNight')
input_list.append('GameNightPercent')

input_list.append('GameCityTileRatio')




# Input map

input_map = {}
for i in range(len(input_list)):
  input_map[input_list[i]] = i




# Input count

INPUT_COUNT = len(input_list)





def prep_input(value, dep=True):
  if not dep:
    return -1.0

  if callable(value):
    return float(value()) * 2.0 - 1.0
  
  return float(value) * 2.0 - 1.0