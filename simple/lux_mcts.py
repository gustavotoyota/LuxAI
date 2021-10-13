from lux_actions import get_game_actions
from luxai2021.game.game import Game




from lux_model import *
from lux_actions import *




import math




class MCTS():
  def __init__(self, model: LuxModel, game: Game):
    self.model = model

    self.game: Game = game

    self.num_iterations = 500
    self.c_puct = 1.0




  def reset(self, updates):
    self.root: MCTSNode = MCTSNode(self)
    self.updates = updates




  def run(self):
    for _ in range(self.num_iterations):
      self.playout()

    best_child = max(self.root.children, key=lambda child: child.num_visits)

    return best_child.team_actions[0]




  def playout(self):
    node: MCTSNode = self.root

    self.game.reset(self.updates)

    while not node.is_leaf():
      node = node.select_child()
      
      self.game.run_turn_with_actions(node.team_actions[0] + node.team_actions[1])

    leaf_value = node.expand()

    node.backup(leaf_value)
  




class MCTSNode():
  def __init__(self, mcts: MCTS, parent = None,
  team_actions: Tuple[List, List] = None, prior_prob: float = 0):
    self.mcts = mcts

    self.parent: MCTSNode = parent

    self.team_actions: Tuple[List, List] = team_actions

    self.prior_prob = prior_prob # Multiplied probability of both teams' actions
    self.num_visits = 0

    self.cumul_value = 0.0

    self.children: List[MCTSNode] = {}




  def select_child(self):
    return max(self.children, key=lambda child: child.get_value())

  def get_value(self):
    mean_value = self.cumul_value / self.num_visits

    adjusted_prior_prob = (self.mcts.c_puct * self.prior_prob *
      math.sqrt(self.parent.num_visits) / (1.0 + self.num_visits))

    return mean_value + adjusted_prior_prob




  def expand(self):
    team_values = [0.0, 0.0]

    team_actions = []
    team_action_probs = []




    # Get team actions and probabilities

    for team in range(2):
      observation = get_team_observation(self.mcts.game, team)

      cell_action_probs, team_values[team] = self.mcts.model(observation)

      considered_units_map = get_team_considered_units_map(self.mcts.game, team)
      valid_cell_actions = get_team_valid_cell_actions(self.mcts.game, team, considered_units_map)

      cell_action_mask = get_cell_action_mask(self.mcts.game, valid_cell_actions)
      cell_action_probs = normalize_cell_action_probs(cell_action_probs, cell_action_mask)

      actions = get_team_actions(self.mcts.game, team, cell_action_probs, valid_cell_actions)
      action_probs = get_action_probs(actions, cell_action_probs)

      team_actions.append(actions)
      team_action_probs.append(action_probs)




    # Create children

    for i in range(len(team_actions[0])):
      for j in range(len(team_actions[1])):
        child_actions = (team_actions[0][i], team_actions[0][j])
        child_prob = team_action_probs[0][i] * team_action_probs[1][j]

        child = MCTSNode(self.mcts, self, child_actions, child_prob)

        self.children.append(child)



    return (team_values[0] - team_values[1]) / 2.0




  def backup(self, leaf_value):
    self.num_visits += 1

    self.cumul_value += leaf_value

    if not self.is_root():
      self.parent.backup(leaf_value)




  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children