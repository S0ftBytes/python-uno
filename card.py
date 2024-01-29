class Card:
    def __init__(self, colour, value):
        self.colour = colour
        self.value = value
        
    def __repr__(self):
        return self.colour + ' ' + str(self.value)
    
    def is_playable(self, prev_card):
        if(prev_card.colour == self.colour or prev_card.value == self.value): return True
        
        return False
        
class PowerCard(Card):
    def __init__(self, card_id, colour='', display_name='', special_attr=None, first_playable=True, custom_is_playable=None, play_handler=None):
        super().__init__(colour, card_id)
        self.card_id = card_id
        self.special_attr = special_attr
        self.first_playable = first_playable
        self.custom_is_playable = custom_is_playable

        if display_name == '':
            display_name = colour + ' ' + card_id

        self.display_name = display_name
        self.play_handler = play_handler
        
    def __repr__(self):
        return self.display_name
        

    def is_playable(self, prev_card):
        if self.custom_is_playable is not None:
            return self.custom_is_playable(prev_card)

        if self.colour != "" and self.colour == prev_card.colour:
            return True

        return False
    
    def set_colour(self, colour):
        self.colour = colour
        self.display_name = colour + ' ' + self.card_id
        
    def handle_played(self, game_instance):
        if self.play_handler is not None: 
            self.play_handler(game_instance, self)
            return
        
        pass