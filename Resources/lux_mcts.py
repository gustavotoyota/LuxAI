import math



class MCTSNode():
  def __init__(self, mcts, parent, prior_prob):
    self.mcts: MCTS = mcts
    self.parent: MCTSNode = parent

    self.prior_prob = prior_prob
    self.num_visits = 0

    self.cumul_value = 0.0

    self.children = {}
    

    
  def expand(self, action_prior_probs):
    for action, prior_prob in action_prior_probs:
      if action not in self.children:
        self.children[action] = MCTSNode(self, prior_prob)



  def backup(self, leaf_value):
    if self.parent is not None:
      self.parent.backup(leaf_value)

    self.num_visits += 1
    self.cumul_value += leaf_value



  def select(self):
    return max(self.children.items, key=lambda node: node.get_value())



  def get_value(self):
    mean_value = self.cumul_value / self.num_visits

    adjusted_prior_prob = (self.mcts.c_puct * self.prior_prob *
      math.sqrt(self.parent.num_visits) / (1.0 + self.num_visits))

    return mean_value + adjusted_prior_prob


  
  def is_leaf(self):
    return len(self.children) == 0


  
  def is_root(self):
    return self.parent is None




class MCTS():
  def __init__(self, model):
    self.model = model

    self.root = MCTSNode(None, None, 1.0)

    self.c_puct = 5 # Constant of the Polynomial Upper Confidence Bound for Trees

    self.num_playouts = 600




  def playout(self):
    node = self.root



    while not node.is_leaf():
      action, node = node.select()

      # Execute action
    
    

    action_probs, value = self.model()
    