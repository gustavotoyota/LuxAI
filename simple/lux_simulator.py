from luxai2021.game.game import Game



class LuxSimulator():
  def __init__(self, configs: dict, updates: list):
    self.game = Game(configs)

    self.updates = updates


  
  def reset(self):
    self.game.reset(self.updates)



  