from time import perf_counter_ns, sleep
from phevaluator import evaluate_cards
from re import findall
from random import shuffle
from math import floor



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
        Returns an integer which represents the hand and the highest card for tiebreakers'''

        hand_score = 0 # Score based on hand
        flush = False # Whether there is a flush, or of the same suit
        straight = False # Whether the cards are straight, or have ranks in a row
        high_card = 0 # Highest card available
        total_hand = self.hand + self.game.comm_cards # Total cards available for player

        # Test
        #total_hand = [Card("Diamonds", "Ace"), Card("Diamonds", "2"), Card("Diamonds", "Queen"), Card("Diamonds", "Jack"), Card("Diamonds", "10"), Card("Diamonds", "9"), Card("Diamonds", "8")]

        # Ranks of all cards in total_hand
        ranks = [x.rank for x in total_hand]
        suits = [x.suit for x in total_hand]

        #print(ranks)

        print([str(x) for x in total_hand])

        # Number of cards per rank
        rank_num = [ranks.count(x) for x in Card.CARD_RANKS]

        print(rank_num)

        # Number of cards per suit
        suit_num = [suits.count(x) for x in Card.CARD_SUITS]

        print(suit_num)

        # Checks if any suit has at least five cards
        # Based off of code from Simeon Visser of Stack Overflow and manjeet_04 of GeeksForGeeks:
        # https://stackoverflow.com/a/21054577
        # https://www.geeksforgeeks.org/python-test-if-list-contains-elements-in-range/#
        flush = any(x >= 5 and x <= 7 for x in suit_num)

        print(flush)

        # Checks for straight

        # Creates string which combines numbers of rank_num together
        combined_rank_num = "".join([str(x) for x in rank_num])
        # Uses the RegEx function findall() to look for five instances of the characters one to
        # five in a row, then checks the length of the list (0 means no items matched the condition)
        if len(findall("[1-5]{5}", combined_rank_num)) > 0:
            straight = True

        print(flush)

        if 4 in rank_num: # four of a kind
            hand_score = 600
            high_card = 14 - rank_num.index(4)
        elif 3 in rank_num:
            if any(x >= 2 for x in rank_num): # full house - needs fix
                hand_score = 500
            else: # three of a kind
                hand_score = 200
                high_card = 14 - rank_num.index(3)
        elif 2 in rank_num: # two of a kind
            hand_score = 100
            high_card = 14 - rank_num.index(2)
        if flush is True and hand_score < 400: # flush
            hand_score = 400
        elif straight is True and hand_score < 300: # straight
            hand_score = 300
        else: # high card 
            high_card = 14 - rank_num.index(1)

        if flush is True and straight is True:
            # Find a way to separate by suit
            rank_by_suit = []
            hand_score = 700
            print("straight flush")

        hand_score += high_card
        # Adds value of highest card in pair or flush to break ties

        return hand_score

    def decision(self):
        '''INCOMPLETE - Performs an action based on the result'''
        pass

    def bet(self, amount):
        '''Bets a given amount of money by adding it to the pot
        Amount - amount of money to bet'''

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
        '''INCOMPLETE - Folds cards (leaving the game)'''
        self.game.player_list.pop(self)


class Card:
    ''' Individual cards'''
    # List of card ranks
    # Combines face cards with number cards (created with a range)
    CARD_RANKS = ["Ace", "King", "Queen", "Jack"] + [str(x) for x in range(10, 1, -1)]

    # List of card suits
    CARD_SUITS = ["Spades", "Hearts", "Clubs", "Diamonds"]

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
        self.deal(2) # Deals cards

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

    def deal(self, num):
        '''Deals out cards to all AI players
        
        Parameter:
        num - number of cards for each player'''
        # Repeats based on num
        # Gives every player a card first, then goes for the next round
        for a in range(num):
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
        self.ai_list = [AI("fdsa", self, x) for x in [0, 2, 4, 5]] # List of all AIs
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

        print(hands_dict)
        print(hands)

        # hands_dict[max(hands)] = list of AIs with the highest hand
        for x in hands_dict[max(hands)]:
            x.money += floor(self.pot / len(hands_dict[max(hands)]))

        # Sets the pot to the remaining money left
        self.pot %= len(hands_dict[max(hands)])





### GAME ###

# New game
newGame = Game()


# Players in game
print([str(x) for x in newGame.player_list])

# Cards of players
print([[str(y) for y in x.hand] for x in newGame.player_list])

# Deck
print(str(newGame.deck))

# Community Cards
print([str(x) for x in newGame.comm_cards])


# Small blind
newGame.player_list[0].bet(2)
# Big blind
newGame.player_list[1].bet(4)
# Flop
newGame.set_round("Flop", 3)
# Turn
newGame.set_round("Turn", 1)
# River
newGame.set_round("River", 1)

# Showdown
newGame.showdown()
print([str(x) for x in newGame.player_list])

# Deck
#print(str(newGame.deck))
#print(len(newGame.deck.cards))

# Community Cards
#print([str(x) for x in newGame.comm_cards])
