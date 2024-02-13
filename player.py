import time
import model_utils
import numpy as np
from uno import Game
from utils import argmax
from model import Linear_QNet
from plotting import plot_wins

class Player:
    def __init__(self, model, number_of_games):
        self.model = model
        self.game_instance = None
        self.player = 1
        self.game_over = False
        self.games_won = 0
        self.number_of_games = number_of_games

    def reset(self):
        self.game_instance = None
        self.game_over = False

    def _setup_game(self):
        self.game_instance = Game(1, 7, self.handle_turn_finished, False)

        self.game_instance.register_play_notifier(self.player, self.handle_turn_ready)
        self.game_instance.start_game()

    def _get_state(self):
        state = self.game_instance.get_game_state(self.player)
        return np.array(state, dtype=int)
    
    def handle_turn_ready(self):
        if not self.game_instance or self.game_over:
            return

        current_state = self._get_state()
        action = model_utils.predict_action(self.model, current_state)
        total_actions = self.game_instance.get_actions(self.player)[1]

        translated_action = total_actions[argmax(action)]
        self.game_instance.play_hand(self.player, translated_action)

    def handle_turn_finished(self, game_done):
        if game_done:
            winner = self.game_instance.get_winner()

            if winner == self.player:
                self.games_won += 1

            self.game_over = True
    
    def run_player(self):
        for i in range(self.number_of_games):
            count_games_won = self.games_won
            self._setup_game()

            while not self.game_over:
                time.sleep(0.1)
            
            if self.games_won > count_games_won:
                print('Model won the game!')
            else: print('Model lost the game :(')

            if(self.number_of_games > 1): plot_wins(['AI', 'Computer'], [self.games_won, i - self.games_won])
        return self.games_won

if __name__ == '__main__':
    model = Linear_QNet(12, 256, 3)
    player = Player(model, 100)

    player.run_player()
