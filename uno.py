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
        get_last_played_card(self): Get the last card played in the game.
        get_playable_cards(self, player): Get a list of playable cards in a player's hand.
        handle_round(self): Handle a round of the game, including player turns and card plays.
        check_win_condition(self, player): Check if a player has won the game.
        handle_win(self, player): Handle the end of the game when a player wins.
        start_game(self): Start the game and handle rounds until it's completed.
        get_winner(self): Get the index of the winning player, if the game has ended.
    """

    def __init__(self, player_count, cards_per_player):
        """Initialize a new game with the specified number of players and cards per player."""
        self.player_count = player_count
        self.current_deck, self.played_cards = utils.shuffle_deck(utils.create_deck(['yellow', 'green', 'blue', 'red']))
        self.player_hands = utils.deal_cards(self.current_deck, player_count, cards_per_player)
        self.current_player = 0
        self.game_active = False
        self.play_direction = 1
        self.skipped_players = []
        self.winning_player = None
        
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
        
    def play_hand(self, player):
        last_played_card = self.get_last_played_card()
        player_hand = self.get_player_cards(player)
        
        print('\nPlayer ' + str(player) + ", it is your turn to play!")
        print('The last played card was ' + str(last_played_card))
        
        print("Here are your all cards. (Not all are playable): " + str(player_hand))
        card = None
        
        while card == None:
            try:
                selection = int(input("Select card to play (1) or play random card (2)"))
                
                if selection == 1:
                    card = self.play_card(player)
                elif selection == 2:
                    card = self.play_random(player)
                else:
                    print(type(selection))
            except:
                print('You must enter either 1 or 2')
            
        
        self.played_cards.append(card)
        player_hand.remove(card)
        
        print("You played " + str(card) + ', leaving you with ' + str(len(player_hand)) + " card(s) remaining!")
        if isinstance(card, PowerCard):
            card.handle_played(self)
            
        if self.check_win_condition(player):
            self.handle_win(player)
            
    def play_random(self, player):
        player_hand = self.get_player_cards(player)
        playable_cards = self.get_playable_cards(player)
        
        random_card = random.choice(playable_cards)
        
        return random_card
    
    def play_card(self, player):
        player_hand = self.get_player_cards(player)
        playable_cards = self.get_playable_cards(player)
        
        card = None        
        while card == None:
            try:
                card_idx = int(input("These are your playable cards. Please enter the number for the card to play: " + str(playable_cards))) -1
                
                card = playable_cards[card_idx]
            except KeyboardInterrupt:
                raise    
            except:
                print('That is not a valid card index number!')
            
        
        return card
        
                   
    def handle_pickup(self, player, amount=1, reason='No playable cards'):
        if(amount >= len(self.current_deck)):
            self.current_deck, self.played_cards = utils.handle_deck_exhausted(self.current_deck, self.played_cards)
        
        picked_up_cards = self.current_deck[:amount]
        del self.current_deck[:amount]
        
        self.player_hands[player-1] += picked_up_cards
        self.player_hands[player-1].sort()
        
        print('\nPlayer ' + str(player) + ' picked up ' + str(amount) + ' card(s) for the reason: ' + reason)
        print(str(picked_up_cards))
        
        
    def get_last_played_card(self):
        num_cards = len(self.played_cards)
        
        if num_cards == 0: return None
        return self.played_cards[num_cards-1]
        
    def get_playable_cards(self, player):
        player_cards = self.player_hands[player-1]
        playable_cards = [card for card in player_cards if card.is_playable(self.get_last_played_card())]
        
        return playable_cards
        
    def handle_round(self):       
        for player_itr in range(1, self.player_count + 1):
            if not self.game_active: break
            
            player = self.get_next_player()
            self.current_player = player
            
            if player in self.skipped_players:
                print("Player " + str(player) + ' was skipped!')
                self.skipped_players.remove(player)
                continue
            
            playable_cards = self.get_playable_cards(player)
            
            if len(playable_cards) == 0:
                self.handle_pickup(player)
                playable_cards = self.get_playable_cards(player)
            if len(playable_cards) >= 1: self.play_hand(player)
        
    def check_win_condition(self, player):
        player_hand = self.player_hands[player-1]
        finished = len(player_hand) == 0
        
        return finished
    
    def handle_win(self, player):
        print("Player " + player + " has won!")

        self.winning_player = player
        self.game_active = False

    def get_winner(self):
        return self.winning_player    
        
    def start_game(self):
        self.current_player = 0
        self.game_active = True
                   
        while self.game_active:
            self.handle_round()
        
        return self.get_winner()