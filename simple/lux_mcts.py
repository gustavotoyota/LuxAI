from luxai2021.game.game import Game




from lux_model import *
from lux_actions import *




import math
import copy




from timeit import default_timer as timer




class MCTS():
  def __init__(self, model: LuxModel):
    self.model: LuxModel = model

    self.num_iterations = 500
    self.c_puct = 10.0

    self.root = None




  def run(self, game: Game) -> List[tuple]:
    if not self.root:
      self.root: MCTSNode = MCTSNode(self)
      self.root.game = game

      self.root_cumul_value = 0.0
      self.root_num_visits = 0

    while self.root_num_visits < self.num_iterations:
      self.playout()

    child_indices = [None, None]
    for team in range(2):
      child_indices[team] = np.argmax(self.root.children_num_visits.sum(1 - team))

    best_child = self.root.children[child_indices[0]][child_indices[1]]
    
    self.root_cumul_value = self.root.children_cumul_values[child_indices[0]][child_indices[1]]
    self.root_num_visits = self.root.children_num_visits[child_indices[0]][child_indices[1]]

    self.root = best_child

    return best_child.team_actions




  def playout(self):
    node: MCTSNode = self.root

    current_game = self.root.game

    while not node.is_leaf():
      node = node.select_child()
      
      if node.game:
        current_game = node.game
        continue

      current_game.log_file = None
      node.game = copy.deepcopy(current_game)
      node.game.stop_replay_logging()

      considered_units_map = get_considered_units_map(node.game)
      env_actions = get_env_actions(node.game, node.team_actions, considered_units_map)
    
      node.game.run_turn_with_actions(env_actions)

      current_game = node.game

    if not current_game.match_over():
      leaf_value = node.expand()
    else:
      leaf_value = float(current_game.get_winning_team() == 0)

    node.backup(leaf_value)
  




class MCTSNode():
  def __init__(self, mcts: MCTS, parent = None, index: int = 0,
  team_actions: Tuple[List, List] = None):
    self.mcts = mcts

    self.parent: MCTSNode = parent
    self.index = index

    self.game: Game = None

    self.children: List[MCTSNode] = None

    self.children_prior_probs = None
    self.children_cumul_values = None
    self.children_num_visits = None

    self.team_actions: Tuple[List, List] = team_actions




  def select_child(self):
    child_indices = [None, None]

    for team in range(2):
      mean_values = self.children_cumul_values.sum(1 - team) / np.maximum(1.0, self.children_num_visits.sum(1 - team))

      if self.is_root():
        parent_num_visits = self.mcts.root_num_visits
      else:
        parent_num_visits = self.parent.children_num_visits[self.index[0]][self.index[1]]

      adjusted_prior_probs = self.mcts.c_puct * self.children_prior_probs[team] * \
        math.sqrt(parent_num_visits) / (1.0 + self.children_num_visits.sum(1 - team))

      ucb_scores = (-team * 2.0 + 1.0) * mean_values + adjusted_prior_probs

      child_indices[team] = np.argmax(ucb_scores)

    return self.children[child_indices[0]][child_indices[1]]




  def expand(self):
    team_values = [None, None]

    team_actions_list = [None, None]
    team_actions_probs = [None, None]




    # Get team actions and probabilities
    
    considered_units_map = get_considered_units_map(self.game)

    for team in range(2):
      team_observation = get_team_observation(self.game, team, considered_units_map)
      team_observation = (team_observation - self.mcts.model.input_mean) / self.mcts.model.input_std

      team_cell_action_probs, team_value = self.mcts.model(team_observation)
      team_cell_action_probs: Tensor; team_value: Tensor

      team_cell_action_probs = team_cell_action_probs.detach().view(CELL_ACTION_COUNT, \
        self.game.map.width, self.game.map.height).cpu().numpy()
      team_values[team] = team_value.item()

      team_valid_cell_actions = get_team_valid_cell_actions(self.game, team, considered_units_map)

      team_cell_action_mask = get_cell_action_mask(self.game, team_valid_cell_actions)
      team_cell_action_probs = normalize_cell_action_probs(team_cell_action_probs, team_cell_action_mask)

      team_actions_list[team] = get_team_actions(team_cell_action_probs, team_valid_cell_actions)
      team_actions_probs[team] = get_team_action_probs(team_actions_list[team], team_cell_action_probs)




    # Children

    self.children = [
      [None for _ in range(len(team_actions_list[1]))]
        for _ in range(len(team_actions_list[0]))]

    self.children_prior_probs = team_actions_probs
    self.children_cumul_values = np.zeros(
      (len(team_actions_list[0]), len(team_actions_list[1])), np.float32)
    self.children_num_visits = np.zeros(
      (len(team_actions_list[0]), len(team_actions_list[1])), np.float32)

    for i in range(len(team_actions_list[0])):
      for j in range(len(team_actions_list[1])):
        self.children[i][j] = MCTSNode(self.mcts, self, (i, j), 
          (team_actions_list[0][i], team_actions_list[1][j]))



    node_value = (team_values[0] - team_values[1]) / 2.0

    return node_value




  def backup(self, leaf_value):
    if self.is_root():
      self.mcts.root_num_visits += 1
      self.mcts.root_cumul_value += leaf_value
      return

    self.parent.children_cumul_values[self.index[0]][self.index[1]] += leaf_value
    self.parent.children_num_visits[self.index[0]][self.index[1]] += 1

    self.parent.backup(leaf_value)




  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children