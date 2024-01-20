### IMPORTS ###
from time import perf_counter_ns, sleep
from csv import reader
from math import floor, perm
from operator import itemgetter
from random import shuffle
# PokerHandEvaluator is copyrighted by Henry Lee (2016-2023) and was licensed under the Apache
# License 2.0
from phevaluator import evaluate_cards
import pied_poker as p




### CONSTANTS ###
PREFLOP_RANGES = [] # Holds 2D array of all possible hands
with open("PREFLOP_RANGES.csv", "r", encoding="utf-8") as csv_file: # Extracts data from csv
    data_reader = reader(csv_file) # Extracts data from csv_file, separated by line
    for row in data_reader:
        # Adds each individual row to PREFLOP_RANGES as its own list
        PREFLOP_RANGES.append([int(item) if item != "N" else item for item in row])

# List of card ranks
# Combines face cards with number cards (created with a range)
CARD_RANKS = tuple(str(card) for card in range(2, 11)) + ("Jack", "Queen", "King", "Ace")

# List of card suits
CARD_SUITS = ("Spades", "Hearts", "Clubs", "Diamonds")

# Dictionary of hand types
HANDS_LIST = ["HighCard", "OnePair", "TwoPair", "ThreeOfAKind", "Straight", "Flush", "FullHouse",
              "FourOfAKind", "StraightFlush", "RoyalFlush"]

# List of AIs
ai_type_list = ["TAG", "LAG", "Rock", "Maniac"]
ai_win_list = [0, 0, 0, 0]
ai_profit_list = [0, 0, 0, 0]

def hand_probability(num: int, player, comm_revealed: int, num_players: int):
    '''Finds the probability that a certain hand will occur
    Returns the probability that a certain hand will occur in a game

    Parameters:
    num - number of cards that can cause the hand to occur
    player - out (meaning hero) or killer (meaning villain)
    comm_revealed - number of community cards revealed
    num_players - number of players (including hero)'''

    # Number of spots available for cards
    # Initially set to the number of community cards
    num_spots = 5 - comm_revealed

    # Adds spots for every villain if checking for killer cards
    if player == "killer":
        num_spots += (num_players - 1) * 2

    non_hand_cards = perm(50 - comm_revealed - num, num_spots)
    all_cards = perm(50 - comm_revealed, num_spots)

    # Calculates probability that none of the remaining community cards can form a hand, then
    # finds its opposite
    return 1 - (non_hand_cards / all_cards)

print("Finished import")

full_start = perf_counter_ns()



### CLASSES ###

# Poker-playing AIs
class AI:
    '''Poker-playing AIs'''
    def __init__(self, strategy, game, preflop, aggression):
        self.strategy = strategy # AI strategy name
        self.game = game # Game which the AI is in
        self.money = 100 # Money on hand - Initially at 100
        self.hole = [] # Hand (cards held by the AI) - aka hole cards
        self.preflop = preflop # Preflop hand range (0 = tight, 0.5 = loose, 1 = very loose)
        self.aggression = aggression # Aggressiveness of preflop bets
        self.position = 0 # Position of AI relative to the big blind

    def __str__(self):
        '''Lists strategy & money
        Ex: "Strategy: Tight Aggressive", Money: 100'''
        return f"Strategy: {self.strategy}, Money: {self.money}, Position: {self.position}, Cards: {[str(card) for card in self.hole]}"

    def evaluate(self):
        '''Evaluates the hand of the deck

        Returns an integer which represents the value of the hand
        Lower values represent better hands'''

        # Total cards available for player
        hand = self.hole + self.game.comm_cards
        # Converts cards into strings which can be inputted into evaluate_cards
        hand = [f"{'T' if c.rank == '10' else c.rank[0]}{c.suit[0].lower()}" for c in hand]
        # Uses the evaluate_cards() function from PokerHandEvaluator to return score for hand
        return evaluate_cards(hand[0], hand[1], hand[2], hand[3], hand[4], hand[5], hand[6])

    def choose_hand(self):
        '''Chooses poker position from array of poker hands (from CSV) based on AI hand
        Returns an integer representing which position this can be played in out of 8 players
        Ex: integer 5 means the hand should be played only by the fifth person () or after'''

        # Sets ranks to all cards
        ranks = [CARD_RANKS.index(card.rank) for card in self.hole]
        suits = [card.suit for card in self.hole]

        if ranks[0] == ranks[1]:
            # If two cards are the same rank
            # Selects item from row & column of the first card's rank
            # Does not matter whether first or second card
            return PREFLOP_RANGES[12-ranks[0]][12-ranks[0]]
        elif suits[0] == suits[1]:
            # If the cards have the same suit (suited)
            return PREFLOP_RANGES[12-max(ranks)][12-min(ranks)]
        else:
            # If the cards are of different suits (unsuited) but have different ranks
            return PREFLOP_RANGES[12-min(ranks)][12-max(ranks)]

    def preflop_decision(self):
        '''INCOMPLETE - Performs a preflop action based on hand, round, and other bets'''

        hand_position = self.choose_hand() # Finds positions available for hand

        # Increases position that the hand is used depending on aggression
        if hand_position != "N":
            hand_position -= self.preflop

        if hand_position == "N" or hand_position < self.position:
            # Bets if no one else bet and the AI is last
            if self.position == len(self.game.ai_list):
                self.bet(self.game.largest_bet)
                return None
            else:
                # Folds if the hand is not good for the position
                self.fold()
                return None
        else:
            self.bet(self.game.highest_bet * self.aggression)
            return None

    def decision(self):
        '''INCOMPLETE - Performs an action based on hand, round, and other bets using pot odds'''

        # Checks if it is the only AI left
        if len(self.game.player_list) == 1:
            return None

        # Creates list of PiedPoker Player objects, each numbered
        players_list = [p.Player(str(num)) for num in range(len(self.game.player_list) - 1)]
        # Creates list of strings which can be used to create PiedPoker Card objects
        # List represents the hole cards of the player
        hand = [f"{'10' if c.rank == '10' else c.rank[0].lower()}{c.suit[0].lower()}" for c in
                self.hole]

        # Creates a Player object representing the AI, named "self"
        players_list.insert(0, p.Player("self", p.Card.of(hand[0], hand[1])))

        del hand

        # Creates list of strings which can be used to create Card objects
        # Represents the community cards
        cc = [f"{'10' if c.rank == '10' else c.rank[0].lower()}{c.suit[0].lower()}" for c in
              self.game.comm_cards]

        # comm - list of Card objects which represent the community cards
        # Adds first three cards
        comm = p.Card.of(cc[0], cc[1], cc[2])

        if len(cc) > 3:
            # Adds fourth card
            comm.append(p.Card(cc[3]))
            if len(cc) > 4:
                # Adds fifth card
                comm.append(p.Card(cc[4]))

        del cc

        result = p.PokerRound.PokerRoundResult(players_list, comm)

        print(result)

        # Finds hand type by turning the hand into a string, then finding the string before the
        # first "("
        # Ex: str(players_list[0].poker_hand(comm)) becomes TwoPair([A♠, A♦, 10♣, 10♠], [9♣])
        # TwoPair([A♠, A♦, 10♣, 10♠], [9♣]) becomes TwoPair
        hand = str(players_list[0].poker_hand(comm)).rsplit('(', maxsplit=1)[0]
        # Finds where it is relative to HANDS_LIST
        hand = HANDS_LIST.index(hand)
        print(hand)

        # List of outs, which are winning combinations, for the player
        # Note that they are all PiedPiper Out objects, so they need to be converted back
        outs = result.outs(players_list[0])
        print(f"outs: {outs}")

        # List number of cards available to create out
        out_cards = [len(out.cards) for out in outs]

        # List of out types
        out_types = [out.out_class for out in outs]
        # Converted to string
        out_types = [str(item).rsplit('.', maxsplit=1)[-1][:-2] for item in out_types]
        # Finds location of type
        out_types = [HANDS_LIST.index(out) for out in out_types]

        # Dictionary of outs
        # Matches each out to the number of cards which can cause the out to occur
        outs_dict = {rank:num_cards for (rank, num_cards) in zip(out_types, out_cards)}
        print(f"outs_dict: {outs_dict}")

        killer_cards = result.killer_cards(players_list[1])
        print(f"Killer_cards: {killer_cards}")

        # List number of cards available to create killer
        kill_cards = [len(out.cards) for out in killer_cards]

        # List of killer types
        killer_types = [out.killer_hand_class for out in killer_cards]
        # Converts to string
        killer_types = [str(item).rsplit('.', maxsplit=1)[-1][:-2] for item in killer_types]
        # Finds location of type
        killer_types = [HANDS_LIST.index(out) for out in killer_types]

        killer_dict = {rank:num_cards for (rank, num_cards) in zip(killer_types, kill_cards)}
        print(f"killer_dict: {killer_dict}")

        # Creates lists of list
        # Each inner list represents a specific hand
        # Has the hand type, then who has it, then the number of cards
        # Uses "out" (hero) and "killer" (villain) for consistency and easier sorting
        all_types = [[out_types[hand], "out", out_cards[hand]] for hand in range(len(out_types))]
        all_types.extend([[killer_types[hand], "killer", kill_cards[hand]] for hand in
                          range(len(killer_types))])
        all_types = sorted(all_types, key=itemgetter(0, 1), reverse=True)
        print(all_types)

        out_prob = 0
        killer_prob = 0

        for type in all_types:
            pass

        # Odds of getting a winning card
        #probability = len(winning_cards) / (50 - len(self.game.comm_cards))

        # Pot odds - ratio of bet required to call
        pot_odds = self.game.highest_bet / (self.game.highest_bet + self.game.pot)

        # checks probability
        '''if probability > pot_odds:
            #self.bet(self.game.highest_bet)
        #    pass
        else:
            if not self.game.bet_round:
                pass
            else:
                #self.fold()
                #return None
                pass'''

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

        # Indicates that bet was placed
        self.game.bet_round = True

    def fold(self):
        '''Folds cards (leaving the game) by removing AI from player_list'''
        self.game.player_list.remove(self)


class Card:
    ''' Individual cards'''

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
        return ", ".join([str(card) for card in self.cards])

    def new_deck(self):
        ''' Creates full deck of cards'''
        # Adds Card objects to cards list with each suit and rank
        # Suit goes from 2 to 15 - cards with rank 11 and above are face cards
        self.cards = [Card(suit, rank) for suit in CARD_SUITS for rank in CARD_RANKS]
        # Shuffles cards in deck using the Random function shuffle()
        shuffle(self.cards)

    def deal(self):
        '''Deals out 2 cards to all AI players'''
        # Repeats based on num
        # Gives every player a card first, then goes for the next round
        for cards in range(2):
            # Gives each player the top card from the deck, then removes that card
            for ai in self.game.ai_list:
                ai.hole.append(self.cards[0])
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
        self.ai_list = [AI("TAG 1", self, 0, 1.5), AI("TAG 2", self, 0, 1.5),
                        AI("LAG 1", self, 1, 1.5), AI("LAG 2", self, 1, 1.5),
                        AI("Maniac 1", self, 2, 2), AI("Maniac 2", self, 2, 2),
                        AI("Rock 1", self, 0, 1), AI("Rock 2", self, 0, 1)]
        shuffle(self.ai_list) # Randomizes order of players
        self.player_list = self.ai_list.copy() # List of AI playing (who did not fold)
        self.set_positions() # Updates positions of every player
        self.comm_cards = [] # Community cards
        self.pot = 0 # Pot (total amount bet by all players)
        self.highest_bet = 0 # Highest bet put down
        self.bet_round = False
        self.deck = Deck(self) # Deck of cards
        self.round = "Preflop" # Round of game

    def __str__(self):
        '''Returns round of game'''
        return self.round

    def set_positions(self):
        '''Sets position for every player based on position in player_list'''
        for ai in self.player_list:
            if self.player_list.index(ai) > 1:
                # Sets players after blinds
                ai.position = self.player_list.index(ai) - 1
            else:
                # Sets players with blinds
                ai.position = self.player_list.index(ai) + len(self.player_list) - 1

    def set_round(self, name, num):
        '''Changes each round in Holdem
        
        Parameters:
        name - name of the round
        num - number of cards revealed in the round'''
        self.round = name
        self.deck.reveal_cards(num)
        self.set_positions()
        self.bet_round = False
        for ai in self.player_list:
            if self.player_list.index(ai) < 2 and self.round == "Flop":
                ai.preflop_decision()
            else:
                ai.decision()

    def showdown(self):
        '''Showdown between all players'''

        hands_dict = {}

        for ai in self.player_list:
            if ai.evaluate() in hands_dict:
                hands_dict[ai.evaluate()].append(ai)
            else:
                hands_dict[ai.evaluate()] = [ai]
        hands = list(hands_dict.keys())
        hands.sort()

        # hands_dict[hands[0]] = list of AIs with the highest hand

        if len(hands_dict) > 0:
            for ai in hands_dict[hands[0]]:
                ai.money += floor(self.pot / len(hands_dict[hands[0]]))

        # Sets the pot to the remaining money left
        self.pot %= len(hands_dict[hands[0]])





### GAME ###
start = perf_counter_ns()
# New game
newGame = Game()

NEW_LINE = "\n"
# Players in game
print(f"\nPlayers: {NEW_LINE.join([str(z) for z in newGame.player_list])}")

# Cards of players
#print(f"\nPlayers' cards: {[str(z) + ': ' + str([str(z2) for z2 in z.hole]) for z in newGame.player_list]}")

# Deck
#print(f"\nDeck: {str(newGame.deck)}")

# Preflop
# Small blind
newGame.player_list[0].bet(2)
# Big blind
newGame.player_list[1].bet(4)

for z in newGame.player_list[2:]:
    z.preflop_decision()

# Flop
newGame.set_round("Flop", 3)
# Turn
newGame.set_round("Turn", 1)
# River
newGame.set_round("River", 1)

# Showdown
newGame.showdown()
end = perf_counter_ns()
print(end - start)
# Community Cards
#print(f"\nCommunity cards: {[str(z) for z in newGame.comm_cards]}")

# Players in game
# print(f"\nPlayers: {[str(z) for z in newGame.player_list]}")

# Deck
#print(str(newGame.deck))
#print(len(newGame.deck.cards))

# Community Cards
#print([str(z) for z in newGame.comm_cards])
