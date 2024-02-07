from card import Card, PowerCard
import utils
import random

class CardMaker:
    def __init__(self, colours):
        self.colours = colours

    def handle_draw_card(self, game_instance, card):
        next_player = game_instance.get_next_player()
        pickup_amount = card.special_attr
        
        game_instance.handle_pickup(next_player, pickup_amount, 'Pickup ' + str(pickup_amount))

    def create_draw_card(self, draw_amount, colour):
        display_name = colour + ' draw ' + str(draw_amount)
        return PowerCard('draw', colour, display_name, draw_amount, play_handler=self.handle_draw_card)

    def handle_skip_card(self, game_instance, card):
        next_player = game_instance.get_next_player()
        game_instance.skip_player(next_player)

    def create_skip_card(self, colour):
        return PowerCard('skip', colour, play_handler=self.handle_skip_card)

    def handle_reverse_card(self, game_instance, card):
        game_instance.flip_play_direction()

    def create_reverse_card(self, colour):
        return PowerCard('reverse', colour, play_handler=self.handle_reverse_card)

    def wild_card_playable(self, prev_card):
        return True

    def handle_wild_card(self, game_instance, card):
        current_player = game_instance.get_current_player()
        player_hand = game_instance.get_player_cards(current_player)

        colour = utils.find_dominant_colour(player_hand, self.colours)
        card.set_colour(colour)

    def create_wild_card(self):
        return PowerCard('wild', first_playable=False, custom_is_playable=self.wild_card_playable, play_handler=self.handle_wild_card)

    def handle_special_wild_card(self, game_instance, card):
        self.handle_wild_card(game_instance, card)
        self.handle_draw_card(game_instance, card)

    def create_special_wild_card(self, draw_amount):
        display_name = 'wild draw ' + str(draw_amount)
        return PowerCard('special_wild', special_attr=draw_amount, display_name=display_name, first_playable=False, custom_is_playable=self.wild_card_playable, play_handler=self.handle_special_wild_card)

