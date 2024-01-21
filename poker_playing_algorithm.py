### IMPORTS ###
from time import sleep
from csv import reader, writer, QUOTE_NONNUMERIC
from math import floor, perm
from operator import itemgetter
from random import shuffle
# PokerHandEvaluator is copyrighted by Henry Lee (2016-2023) and was licensed under the Apache
# License 2.0
from phevaluator import evaluate_cards
import pied_poker as p




### CONSTANTS ###

PREFLOP_RANGES = [] # Holds 2D array of all possible hands
with open("PREFLOP_RANGES.csv", "r", encoding="utf-8") as csv_file: # Sets up csv as csv_file
    data_reader = reader(csv_file) # Creates object to read csv_file, separated by line
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


def hand_probability(num: int, player, comm_revealed: int, num_players: int):
    '''Finds the probability that a certain hand will occur
    
    Parameters:\n
    num - number of cards that can cause the hand to occur\n
    player - out (meaning hero) or killer (meaning villain)\n
    comm_revealed - number of community cards revealed\n
    num_players - number of players (including hero)\n
    
    Returns the probability that a certain hand will occur in a game'''

    # Number of spots available for cards
    # Initially set to the number of community cards
    num_spots = 5 - comm_revealed

    # Adds spots for every villain if checking for killer cards
    if player == "killer":
        num_spots += (num_players - 1) * 2

    # Total number of permutations of not selecting the card for every spot available
    non_hand_cards = perm(50 - comm_revealed - num, num_spots)
    # Total number of permutations of any card being selected for every spot available
    all_cards = perm(50 - comm_revealed, num_spots)

    # Calculates probability that none of the remaining community cards can form a hand, then
    # finds its complement
    return 1 - (non_hand_cards / all_cards)

print("Setup complete\n")





### CLASSES ###

# Poker-playing AIs
class AI:
    '''Poker-playing AIs'''
    def __init__(self, name, game, preflop, aggression):
        self.name = name # AI strategy name
        self.strategy = name.rsplit(" ")[0] # Strategy name which AI uses
        self.game = game # Game which the AI is in
        self.money = 10000 # Money on hand - Initially at 10000
        self.hole = [] # Hand (cards held by the AI) - aka hole cards
        self.preflop = preflop # Preflop hand range (0 = tight, 0.5 = loose, 1 = very loose)
        self.aggression = aggression # Aggressiveness of preflop bets
        self.position = 0 # Position of AI relative to the big blind

    def __str__(self):
        '''Lists strategy & money

        Ex: "Strategy: Tight Aggressive", Money: 100'''
        return f"Name: {self.name}, Money: {self.money}, Position: {self.position}, Cards: {[str(card) for card in self.hole]}"

    def evaluate(self):
        '''Evaluates the hand of the deck

        Returns an integer which represents the value of the hand\n
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
        '''Performs a preflop action based on hand, position, and other bets'''

        hand_position = self.choose_hand() # Finds positions available for hand

        # Increases position that the hand is used depending on aggression
        if hand_position != "N":
            hand_position -= self.preflop

        if hand_position == "N" or hand_position < self.position:
            # Calls if no one else bet (outside of blinds) and the AI is last
            if self.position == len(self.game.ai_list):
                self.bet(self.game.highest_bet)
                return None
            else:
                # Folds if the hand is not good for the position
                self.fold()
                return None
        else:
            # Calls/raises depending on aggression
            self.bet(self.game.highest_bet * self.aggression)
            return None

    def decision(self):
        '''Performs an action (after preflop) based on hand and other bets using pot odds'''

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

        # Finds hand type by turning the hand into a string, then finding the string before the
        # first "("
        # Ex: str(players_list[0].poker_hand(comm)) becomes TwoPair([A♠, A♦, 10♣, 10♠], [9♣])
        # TwoPair([A♠, A♦, 10♣, 10♠], [9♣]) becomes TwoPair
        hand = str(players_list[0].poker_hand(comm)).rsplit('(', maxsplit=1)[0]
        # Finds where it is relative to HANDS_LIST
        hand = HANDS_LIST.index(hand)

        # List of outs, which are winning combinations, for the player
        # Note that they are all PiedPiper Out objects, so they need to be converted back
        outs = result.outs(players_list[0])

        # List number of cards available to create out
        out_cards = [len(out.cards) for out in outs]

        # List of out types
        out_types = [out.out_class for out in outs]
        # Converted to string
        out_types = [str(item).rsplit('.', maxsplit=1)[-1][:-2] for item in out_types]
        # Finds location of type
        out_types = [HANDS_LIST.index(out) for out in out_types]

        killer_cards = result.killer_cards(players_list[1])

        # List number of cards available to create killer
        kill_cards = [len(out.cards) for out in killer_cards]

        # List of killer types
        killer_types = [out.killer_hand_class for out in killer_cards]
        # Converts to string
        killer_types = [str(item).rsplit('.', maxsplit=1)[-1][:-2] for item in killer_types]
        # Finds location of type
        killer_types = [HANDS_LIST.index(out) for out in killer_types]

        del result, outs, killer_cards

        # Creates lists of list
        # Each inner list represents a specific hand
        # Has the hand type, then who has it, then the number of cards
        # Uses "out" (hero) and "killer" (villain) for consistency and easier sorting
        all_types = [[out_types[hand], "out", out_cards[hand]] for hand in range(len(out_types))]
        all_types.extend([[killer_types[hand], "killer", kill_cards[hand]] for hand in
                          range(len(killer_types))])
        # Line below was based off a from a line made by John La Rooy
        all_types = sorted(all_types, key=itemgetter(0, 1), reverse=True)

        # Win & lose odds
        win_prob = 0
        lose_prob = 0
        # Odds of certain hands not occuring
        remaining_prob = 1
        for item in all_types:
            # Calculates base odds of getting certain out
            probability = hand_probability(item[2], item[1], len(self.game.comm_cards),
                                           len(self.game.player_list))

            # Adds odds that hand occurs (given that better hands didn't occur) to winning or losing
            # probabilities depending on whether it is an out or a killer card
            if type[1] == "out":
                win_prob += probability * remaining_prob
            else:
                lose_prob += probability * remaining_prob

            # Removes probability of hand occuring
            remaining_prob -= probability * remaining_prob

        # Adds odds that none of the outs/killer cards occur to the winning odds
        win_prob += remaining_prob

        # Pot odds - ratio of bet required to call
        pot_odds = self.game.highest_bet / (self.game.highest_bet + self.game.pot)

        # Checks probability
        if probability > pot_odds:
            # Uses pot odds in reverse to calculate the bet and raise
            bet = self.game.highest_bet + (self.game.highest_bet / probability) - self.game.pot
            self.bet(bet)
            return None

        else:
            # Checks (skips turn) if no one has bet yet
            if not self.game.bet_round:
                return None

            # Folds if there has been earlier betting
            self.fold()
            return None

    def bet(self, amount):
        '''Bets a given amount of money by adding it to the pot

        Parameter:\n
        amount - amount of money to bet'''

        money_bet = floor(amount)

        # Increases bet to highest_bet if it is too low
        if money_bet < self.game.highest_bet:
            money_bet = self.game.highest_bet

        # Lowers bet to max possible if bet is too high
        if self.money - amount < 0:
            money_bet = self.money

        # Moves amount bet from money to pot
        self.money -= money_bet
        self.game.pot += money_bet

        # Resets highest bet if bet was raised
        if money_bet > self.game.highest_bet:
            self.game.highest_bet = money_bet

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

        Parameter:\n
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

    def set_round(self, name: str, num: int):
        '''Changes each round in Holdem\n
        
        Parameters:\n
        name - name of the round\n
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

        # List of winning AIs
        winners = hands_dict[hands[0]]

        if len(hands_dict) > 0:
            for ai in winners:
                ai.money += int(floor(self.pot / len(winners)))

        # Sets the pot to the remaining money left
        self.pot %= len(winners)

        # List of AIs' strategies, net profit, number of games won (1 = win, 0-1 = tie with others,
        # 0 = loss), and position (doesn't use the same system for position in the rest of the code)
        ne_ai_list = [[ai.strategy, ai.money - 10000, (1 / len(winners)) if ai.money > 10000 else 0,
                        self.ai_list.index(ai)] for ai in self.ai_list]

        with open("RESULTS.csv", "a", encoding="utf-8", newline="") as file: # Opens RESULTS as file
            read_file = writer(file, quoting=QUOTE_NONNUMERIC) # Creates object to rewrite RESULTS
            read_file.writerows(ne_ai_list) # Adds all stats to RESULTS as new lines each





### GAME ###




# Asks for number of games to simulate
num_of_games = int(input("How many games would you like to simulate?\n"))

for x in range(num_of_games):
    try:
        # Creates game
        newGame = Game()

        # Preflop
        # Small blind
        newGame.player_list[0].bet(2)
        # Big blind
        newGame.player_list[1].bet(4)

        # Makes a preflop decision for non blinds
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

        # Deletes game
        del newGame

    # To handle any unforeseen errors
    except Exception as e:
        print(f"An error occurred: {e}, {type(e)}")

print("\nSimulation is complete! Your data can be found in RESULTS.csv.")
sleep(600)
