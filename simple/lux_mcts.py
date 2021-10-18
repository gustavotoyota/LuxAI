from luxai2021.game.game import Game




from lux_model import *
from lux_actions import *




import math
import copy




from timeit import default_timer as timer




class MCTS():
  def __init__(self, model: LuxModel):
    self.model: LuxModel = model

    self.num_iterations = 100
    self.c_puct = 1.0
    
    self.game: Game = None
    self.current_game: Game = None




  def run(self, game: Game) -> List[tuple]:
    self.game: Game = game

    self.root: MCTSNode = MCTSNode(self)
    self.root_cumul_value = 0.0
    self.root_num_visits = 0

    for _ in range(self.num_iterations):
      self.playout()

    best_child = self.root.children[np.argmax(self.root.children_num_visits)]

    return best_child.team_actions




  def playout(self):
    node: MCTSNode = self.root

    self.game.log_file = None
    self.current_game: Game = copy.deepcopy(self.game)
    self.current_game.stop_replay_logging()

    while not node.is_leaf():
      node = node.select_child()

      considered_units_map = get_considered_units_map(self.current_game)
      env_actions = get_env_actions(self.current_game, node.team_actions, considered_units_map)
      
      self.current_game.run_turn_with_actions(env_actions)

    if not self.current_game.match_over():
      leaf_value = node.expand()
    else:
      leaf_value = float(self.current_game.get_winning_team() == 0)

    node.backup(leaf_value)
  




class MCTSNode():
  def __init__(self, mcts: MCTS, parent = None, index: int = 0,
  team_actions: Tuple[List, List] = None):
    self.mcts = mcts

    self.parent: MCTSNode = parent
    self.index = index

    self.children: List[MCTSNode] = None

    self.children_prior_probs = None
    self.children_cumul_values = None
    self.children_num_visits = None

    self.team_actions: Tuple[List, List] = team_actions




  def select_child(self):
    mean_values = self.children_cumul_values / np.maximum(1.0, self.children_num_visits)

    if self.is_root():
      parent_num_visits = self.mcts.root_num_visits
    else:
      parent_num_visits = self.parent.children_num_visits[self.index]

    adjusted_prior_probs = self.mcts.c_puct * self.children_prior_probs * \
      math.sqrt(parent_num_visits) / (1.0 + self.children_num_visits)

    aux_value = mean_values + adjusted_prior_probs

    return self.children[np.argmax(aux_value)]




  def expand(self):
    team_values = [0.0, 0.0]

    team_actions_list = []
    team_actions_probs = []




    # Get team actions and probabilities
    
    considered_units_map = get_considered_units_map(self.mcts.current_game)

    for team in range(2):
      team_observation = get_team_observation(self.mcts.current_game, team, considered_units_map)

      team_observation = (team_observation - self.mcts.model.input_mean) / self.mcts.model.input_std

      team_cell_action_probs, team_value = self.mcts.model(team_observation)

      team_cell_action_probs: Tensor
      team_value: Tensor

      team_cell_action_probs = team_cell_action_probs.detach().view(CELL_ACTION_COUNT, \
        self.mcts.current_game.map.width, self.mcts.current_game.map.height).cpu().numpy()
      team_values[team] = team_value.item()

      team_valid_cell_actions = get_team_valid_cell_actions(self.mcts.current_game, team, considered_units_map)

      team_cell_action_mask = get_cell_action_mask(self.mcts.current_game, team_valid_cell_actions)
      team_cell_action_probs = normalize_cell_action_probs(team_cell_action_probs, team_cell_action_mask)

      team_actions = get_team_actions(team_cell_action_probs, team_valid_cell_actions)
      team_action_probs = get_team_action_probs(team_actions, team_cell_action_probs)

      team_actions_list.append(team_actions)
      team_actions_probs.append(team_action_probs)




    # Children

    num_children = len(team_actions_list[0]) * len(team_actions_list[1])

    self.children = [None] * num_children

    self.children_prior_probs = np.zeros(num_children, np.float32)
    self.children_cumul_values = np.zeros(num_children, np.float32)
    self.children_num_visits = np.zeros(num_children, np.float32)




    child_index = 0

    for i in range(len(team_actions_list[0])):
      for j in range(len(team_actions_list[1])):
        child_actions = (team_actions_list[0][i], team_actions_list[1][j])

        self.children[child_index] = MCTSNode(self.mcts, self, child_index, child_actions)
        self.children_prior_probs[child_index] = team_actions_probs[0][i] * team_actions_probs[1][j]

        child_index += 1




    return (team_values[0] - team_values[1]) / 2.0




  def backup(self, leaf_value):
    if self.is_root():
      self.mcts.root_num_visits += 1
      self.mcts.root_cumul_value += leaf_value
      return

    self.parent.children_cumul_values[self.index] += leaf_value
    self.parent.children_num_visits[self.index] += 1

    self.parent.backup(leaf_value)




  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children