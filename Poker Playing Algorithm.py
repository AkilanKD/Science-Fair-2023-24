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
        handScore = 0 # Score based on hand
        flush = False # Whether there is a flush, or of the same suit
        straight = False # Whether the cards are straight, or ranks in a row
        highCard = 0 # Highest card available
        totalHand = self.hand + self.game.commCards # Total cards available for player

        # Ranks of all cards in totalHand
        ranks = [x.rank for x in totalHand]
        suits = [x.suit for x in totalHand]

        #print(ranks)
        # Sorts cards by numeric order
        #ranks = sorted(ranks)

        print([str(x) for x in totalHand])

        # Number of cards per rank
        rankNum = [ranks.count(x) for x in Card.cardRanks]

        print(rankNum)

        # Number of cards per suit
        suitNum = [suits.count(x) for x in Card.cardSuits]

        print(suitNum)

        if 5 in suitNum:
            flush = True

        print(flush)

        # How to do straight flush

        if 4 in rankNum: # four of a kind
            handScore = 400
        elif 3 in rankNum:
            if 2 in rankNum: # full house
                handScore = 500
            else: # three of a kind
                handScore = 200
        elif 2 in rankNum: # two of a kind
            handScore = 100

        if flush is True and handScore < 400: # flush
            handScore = 400
        elif straight is True and handScore < 300: # straight
            handScore = 300

        if flush is True and straight is True:
            # Find a way to separate by suit
            rankBySuit = []
            handScore = 600
            print("straight flush")

        handScore += highCard
        # Adds value of highest card in pair or flush to break ties

        return handScore

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
        if amount > self.game.highestBet:
            self.game.highestBet = amount
    
    def fold(self):
        pass


# Individual cards
class Card:
    # List of card ranks
    # Combines number cards (created with a range) with face cards
    cardRanks = [str(x) for x in range(2, 11)] + ["Jack", "Queen", "King", "Ace"]
    
    # List of card suits
    cardSuits = ["Spades", "Hearts", "Clubs", "Diamonds"]

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
        self.newDeck() # Creates new deck
        self.deal(2) # Deals cards

    # Lists all cards available in deck, separated by commas
    def __str__(self):
        return ", ".join([str(x) for x in self.cards])
    
    # newDeck - creates full deck of cards
    def newDeck(self):
        # Adds Card objects to cards list with each suit and rank
        # Suit goes from 2 to 15 - cards with rank 11 and above are face cards 
        self.cards = [Card(x, y) for x in Card.cardSuits for y in Card.cardRanks]
        # Shuffles cards in deck
        shuffle(self.cards)
    
    # newDeck - deals out cards to all AI players
    # num - number of cards for each player
    def deal(self, num):
        # Repeats based on num
        # Gives every player a card first, then goes for the next round
        for a in range(num):
            # Gives each player the top card from the deck, then removes that card
            for b in self.game.aiList:
                b.hand.append(self.cards[0])
                self.cards.pop(0)
    
    # revealCards - Reveals community cards
    # num - number of cards revealed
    def revealCards(self, num):
        # Adds all cards from deck with indices from 0 (start) to num to the commCards list
        self.game.commCards.extend(self.cards[0:num])
        # Removes top cards from the deck by setting cards to to a slice of items after index num 
        self.cards = self.cards[num:]


# Game
class Game:
    def __init__(self):
        self.aiList = [AI("fdsa", self, x) for x in [0, 2, 4, 5]] # List of all AIs
        shuffle(self.aiList) # Randomizes order of players
        self.playerList = self.aiList.copy() # List of AI playing (who did not fold)
        self.commCards = [] # Community cards
        self.pot = 0 # Pot (total amount bet by all players)
        self.highestBet = 0 # Highest bet put down
        self.deck = Deck(self) # Deck of cards
        self.round = "Preflop" # Round of game
    
    # Showdown between all players
    def showdown(self):
        handsDict = {}

        for x in self.playerList:
            if x.evaluate() in handsDict:
                handsDict[x.evaluate()].append(x)
            else:
                handsDict[x.evaluate()] = [x]
        hands = list(handsDict.keys())
        hands.sort(reverse=True)

        print(handsDict)
        print(hands)

        # handsDict[hands[0]] = list of AIs with the highest hand
        for x in handsDict[hands[0]]:
            x.money += floor(self.pot / len(handsDict[hands[0]]))
        
        # Adds the 
        self.pot %= len(handsDict[hands[0]])

        if len(handsDict[hands[0]]) > 1:
            print(1)
        else:
            handsDict[hands[0]][0].money += self.pot
            self.pot = 0
            print(2)





### GAME ###

# New game
newGame = Game()


# Players in game
print([str(x) for x in newGame.playerList])

# Cards of players
print([[str(y) for y in x.hand] for x in newGame.playerList])

# Deck
print(str(newGame.deck))

# Community Cards
print([str(x) for x in newGame.commCards])


# Small blind
newGame.playerList[0].bet(2)

# Big blind
newGame.playerList[1].bet(4)

# FLOP
newGame.round = "Flop"
# Shows flop cards
newGame.deck.revealCards(3)

# TURN
newGame.round = "Turn"
# Shows turn card
newGame.deck.revealCards(1)

# RIVER
newGame.round = "River"
# Shows river card
newGame.deck.revealCards(1)

# Showdown
newGame.showdown()
print([str(x) for x in newGame.playerList])

# Deck
#print(str(newGame.deck))
#print(len(newGame.deck.cards))

# Community Cards
#print([str(x) for x in newGame.commCards])