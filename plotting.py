import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot_wins(players, wins):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Wins - Losses')
    plt.xlabel('Players')
    plt.ylabel('Number of wins')
    plt.bar(players, wins)
    plt.pause(0.1)

def plot_cards_played(cards_played, mean_cards_played):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Cards played')
    plt.xlabel('Number of Games')
    plt.ylabel('Cards played')
    plt.plot(cards_played)
    plt.plot(mean_cards_played)
    plt.ylim(ymin=0)
    # plt.text(len(cards_played)-1, cards_played[-1], str([cards_played-1]))
    # plt.text(len(mean_cards_played)-1, mean_cards_played[-1], str([mean_cards_played-1]))
    plt.show(block=False)
    plt.pause(0.1)