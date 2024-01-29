# Python UNO

## Setting up a game

Create a class and instantiate a game instance from `uno.py`
```py
import uno

#Create the game instance for 4 players, each being dealt 7 cards to start
game = uno.Game(4,7)
# Synchronously extract the winner from the game on end to enable future calculations
winner = game.start_game()
```