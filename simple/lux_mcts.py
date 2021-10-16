from sortedcontainers.sortedlist import SortedList



from luxai2021.game.game import Game




from lux_model import *
from lux_actions import *




import math
import copy




from timeit import default_timer as timer




class MCTS():
  def __init__(self, model: LuxModel):
    self.model: LuxModel = model

    self.num_iterations = 1
    self.c_puct = 1.0
    
    self.game: Game = None
    self.current_game: Game = None




  def run(self, game: Game) -> List[tuple]:
    self.root: MCTSNode = MCTSNode(self)

    self.game: Game = game

    for _ in range(self.num_iterations):
      self.playout()

    best_child = max(self.root.children, key=lambda child: child.num_visits)

    return best_child.team_actions




  def playout(self):
    node: MCTSNode = self.root

    self.game.log_file = None
    self.current_game: Game = copy.deepcopy(self.game)

    while not node.is_leaf():
      node = node.select_child()
      
      self.current_game.run_turn_with_actions(node.team_actions[0] + node.team_actions[1])

    if not self.current_game.match_over():
      leaf_value = node.expand()
    else:
      leaf_value = float(self.current_game.get_winning_team() == 0)

    node.backup(leaf_value)
  




class MCTSNode():
  def __init__(self, mcts: MCTS, parent = None,
  team_actions: Tuple[List, List] = None, prior_prob: float = 0.0):
    self.mcts = mcts

    self.parent: MCTSNode = parent

    self.team_actions: Tuple[List, List] = team_actions
    
    self.num_visits = 0
    self.cumul_value = 0.0

    self.aux_value = prior_prob

    self.children = SortedList(key=lambda item: -item.aux_value)




  def select_child(self):
    return self.children[0]




  def expand(self):
    team_values = [0.0, 0.0]

    team_actions_list = []
    team_actions_probs = []




    # Get team actions and probabilities
    
    considered_units_map = get_considered_units_map(self.mcts.current_game)

    for team in range(2):
      team_observation = get_team_observation(self.mcts.current_game, team, considered_units_map)

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




    # Create children

    child_list = []

    for i in range(len(team_actions_list[0])):
      for j in range(len(team_actions_list[1])):
        child_actions = (team_actions_list[0][i], team_actions_list[1][j])
        child_prob = team_actions_probs[0][i] * team_actions_probs[1][j]

        child = MCTSNode(self.mcts, self, child_actions, child_prob)

        child_list.append(child)

    self.children.update(child_list)



    return (team_values[0] - team_values[1]) / 2.0




  def backup(self, leaf_value):
    self.num_visits += 1
    self.cumul_value += leaf_value

    if self.is_root():
      return

    self.parent.children.remove(self)
    self.aux_value -= 0.25 ** leaf_value
    self.parent.children.add(self)

    self.parent.backup(leaf_value)




  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children