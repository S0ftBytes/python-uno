import random
from card import Card, PowerCard
import card_maker

def create_colour_card_set(maker, colour, number_card_ranges, colour_item_count):
    lower = number_card_ranges[0]
    upper = number_card_ranges[1]
    
    if(lower >= upper): return []
    
    card_set = []
    
    for i in range(lower, upper):
        for j in range(colour_item_count):
            card = Card(colour, i)
            card_set.append(card)
            
    for i in range(colour_item_count):
        card_set.append(maker.create_draw_card(2, colour))
        card_set.append(maker.create_reverse_card(colour))
        card_set.append(maker.create_skip_card(colour))
    
    return card_set

def create_deck(colours, wild_card_count = 4):
    maker = card_maker.CardMaker(colours)
    deck = []
    
    for colour in colours:
        colour_set = create_colour_card_set(maker, colour, [0,9], 2)
        deck.extend(colour_set)
    
    for i in range(wild_card_count):
        deck.append(maker.create_wild_card())
        deck.append(maker.create_special_wild_card(4))
        
    return deck

def shuffle_deck(deck, played_cards = []):
    shuffled_deck = deck.copy()
    random.shuffle(shuffled_deck)
    
    while True:
        revealed_card = shuffled_deck.pop(0)
        played_cards.append(revealed_card)
        
        revealed_card_playable = True
        
        if isinstance(revealed_card, PowerCard) and not revealed_card.first_playable:
            revealed_card_playable = False
            
        if revealed_card_playable: break
    
    return shuffled_deck, played_cards

def deal_cards(deck, player_count, cards_per_player):
    total_cards_needed = player_count * cards_per_player

    if total_cards_needed > len(deck):
        raise ValueError("Not enough cards to distribute evenly among players.")

    player_hands = [deck.pop(0) for _ in range(total_cards_needed)]

    return [player_hands[i:i + cards_per_player] for i in range(0, total_cards_needed, cards_per_player)]

def handle_deck_exhausted(deck, played_cards):
    print("The game deck has been exhausted! Now shuffling played cards...")
    
    new_deck = deck + played_cards
    
    return shuffle_deck(new_deck, [])

def find_dominant_colour(deck, colours):
    colour_counter = { }

    if len(deck) == 0: return random.choice(colours)

    for card in deck:
        colour = card.colour
        count = colour_counter[colour] + 1 if colour in colour_counter else 1

        colour_counter[colour] = count

    dominant_colour, count = max(colour_counter.items(), key=lambda x: x[1])
    if dominant_colour == None or dominant_colour == "": dominant_colour = random.choice(colours)

    return dominant_colour

def argmax(list):
    return list.index(max(list))