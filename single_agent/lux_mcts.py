import copy

import numpy as np



import luxai2021.game.game




import lux_neural_net
import lux_units
import lux_engine_actions
import lux_inputs
import lux_cell_actions
import lux_actions



class MCTS():
  def __init__(self, neural_net: lux_neural_net.LuxNet):
    self.neural_net: lux_neural_net.LuxNet = neural_net

    self.num_iterations = 100
    self.c_puct = 1.0

    self.reset()




  def reset(self):
    self.root = MCTSNode(self)

    self.root_cumul_value = 0.0
    self.root_num_visits = 0




  def run(self, engine_game: luxai2021.game.game.Game):
    ###################################################
    # Run playouts until root is visited enough times #
    ###################################################



    # Run playouts

    while self.root_num_visits < self.num_iterations:
      self.playout()



    # Return best actions






  def playout(self):
    ###########################################
    # Follow children with the best UCB score #
    # Expand leaf node and backup its value   #
    ###########################################



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
      engine_actions = lux_engine_actions.get_team_engine_actions(
        node.team_actions, node.engine_game, considered_units_map)

      node.engine_game.run_turn_with_actions(engine_actions)



    # Get value from leaf node

    if node.engine_game.match_over():
      leaf_value = float(node.engine_game.get_winning_team() == 0)
    else:
      leaf_value = node.expand()

    

    # Backup value from leaf node

    node.backup(leaf_value)


    



class MCTSNode():
  def __init__(self, mcts, parent, index):
    self.mcts: MCTS = mcts

    self.parent: MCTSNode = parent
    self.index = index

    self.children = {}

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
      
      cell_action_probs, team_values[team] = self.mcts.neural_net(observation)
      cell_action_probs = cell_action_probs.detach().cpu().numpy()

      valid_cell_actions = lux_cell_actions.get_team_valid_cell_actions(
        self.engine_game, team, considered_units_map)
      cell_action_mask = lux_cell_actions.get_cell_action_mask(
        self.engine_game, valid_cell_actions)
      cell_action_probs = lux_cell_actions.normalize_cell_action_probs(
        cell_action_probs, cell_action_mask)

      team_actions[team] = lux_actions.get_team_actions(
        cell_action_probs, valid_cell_actions)
      team_action_probs[team] = lux_actions.get_team_action_probs(
        team_actions[team], cell_action_probs)



    
    # Create children

    self.children = [
      [
        (
          MCTSNode(self.mcts, self, (i, j), 
            (team_actions[0][i], team_actions[1][j]))
        ) for j in range(len(team_actions[1]))
      ] for i in range(len(team_actions[0]))
    ]

    self.children_probs = team_action_probs
    self.children_cumul_values = np.zeros(
      (len(team_actions[0]), len(team_actions[1])), np.float32)
    self.children_num_visits = np.zeros(
      (len(team_actions[0]), len(team_actions[1])), np.float32)




    return (team_values[0] - team_values[1]) / 2.0
    





  def backup(self):
    pass




  def select_child(self):
    pass





  def is_root(self):
    return not self.parent

  def is_leaf(self):
    return not self.children




