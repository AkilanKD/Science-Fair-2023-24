from time import perf_counter_ns, sleep
from random import shuffle
from math import floor
# PokerHandEvaluator is copyrighted by Henry Lee (2016-2023) and was licensed under the Apache
# License 2.0
from phevaluator import evaluate_cards





### CLASSES ###

# Poker-playing AIs
class AI:
    '''Poker-playing AIs'''
    def __init__(self, strategy, game, preflop):
        self.strategy = strategy # AI strategy name
        self.game = game # Game which the AI is in
        self.money = 100 # Money on hand - Initially at 100
        self.hand = [] # Hand (cards held by the AI) - aka hole cards
        self.preflop = preflop # Preflop betting pct

    def __str__(self):
        '''Lists strategy & money
        Ex: "Strategy: Tight Aggressive", Money: 100'''
        return f"Strategy: {self.strategy}, Money: {self.money}"

    def evaluate(self):
        '''Evaluates the hand of the deck

        Returns an integer which represents the value of the hand
        Lower values represent better hands'''

        cards = self.hand + self.game.comm_cards # Total cards available for player

        # Converts cards into strings which can be inputted into evaluate_cards
        cards = [f"{'T' if x.rank == '10' else x.rank[0]}{x.suit[0].lower()}" for x in cards]

        # Uses the evaluate_cards() function from PokerHandEvaluator to return score for hand
        return evaluate_cards(cards[0], cards[1], cards[2], cards[3], cards[4], cards[5], cards[6])

    def decision(self):
        '''INCOMPLETE - Performs an action based on hand, round, and other bets'''
        pass

    def bet(self, amount):
        '''Bets a given amount of money by adding it to the pot

        Parameter:
        amount - amount of money to bet'''

        # Lowers bet to max possible if bet is too high
        if self.money - amount < 0:
            amount = self.money

        # Moves amount bet from money to pot
        self.money -= amount
        self.game.pot += amount

        # Resets highest bet if bet was raised
        if amount > self.game.highest_bet:
            self.game.highest_bet = amount

    def fold(self):
        '''Folds cards (leaving the game) by removing AI from player_list'''
        self.game.player_list.pop(self)


class Card:
    ''' Individual cards'''
    # List of card ranks
    # Combines face cards with number cards (created with a range)
    CARD_RANKS = ("Ace", "King", "Queen", "Jack") + tuple(str(x) for x in range(10, 1, -1))

    # List of card suits
    CARD_SUITS = ("Spades", "Hearts", "Clubs", "Diamonds")

    def __init__(self, suit, rank):
        self.suit = suit # Card suit (spades, hearts, clubs, diamonds)
        self.rank = rank # Card rank (number/face) - set to string

    def __str__(self):
        '''Returns rank, then suit of card (ex: "Ace of Spades")'''
        return f"{self.rank} of {self.suit}"


class Deck:
    '''Deck of cards'''
    def __init__(self, game):
        self.game = game # Part of game
        self.cards = [] # Deck of cards
        self.new_deck() # Creates new deck
        self.deal() # Deals cards

    def __str__(self):
        '''Lists all cards available in deck, separated by commas'''
        return ", ".join([str(x) for x in self.cards])

    def new_deck(self):
        ''' Creates full deck of cards'''
        # Adds Card objects to cards list with each suit and rank
        # Suit goes from 2 to 15 - cards with rank 11 and above are face cards
        self.cards = [Card(x, y) for x in Card.CARD_SUITS for y in Card.CARD_RANKS]
        # Shuffles cards in deck using the Random function shuffle()
        shuffle(self.cards)

    def deal(self):
        '''Deals out 2 cards to all AI players'''
        # Repeats based on num
        # Gives every player a card first, then goes for the next round
        for a in range(2):
            # Gives each player the top card from the deck, then removes that card
            for b in self.game.ai_list:
                b.hand.append(self.cards[0])
                self.cards.pop(0)

    def reveal_cards(self, num):
        '''Reveals community cards

        Parameter:
        num - number of cards revealed'''
        # Adds all cards from deck with indices from 0 (start) to num to the comm_cards list
        self.game.comm_cards.extend(self.cards[0:num])
        # Removes top cards from the deck by setting cards to to a slice of items after index num
        self.cards = self.cards[num:]


# Game
class Game:
    ''' Creates a game of Texas Holdem'''
    def __init__(self):
        self.ai_list = [AI("fdsa" + str(x), self, x) for x in [0, 2, 4, 5]] # List of all AIs
        shuffle(self.ai_list) # Randomizes order of players
        self.player_list = self.ai_list.copy() # List of AI playing (who did not fold)
        self.comm_cards = [] # Community cards
        self.pot = 0 # Pot (total amount bet by all players)
        self.highest_bet = 0 # Highest bet put down
        self.deck = Deck(self) # Deck of cards
        self.round = "Preflop" # Round of game

    def __str__(self):
        '''Returns round of game'''
        return self.round

    def set_round(self, name, num):
        '''Changes each round in Holdem
        
        Parameters:
        name - name of the round
        num - number of cards revealed in the round'''
        self.round = name
        self.deck.reveal_cards(num)
        for x in self.player_list:
            x.decision()

    def showdown(self):
        '''Showdown between all players'''

        hands_dict = {}

        for x in self.player_list:
            if x.evaluate() in hands_dict:
                hands_dict[x.evaluate()].append(x)
            else:
                hands_dict[x.evaluate()] = [x]
        hands = list(hands_dict.keys())
        hands.sort()

        # hands_dict[hands[0]] = list of AIs with the highest hand
        for x in hands_dict[hands[0]]:
            x.money += floor(self.pot / len(hands_dict[hands[0]]))

        # Sets the pot to the remaining money left
        self.pot %= len(hands_dict[hands[0]])





### GAME ###

# New game
newGame = Game()


# Players in game
print(f"\nPlayers: {[str(x) for x in newGame.player_list]}")

# Cards of players
print(f"\nPlayers' cards: {[str(x) + ': ' + str([str(y) for y in x.hand]) for x in newGame.player_list]}")

# Deck
#print(f"\nDeck: {str(newGame.deck)}")

# Preflop
# Small blind
newGame.player_list[0].bet(2)
# Big blind
newGame.player_list[1].bet(4)

for z in newGame.player_list[2:]:
    z.decision()

# Flop
newGame.set_round("Flop", 3)
# Turn
newGame.set_round("Turn", 1)
# River
newGame.set_round("River", 1)

# Showdown
newGame.showdown()

# Community Cards
print(f"\nCommunity cards: {[str(x) for x in newGame.comm_cards]}")

# Players in game
print(f"\nPlayers: {[str(x) for x in newGame.player_list]}")

# Deck
#print(str(newGame.deck))
#print(len(newGame.deck.cards))

# Community Cards
#print([str(x) for x in newGame.comm_cards])
