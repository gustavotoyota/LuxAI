from luxai2021.game.game import Game


from lux_model import *



import math



class MCTS():
  def __init__(self, model: LuxModel, game: Game):
    self.model = model

    self.root = MCTSNode(self)

    self.c_puct = 1.0

    self.game = game




  def playout(self):
    node: MCTSNode = self.root

    while not node.is_leaf():
      action, node = node.select_child()

    self.game.run_turn_with_actions()

    node.expand()
  




class MCTSNode():
  def __init__(self, mcts: MCTS, parent, prior_prob: float):
    self.mcts = mcts

    self.parent: MCTSNode = parent

    self.prior_prob = prior_prob # Multiplied probability of both player's actions
    self.num_visits = 0

    self.cumul_value = 0.0

    self.children: Dict[tuple, MCTSNode] = {} # Cross product of both player's actions




  def select_child(self):
    return max(self.children.items(), key=lambda node: node[1].get_value())




  def expand(self):



    pass


  
  def get_value(self):
    mean_value = self.cumul_value / self.num_visits

    adjusted_prior_prob = (self.mcts.c_puct * self.prior_prob *
      math.sqrt(self.parent.num_visits) / (1.0 + self.num_visits))

    return mean_value + adjusted_prior_prob



  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children

  



def run_mcts(model: LuxModel, game: Game, updates: list):
  pass