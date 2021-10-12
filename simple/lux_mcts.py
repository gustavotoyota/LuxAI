from luxai2021.game.game import Game


from lux_model import *




class MCTS():
  def __init__(self, model: LuxModel):
    self.model = model

    self.root = MCTSNode(self)

  
  def select():
    pass




class MCTSNode():
  def __init__(self, mcts: MCTS, parent, prior_prob: float):
    self.mcts = mcts

    self.parent: MCTSNode = parent

    self.prior_prob = prior_prob
    self.num_visits = 0

    self.cumul_value = 0.0

    self.children = {}



  def expand(self):
    pass

  



def run_mcts(model: LuxModel, game: Game, updates: list):
  pass