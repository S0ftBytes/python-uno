import random
import numpy as np
import time
from utils import argmax
from uno import Game
from collections import deque
from model import Linear_QNet, QTrainer
import storage_utils
import model_utils
from plotting import plot_wins

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.0001
GAME_TOTAL_PLAYERS = 1
GAME_CARDS_PER_PLAYER = 7

class Agent:
    def __init__(self):
        self.game_number = 0
        self.epsilon_exp = 80
        self.epsilon = 0
        self.gamma = 0.2
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(12, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        #The lower the better (cards played for the whole game)
        self.min_cards_played = 1000
        self.games_won = 0
        self.player = 1

    def get_state(self, game):
        game_state = game.get_game_state(self.player)
        return np.array(game_state, dtype=int)

    def remember(self, state, action, reward, next_state, game_finished):
        self.memory.append((state, action, reward, next_state, game_finished))

    def train_long_term(self):
        mini_sample = random.sample(self.memory, min(len(self.memory), BATCH_SIZE))
        
        states, actions, rewards, next_states, game_finished = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_finished)
        self.model.save()


    def train_short_term(self, state, action, reward, next_state, game_finished):
        self.trainer.train_step(state, action, reward, next_state, game_finished)

    def get_action(self, state):
        self.epsilon = self.epsilon_exp - self.game_number

        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)

            moves = [0,0,0,0]
            moves[move] = 1

            return moves
        else: return model_utils.predict_action(self.model, state)
        


class Trainer:
    def __init__(self, mode='live', instance_number=1, number_of_games=1000):
        self.agent = Agent()
        self.game_instance = None
        self.game_over = False
        self.instance_number = instance_number
        self.mode = mode
        self.number_of_games = number_of_games
        self.cards_played_hist = []
        self.cards_played_mean_hist = []
        self.total_cards_played = 0

    def reset_game(self):
        self.game_instance = Game(GAME_TOTAL_PLAYERS, GAME_CARDS_PER_PLAYER, self.handle_turn_finished, False)
        self.game_instance.register_play_notifier(self.agent.player, self.handle_turn_ready)

        self.agent.game_number += 1
        self.game_over = False
        self.game_instance.start_game()

            
    def get_game(self):
        if self.game_instance == None:
            self.reset_game()

        return self.game_instance

    def handle_turn_ready(self):
        if not self.game_instance or self.game_over:
            return

        current_state = self.agent.get_state(self.game_instance)
        action = self.agent.get_action(current_state)
        total_actions = self.get_game().get_actions(self.agent.player)[1]

        translated_action = total_actions[argmax(action)]
        reward = self.game_instance.play_hand(self.agent.player, translated_action)

        self.train(current_state, action, reward)

    def train(self, old_state, action, reward):
        if not self.game_instance:
            return

        new_state = self.agent.get_state(self.game_instance)
        game_over = not self.game_instance.is_game_active()

        self.handle_memory(old_state, action, reward, new_state, game_over)

    def handle_memory(self, old_state, action, reward, new_state, game_over, store=True):
        self.agent.train_short_term(old_state, action, reward, new_state, game_over)
        self.agent.remember(old_state, action, reward, new_state, game_over)

        if store == True: storage_utils.store_move(self.instance_number, old_state, action, reward, new_state, game_over)
    
    def handle_turn_finished(self, game_done):
        if game_done:
            self.game_over = True
            self.agent.train_long_term()

            winner = self.game_instance.get_winner()

            cards_played = self.game_instance.get_cards_played()

            if winner == self.agent.player:
                if cards_played < self.agent.min_cards_played: self.agent.min_cards_played = cards_played
                self.agent.games_won += 1
            
            if self.instance_number == 1:
                self.cards_played_hist.append(cards_played)
                self.total_cards_played += cards_played

    def play(self):
        print('Begin training...')
        start_time = time.time()

        for i in range(self.number_of_games):
            self.reset_game()

            while not self.game_over:
                time.sleep(0.01)

            if self.instance_number == 1:
                self.cards_played_mean_hist.append(self.total_cards_played / (i + 1))
            
        end_time = time.time()
        training_time = end_time - start_time

        hours, remainder = divmod(training_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f'\nFinished training! Training took {int(hours)} hours, {int(minutes)} minutes, and {seconds:.2f} seconds.')
        print(f'Games won: {self.agent.games_won}\nGames lost: {self.agent.game_number - self.agent.games_won}')

    def recall(self):
        print('Begin training from data set...')
        start_time = time.time()

        recalled_data = storage_utils.get_master()

        for data_row in recalled_data:
            parsed_row = storage_utils.restore_row(data_row)
            self.handle_memory(*parsed_row, False)

        end_time = time.time()
        training_time = end_time - start_time

        hours, remainder = divmod(training_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f'\nFinished training! Training took {int(hours)} hours, {int(minutes)} minutes, and {seconds:.2f} seconds.')
        print(f'Model was trained on {len(recalled_data)} data rows')

    def start(self):
        if self.mode == 'live':
            self.play()
        else: self.recall()

if __name__ == '__main__':
    trainer = Trainer()
    trainer.start()