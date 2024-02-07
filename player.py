import time
import model_utils
import numpy as np
from uno import Game
from utils import argmax
from model import Linear_QNet

class Player:
    def __init__(self, model):
        self.model = model
        self.game_instance = None
        self.player = 1
        self.game_over = False
        self.game_won = False

    def _setup_game(self):
        self.game_instance = Game(1, 7, turn_finished_callback=self.handle_turn_finished)

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
                self.game_won = True

            self.game_over = True
    
    def run_player(self):
        self._setup_game()

        while not self.game_over:
            time.sleep(0.1)
        
        if self.game_won:
            print('Model won the game!')
        else: print('Model lost the game :(')

        return self.game_won

if __name__ == '__main__':
    model = Linear_QNet(3, 256, 3)
    player = Player(model)

    player.run_player()
