


import json



from lux.game import Game
from lux.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate



def study_replay(file_path):
  with open(file_path) as f:
    replay = json.load(f)



  game = Game()

  game._initialize(replay['steps'][0][0]['observation']['updates'])
  replay['steps'][0][0]['observation']['updates'] = replay['steps'][0][0]['observation']['updates'][2:]

  for step in replay['steps']:
    game._update(step[0]['observation']['updates'])



study_replay('27583628.json')