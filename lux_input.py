from luxai2021.game.game import Game as LuxGame
import luxai2021.game.actions as luxActions
from luxai2021.game.constants import LuxMatchConfigs_Default









if __name__ == "__main__":
    # Create a game
    configs = LuxMatchConfigs_Default
    print(configs)

    game = LuxGame(configs)
    
    game_over = False
    while not game_over:
        print("Turn %i" % game.state["turn"])

        # Array of actions for both teams. Eg: MoveAction(team, unit_id, direction)
        actions = []

        game_over = game.run_turn_with_actions(actions)
    
    print("Game done, final map:")
    print(game.map.get_map_string())
