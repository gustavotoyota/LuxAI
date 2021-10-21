import copy
from typing import List

import numpy as np

import math




import luxai2021.game.game




import lux_model
import lux_units
import lux_engine_actions
import lux_inputs
import lux_cell_actions
import lux_actions



class MCTS():
  def __init__(self, engine_game: luxai2021.game.game.Game, model: lux_model.LuxModel):
    self.model: lux_model.LuxModel = model

    self.num_iterations = 100
    self.c_puct = 3.0

    self.reset(engine_game)




  def reset(self, engine_game: luxai2021.game.game.Game):
    self.root = MCTSNode(self)

    self.root_cumul_value = 0.0
    self.root_num_visits = 0.0

    self.root.engine_game = engine_game




  def run(self):
    ###################################################
    # Run playouts until root is visited enough times #
    ###################################################




    # Run playouts

    while self.root_num_visits < self.num_iterations:
      self.playout()




    # Get child with most number of visits

    best_child_index = np.argmax(self.root.children_cross_num_visits)
    best_child = self.root.children.flat[best_child_index]




    # Put best child as root

    self.root_cumul_value = self.root.children_cross_cumul_values.flat[best_child_index]
    self.root_num_visits = self.root.children_cross_num_visits.flat[best_child_index]

    self.root = best_child




    return best_child.team_actions




  def playout(self):
    ############################################
    # Follow children with the best UCB score, #
    # expand leaf node, and backup its value   #
    ############################################




    # Play until reach leaf node

    node: MCTSNode = self.root
    while not node.is_leaf():
      node: MCTSNode = node.select_child()



    
    # Simulate leaf node actions

    if node != self.root:
      node.parent.engine_game.log_file = None 
      node.engine_game = copy.deepcopy(node.parent.engine_game)
      node.engine_game.stop_replay_logging()

      considered_units_map = lux_units.get_considered_units_map(node.engine_game)
      engine_actions = lux_engine_actions.get_engine_actions(
        node.team_actions, node.engine_game, considered_units_map)

      node.engine_game.run_turn_with_actions(engine_actions)




    # Get value from leaf node

    if node.engine_game.match_over():
      leaf_value = float(node.engine_game.get_winning_team() == 0) * 2.0 - 1.0
    else:
      leaf_value = node.expand()


    

    # Backup value from leaf node

    node.backup(leaf_value)


    



class MCTSNode():
  def __init__(self, mcts, parent = None, index: int = 0, team_actions = None):
    self.mcts: MCTS = mcts

    self.parent: MCTSNode = parent
    self.index = index

    self.children: np.array = None

    self.team_actions = team_actions

    self.engine_game: luxai2021.game.game.Game = None





  def expand(self):
    team_values = [None, None]

    team_actions = [None, None]
    team_action_probs = [None, None]




    # Get action informations

    considered_units_map = lux_units.get_considered_units_map(self.engine_game)

    for team in range(2):
      observation = lux_inputs.get_team_observation(
        self.engine_game, team, considered_units_map)
      
      cell_action_probs, team_values[team] = self.mcts.model(observation)

      valid_cell_actions = lux_cell_actions.get_team_valid_cell_actions(
        self.engine_game, team, considered_units_map)
      cell_action_mask = lux_cell_actions.get_cell_action_mask(
        self.engine_game, valid_cell_actions)
      cell_action_probs = lux_cell_actions.normalize_cell_action_probs(
        cell_action_probs.detach().squeeze(0).cpu().numpy(), cell_action_mask)

      team_actions[team] = lux_actions.get_team_actions(
        cell_action_probs, valid_cell_actions)
      team_action_probs[team] = lux_actions.get_team_action_probs(
        team_actions[team], cell_action_probs)



    
    # Create children

    self.children = np.array([
      [
        (
          MCTSNode(self.mcts, self, (i, j), 
            (team_actions[0][i], team_actions[1][j]))
        ) for j in range(len(team_actions[1]))
      ] for i in range(len(team_actions[0]))
    ], dtype=object)

    self.children_prior_probs = team_action_probs

    self.children_cross_cumul_values = np.zeros(
      (len(team_actions[0]), len(team_actions[1])), np.float32)
    self.children_cross_num_visits = np.zeros(
      (len(team_actions[0]), len(team_actions[1])), np.float32)

    self.children_solo_cumul_values = [
      np.zeros(len(team_actions[0])),
      np.zeros(len(team_actions[1])),
    ]
    self.children_solo_num_visits = [
      np.zeros(len(team_actions[0])),
      np.zeros(len(team_actions[1])),
    ]




    return (team_values[0].item() - team_values[1].item()) / 2.0
    




  def backup(self, leaf_value):
    if self.is_root():
      self.mcts.root_cumul_value += leaf_value
      self.mcts.root_num_visits += 1.0
    else:
      self.parent.children_cross_cumul_values[self.index] += leaf_value
      self.parent.children_cross_num_visits[self.index] += 1.0

      for team in range(2):
        self.parent.children_solo_cumul_values[team][self.index[team]] += leaf_value
        self.parent.children_solo_num_visits[team][self.index[team]] += 1.0

      self.parent.backup(leaf_value)





  def select_child(self):
    #############################################
    # Choose the action with the best UCB score #
    # from the perspective of each player       #
    #############################################




    child_index = [None, None]




    for team in range(2):
      mean_action_values = self.children_solo_cumul_values[team] / \
        np.maximum(1.0, self.children_solo_num_visits[team])

      if self.is_root():
        num_parent_visits = self.mcts.root_num_visits
      else:
        num_parent_visits = self.parent.children_cross_num_visits[self.index[0]][self.index[1]]

      adjusted_prior_probs = self.mcts.c_puct * self.children_prior_probs[team] * \
        math.sqrt(num_parent_visits) / (1.0 + self.children_solo_num_visits[team])
      action_ucb_scores = (-team * 2.0 + 1.0) * mean_action_values + adjusted_prior_probs

      child_index[team] = np.argmax(action_ucb_scores)




    return self.children[tuple(child_index)]





  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return self.children is None




