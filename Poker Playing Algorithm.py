from time import perf_counter_ns, sleep
from random import shuffle
from math import floor



### CLASSES ###

# Poker-playing AIs
class AI:
    def __init__(self, strategy, game, preflop):
        self.strategy = strategy # AI strategy name
        self.game = game # Game which the AI is in
        self.money = 100 # Money on hand - Initially at 100
        self.hand = [] # Hand (cards held by the AI) - aka hole cards
        self.preflop = preflop # Preflop betting pct

    # Lists strategy & money (ex: "Strategy: Tight Aggressive"),\nMoney: 100
    def __str__(self):
        return f"Strategy: {self.strategy},\nMoney: {self.money}"

    # Evaluates the hand of the deck
    def evaluate(self):
        hand_score = 0 # Score based on hand
        flush = False # Whether there is a flush, or of the same suit
        straight = False # Whether the cards are straight, or ranks in a row
        high_card = 0 # Highest card available
        total_hand = self.hand + self.game.comm_cards # Total cards available for player

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

        if 5 in suit_num:
            flush = True

        print(flush)

        # How to do straight flush

        if 4 in rank_num: # four of a kind
            hand_score = 400
        elif 3 in rank_num:
            if 2 in rank_num: # full house
                hand_score = 500
            else: # three of a kind
                hand_score = 200
        elif 2 in rank_num: # two of a kind
            hand_score = 100

        if flush is True and hand_score < 400: # flush
            hand_score = 400
        elif straight is True and hand_score < 300: # straight
            hand_score = 300

        if flush is True and straight is True:
            # Find a way to separate by suit
            rank_by_suit = []
            hand_score = 600
            print("straight flush")

        hand_score += high_card
        # Adds value of highest card in pair or flush to break ties

        return hand_score

    def decision(self):
        pass

    # Sets a bet of a certain amount
    # Amount - amount of money to bet
    def bet(self, amount):
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
        pass


# Individual cards
class Card:
    # List of card ranks
    # Combines number cards (created with a range) with face cards
    CARD_RANKS = [str(x) for x in range(2, 11)] + ["Jack", "Queen", "King", "Ace"]

    # List of card suits
    CARD_SUITS = ["Spades", "Hearts", "Clubs", "Diamonds"]

    def __init__(self, suit, rank):
        self.suit = suit # Card suit (spades, hearts, clubs, diamonds)
        self.rank = rank # Card rank (number/face) - set to string

    def __str__(self):
        # Returns rank, then suit of card (ex: "Ace of Spades")
        return f"{self.rank} of {self.suit}"


# Deck of cards
class Deck:
    def __init__(self, game):
        self.game = game # Part of game
        self.cards = [] # Deck of cards
        self.new_deck() # Creates new deck
        self.deal(2) # Deals cards

    # Lists all cards available in deck, separated by commas
    def __str__(self):
        return ", ".join([str(x) for x in self.cards])

    # new_deck - creates full deck of cards
    def new_deck(self):
        # Adds Card objects to cards list with each suit and rank
        # Suit goes from 2 to 15 - cards with rank 11 and above are face cards
        self.cards = [Card(x, y) for x in Card.CARD_SUITS for y in Card.CARD_RANKS]
        # Shuffles cards in deck
        shuffle(self.cards)

    # new_deck - deals out cards to all AI players
    # num - number of cards for each player
    def deal(self, num):
        # Repeats based on num
        # Gives every player a card first, then goes for the next round
        for a in range(num):
            # Gives each player the top card from the deck, then removes that card
            for b in self.game.ai_list:
                b.hand.append(self.cards[0])
                self.cards.pop(0)

    # reveal_cards - Reveals community cards
    # num - number of cards revealed
    def reveal_cards(self, num):
        # Adds all cards from deck with indices from 0 (start) to num to the comm_cards list
        self.game.comm_cards.extend(self.cards[0:num])
        # Removes top cards from the deck by setting cards to to a slice of items after index num
        self.cards = self.cards[num:]


# Game
class Game:
    def __init__(self):
        self.ai_list = [AI("fdsa", self, x) for x in [0, 2, 4, 5]] # List of all AIs
        shuffle(self.ai_list) # Randomizes order of players
        self.player_list = self.ai_list.copy() # List of AI playing (who did not fold)
        self.comm_cards = [] # Community cards
        self.pot = 0 # Pot (total amount bet by all players)
        self.highest_bet = 0 # Highest bet put down
        self.deck = Deck(self) # Deck of cards
        self.round = "Preflop" # Round of game

    # Showdown between all players
    def showdown(self):
        hands_dict = {}

        for x in self.player_list:
            if x.evaluate() in hands_dict:
                hands_dict[x.evaluate()].append(x)
            else:
                hands_dict[x.evaluate()] = [x]
        hands = list(hands_dict.keys())
        hands.sort(reverse=True)

        print(hands_dict)
        print(hands)

        # hands_dict[hands[0]] = list of AIs with the highest hand
        for x in hands_dict[hands[0]]:
            x.money += floor(self.pot / len(hands_dict[hands[0]]))

        # Adds the 
        self.pot %= len(hands_dict[hands[0]])

        if len(hands_dict[hands[0]]) > 1:
            print(1)
        else:
            hands_dict[hands[0]][0].money += self.pot
            self.pot = 0
            print(2)





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

# FLOP
newGame.round = "Flop"
# Shows flop cards
newGame.deck.reveal_cards(3)

# TURN
newGame.round = "Turn"
# Shows turn card
newGame.deck.reveal_cards(1)

# RIVER
newGame.round = "River"
# Shows river card
newGame.deck.reveal_cards(1)

# Showdown
newGame.showdown()
print([str(x) for x in newGame.player_list])

# Deck
#print(str(newGame.deck))
#print(len(newGame.deck.cards))

# Community Cards
#print([str(x) for x in newGame.comm_cards])
