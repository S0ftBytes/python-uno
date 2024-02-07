import random
import utils
from card import PowerCard

class Game:
    """A class representing representing the classic uno card game.

    Attributes:
        player_count (int): The number of players in the game.
        current_deck (list): The current deck of cards in play.
        played_cards (list): The cards that have been played during the game.
        player_hands (list): A list of lists, where each inner list represents a player's hand.
        current_player (int): The index of the current player taking their turn.
        game_active (bool): Indicates whether the game is still active.
        play_direction (int): 1 for clockwise, -1 for counterclockwise play direction.
        skipped_players (list): A list of players who have been skipped in the current round.
        winning_player (int): The index of the player who has won the game.

    Methods:
        get_next_player(self): Get the index of the next player based on play direction.
        get_current_player(self): Get the index of the current player.
        is_game_active(self): Check if the game is still active.
        get_player_cards(self, player): Get the list of cards in a player's hand.
        flip_play_direction(self): Change the play direction from clockwise to counterclockwise and vice versa.
        skip_player(self, player): Mark a player as skipped in the current round.
        play_hand(self, player): Allow a player to play a card from their hand.
        play_random(self, player): Play a random card from a player's hand.
        play_card(self, player): Allow a player to select and play a specific card from their hand.
        handle_pickup(self, player, amount=1, reason='No playable cards'): Handle a player picking up cards from the deck.
        _get_last_played_card(self): Get the last card played in the game.
        get_playable_cards(self, player): Get a list of playable cards in a player's hand.
        handle_round(self): Handle a round of the game, including player turns and card plays.
        check_win_condition(self, player): Check if a player has won the game.
        handle_win(self, player): Handle the end of the game when a player wins.
        start_game(self): Start the game and handle rounds until it's completed.
        get_winner(self): Get the index of the winning player, if the game has ended.
    """

    def __init__(self, player_count, cards_per_player, turn_finished_callback=None, logging=True):
        """Initialize a new game with the specified number of players and cards per player."""
        self.robots = []

        if(player_count == 1):
            player_count = 2
            self.robots.append(2)

        self.player_count = player_count
        self.current_deck, self.played_cards = utils.shuffle_deck(utils.create_deck(['yellow', 'green', 'blue', 'red']))
        self.player_hands = utils.deal_cards(self.current_deck, player_count, cards_per_player)
        self.current_player = 0
        self.game_active = False
        self.play_direction = 1
        self.skipped_players = []
        self.winning_player = None
        self.managed_play_handlers = {}
        self.cards_played = 0
        self.turn_finished_callback = turn_finished_callback
        self.logging_enabled = logging
        
    def get_next_player(self):
        if self.play_direction == 1:
            next_player = self.current_player + 1
            if next_player > self.player_count:
                next_player = 1
        elif self.play_direction == -1:
            next_player = self.current_player - 1
            if next_player < 1:
                next_player = self.player_count
        else:
            raise ValueError("Invalid play_direction. It should be either 1 or -1.")

        return next_player
    
    def get_current_player(self):
        return self.current_player
    
    def is_robot(self, player):
        return player in self.robots
    
    def is_game_active(self):
        return self.game_active
    
    def get_player_cards(self, player):
        return self.player_hands[player-1]
    
    def flip_play_direction(self):
        if self.play_direction == 1:
            self.play_direction = -1
            return
        
        self.play_direction = 1
    
    def skip_player(self, player):
        self.skipped_players.append(player)

    def _get_points(self, player):
        player_hand = self.get_player_cards(player)

        points = 1
        for card in player_hand:
            if isinstance(card, PowerCard):
                if 'wild' in card.card_id:
                    points += 50
                else: points += 25
            elif type(card.value) == int: points += card.value
            else: points += 25

        return points
    
    def get_game_state(self, player):
        last_played_card = self._get_last_played_card()
        current_number = 99 if isinstance(last_played_card, PowerCard) else last_played_card.value
        current_colour = last_played_card.colour

        matching_number = self._get_number_card(player, current_number) != None
        matching_colour = self._get_colour_card(player, current_colour) != None
        has_wild = self._get_wild_card(player) != None

        return [matching_colour, matching_number, has_wild ]
        
    def play_hand(self, player, action=None):
        last_played_card = self._get_last_played_card()
        player_hand = self.get_player_cards(player)
        
        utils.log('\nPlayer ' + str(player) + ", it is your turn to play!", self.logging_enabled)
        utils.log('The last played card was ' + str(last_played_card), self.logging_enabled)
        
        utils.log("Here are your all cards. (Not all are playable): " + str(player_hand), self.logging_enabled)
        utils.log("Here are your playable cards: " + str(self._get_playable_cards(player)), self.logging_enabled)
        card = None

        if self.is_robot(player):
            card = self._play_random(player)
        else:

            while card == None:
                try:
                    utils.log("Please select one of the following play options:\n", self.logging_enabled)
                    
                    utils.log("Play random same number (n)", self.logging_enabled)
                    utils.log("Play random same colour (c)", self.logging_enabled)
                    utils.log("Play wild card (w)", self.logging_enabled)

                    if action != None: selection = action
                    else: selection = input()
                    
                    card = self._get_card_for_action(player, selection)
                    if card == None:
                        actions = self.get_actions(player)[0]
                        card = self._get_card_for_action(player, actions[0])
                except:
                    utils.log('Error: You must enter one of the provided options!', self.logging_enabled)
            
        reward = self._play_card(player, card)

        return reward
    
    def _get_card_for_action(self, player, action):
        actions, total_actions, number_card, colour_card, wild_card = self.get_actions(player)
        card = None

        if action.lower() == 'n' and 'n' in actions:
            card = number_card
        elif action.lower() == 'c' and 'c' in actions:
            card = colour_card
        elif action.lower() == 'w' and 'w' in actions:
            card = wild_card

        return card
        

    def get_actions(self, player):
        last_played_card = self._get_last_played_card()

        last_played_number = None
        last_played_colour = None

        if not isinstance(last_played_card, PowerCard):
            last_played_number = last_played_card.value
            last_played_colour = last_played_card.colour
        elif isinstance(last_played_card, PowerCard) and last_played_card.colour != "":
            last_played_colour = last_played_card.colour

        number_card = self._get_number_card(player, last_played_number)
        colour_card = self._get_colour_card(player, last_played_colour)
        wild_card = self._get_wild_card(player)

        total_actions = ['n','c','w']
        actions = []

        if number_card != None:
            actions.append(total_actions[0])
        if colour_card != None:
            actions.append(total_actions[1])
        if wild_card != None:
            actions.append(total_actions[2])

        return actions, total_actions, number_card, colour_card, wild_card
            
    def _play_random(self, player):
        playable_cards = self._get_playable_cards(player)
        
        random_card = random.choice(playable_cards)
        
        return random_card
    
    def _get_colour_card(self, player, colour):
        if colour is None:
            return None

        player_hand = self._get_playable_cards(player)
        colour_cards = [card for card in player_hand if card.colour == colour]

        def sorting_key(card):
            if type(card.value) == int:
                return card.value
            else:
                return float('-inf')

        colour_cards.sort(key=sorting_key, reverse=True)

        if len(colour_cards) == 0:
            return None

        return random.choice(colour_cards)

    def _get_number_card(self, player, number):
        if(number == None): return None

        player_hand = self._get_playable_cards(player)
        number_cards = [card for card in player_hand if not isinstance(card, PowerCard) and card.value == number]

        if len(number_cards) == 0: return None

        return random.choice(number_cards)
    
    def _get_wild_card(self, player):
        player_hand = self._get_playable_cards(player)
        wild_cards = [card for card in player_hand if isinstance(card, PowerCard) and 'wild' in card.card_id]

        if len(wild_cards) == 0: return None

        return random.choice(wild_cards)

    
    def _play_card(self, player, card):
        player_hand = self.get_player_cards(player)
        starting_points = self._get_points(player)

        self.played_cards.append(card)
        player_hand.remove(card)

        reward = 0
        
        utils.log("You played " + str(card) + ', leaving you with ' + str(len(player_hand)) + " card(s) remaining!", self.logging_enabled)
        if isinstance(card, PowerCard):
            card.handle_played(self)
        
        self.cards_played += 1

        game_won = self._check_win_condition(player)
        if game_won:
            self._handle_win(player)
            reward = 1000

        updated_points = self._get_points(player)
        reward += starting_points - updated_points

        if self.turn_finished_callback != None:
            self.turn_finished_callback(game_won)
        return reward
                   
    def handle_pickup(self, player, amount=1, reason='No playable cards'):
        if(amount >= len(self.current_deck)):
            self.current_deck, self.played_cards = utils.handle_deck_exhausted(self.current_deck, self.played_cards, self.logging_enabled)
        
        picked_up_cards = self.current_deck[:amount]
        del self.current_deck[:amount]
        
        self.player_hands[player-1] += picked_up_cards
        
        utils.log('\nPlayer ' + str(player) + ' picked up ' + str(amount) + ' card(s) for the reason: ' + reason, self.logging_enabled)
        utils.log(str(picked_up_cards), self.logging_enabled)
        
        
    def _get_last_played_card(self):
        num_cards = len(self.played_cards)
        
        if num_cards == 0: return None
        return self.played_cards[num_cards-1]
        
    def _get_playable_cards(self, player):
        player_cards = self.player_hands[player-1]
        playable_cards = [card for card in player_cards if card.is_playable(self._get_last_played_card())]
        
        return playable_cards
        
    def _handle_round(self):       
        for player_itr in range(1, self.player_count + 1):
            if not self.game_active: break
            
            player = self.get_next_player()
            self.current_player = player
            
            if player in self.skipped_players:
                utils.log("Player " + str(player) + ' was skipped!', self.logging_enabled)
                self.skipped_players.remove(player)
                continue
            
            playable_cards = self._get_playable_cards(player)
            
            if len(playable_cards) == 0:
                self.handle_pickup(player)
                playable_cards = self._get_playable_cards(player)
            if len(playable_cards) == 0: return
            
            if player in self.managed_play_handlers:
                managed_handler = self.managed_play_handlers.get(player)
                managed_handler()
            else: self.play_hand(player)
        
    def _check_win_condition(self, player):
        player_hand = self.get_player_cards(player)
        finished = len(player_hand) == 0
        
        return finished
    
    def _handle_win(self, player):
        utils.log(f"Player {player} has won!", self.logging_enabled)

        self.winning_player = player
        self.game_active = False

    def get_winner(self):
        return self.winning_player
    
    def register_play_notifier(self, player, notifier):
        self.managed_play_handlers[player] = notifier

    def get_cards_played(self):
        return self.cards_played
        
    def start_game(self):
        self.current_player = 0
        self.game_active = True
                   
        while self.game_active:
            self._handle_round()
        
        return self.get_winner()