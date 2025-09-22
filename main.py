from enum import Enum
import random

class Suit(Enum):
    HEARTS = ("Hearts", "❤️")
    DIAMONDS = ("Diamonds", "♦️")
    CLUBS = ("Clubs", "♣️")
    SPADES = ("Spades", "♠️")
    JOKER = ("Joker", "🃏")

    def __str__(self):
        return self.value[1]

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    JOKER = 15

    def __init__(self, *args):
        super().__init__(*args)

    def __lt__(self, other):
        if isinstance(other, Rank):
            return self.value < other.value
        return NotImplemented
    
    def __str__(self):
        if self == Rank.JOKER:
            return "🃏"
        elif self.value <= 10:
            return str(self.value)
        elif self == Rank.JACK:
            return "J"
        elif self == Rank.QUEEN:
            return "Q"
        elif self == Rank.KING:
            return "K"
        elif self == Rank.ACE:
            return "A"
        else:
            return "?"

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f" {self.rank}{self.suit} "

    def __lt__(self, other):
        if isinstance(other, Card):
            return self.rank < other.rank
        return NotImplemented

class Deck:
    def __init__(self, no_of_decks=1):
        self.no_of_decks = no_of_decks
        self.cards = []
        for _ in range(no_of_decks):
            self.cards.extend(self.create_deck())
        random.shuffle(self.cards)

    def create_deck(self):
        deck = [Card(rank, suit) for suit in Suit if suit != Suit.JOKER for rank in Rank if rank != Rank.JOKER]*self.no_of_decks
        deck.extend([Card(Rank.JOKER, Suit.JOKER)]*self.no_of_decks)
        return deck

    def create_shuffled_deck(self):
        deck = self.create_deck()
        random.shuffle(deck)
        return deck

class PlayerAction(Enum):
    MATCH = "match"
    RAISE = "raise"
    FOLD = "fold"
    SHOW = "show"
    SIDE_SHOW = "side_show"

    def __str__(self):
        return self.value

    def get_move(self):
        return self.value

class GameTheme:
    def is_joker(self, card):
        return card.rank == Rank.JOKER

    def lt(self, cards1, card2s2):
        for c1, c2 in zip(sorted(cards1, reverse=True), sorted(card2s2, reverse=True)):
            if c1.rank < c2.rank:
                return True
            elif c1.rank > c2.rank:
                return False
        return False

    def generate_multiple_combinations(self, cards):
        combinations = []
        basic_combination = []

        joker_count = 0
        for card in cards:
            if self.is_joker(card):
                joker_count += 1
                continue
            basic_combination.append(card)

        if joker_count == 0:
            return [basic_combination]
        
        for i in range(joker_count):
            pass

        possible_replacements = []
        for suit in Suit:
            if suit == Suit.JOKER:
                continue
            for rank in Rank:
                if rank == Rank.JOKER:
                    continue
                new_card = Card(rank, suit)
                possible_replacements.append(new_card)

        import itertools
        combinations_of_length_r = list(itertools.combinations(possible_replacements, joker_count))

        ret = [sorted(basic_combination + list(comb), reverse=True) for comb in combinations_of_length_r]
        ret = sorted(ret, key=lambda x: [card.rank.value for card in x], reverse=True)
        return ret
    
    def should_i_continue(self, cards):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def __str__(self):
        return self.__class__.__name__

class StandardGame(GameTheme):
    def who_wins(self, players):
        # Determine the winner among the players
        winning_player = max(players, key=lambda p: p.cards)
        return winning_player

    def is_trial(self, cards) -> bool:
        # Logic to determine if the cards form a trial
        ranks = []
        for card in cards:
            if card.rank == Rank.JOKER:
                continue
            ranks.append(card.rank)
        
        if len(set(ranks)) == 1:
            return True, 85
        
        return False, 0

    def is_pure_sequence(self, cards) -> bool:
        # Logic to determine if the cards form a pure sequence
        suits = [card.suit for card in cards if card.rank != Rank.JOKER]
        if len(set(suits)) == 1:
            is_sequence, _ = self.is_sequence(cards)
            return is_sequence, 70
        return False, 0

    def is_sequence(self, cards) -> bool:
        # Check if Ace can be used as low (1) or high (14)
        has_ace = any(card.rank == Rank.ACE for card in cards)

        ranks = [card.rank.value for card in cards if card.rank != Rank.ACE]

        def foo(ranks):
            ranks.sort()
            for i in range(len(ranks) - 1):
                if ranks[i] + 1 == ranks[i + 1]:
                    continue
                else:
                    return False, 0
            return True, 60


        if has_ace:
            ret1, val1 = foo(ranks + [1])
            ret2, val2 = foo(ranks + [Rank.ACE.value])  # Ace as low
            if ret1:
                return ret1, val1
            elif ret2:
                return ret2, val2
            return False, 0
        else:
            return foo(ranks)

        
        return True, 60

    def is_color(self, cards) -> bool:
        # Logic to determine if the cards form a color
        suits = [card.suit for card in cards if card.rank != Rank.JOKER]
        return len(set(suits)) == 1, 40

    def is_pair(self, cards) -> bool:
        # Logic to determine if the cards form a pair
        ranks = [card.rank for card in cards if card.rank != Rank.JOKER]
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        return any(count > 1 for count in rank_counts.values()), 20

    def is_high_card(self, cards) -> bool:
        # Logic to determine if the cards form a high card
        return True, max(cards).rank.value # Always true if none of the above

    def get_combination_precedence(self):
        return [
            self.is_trial,
            self.is_pure_sequence,
            self.is_sequence,
            self.is_color,
            self.is_pair,
            self.is_high_card
        ]

    def who_has_own(self, player1, player2):
        for func in self.get_combination_precedence():
            ret1, val1 = func(player1.combination)
            ret2, val2 = func(player2.combination)
            if ret1 and ret2:
                if val1 > val2:
                    return player1
                elif val2 > val1:
                    return player2
                else:
                    return [player1, player2]
            elif ret1:
                return player1
            elif ret2:
                return player2

    def should_i_continue(self, cards):
        # Logic to decide if the player should continue
        multiple_combinations = self.generate_multiple_combinations(cards)

        for func in self.get_combination_precedence():
            for combination in multiple_combinations:
                ret, value = func(combination)
                if ret:
                    return True, value+max(combination).rank.value, combination, func.__name__
        return False, 0, None, None

class AllEvenJoker(StandardGame):
    def is_joker(self, card):
        if super().is_joker(card):
            return True
        return card.rank.value < 11 and card.rank.value % 2 == 0

class AllOddJoker(StandardGame):
    def is_joker(self, card):
        if super().is_joker(card):
            return True
        return card.rank.value < 11 and card.rank.value % 2 == 1

class AllRedJoker(StandardGame):
    def is_joker(self, card):
        if super().is_joker(card):
            return True
        return card.suit in (Suit.HEARTS, Suit.DIAMONDS)
    
class AllBlackJoker(StandardGame):
    def is_joker(self, card):
        if super().is_joker(card):
            return True
        return card.suit in (Suit.SPADES, Suit.CLUBS)
    
class Game1947(StandardGame):
    def is_joker(self, card):
        if super().is_joker(card):
            return True
        return card.rank in (Rank.ACE, Rank.NINE, Rank.FOUR, Rank.SEVEN)

class TeenPatti:
    def __init__(self, players, initial_bet=10, game_theme=StandardGame(), deck=None):
        self.players = players
        self.pot = 0
        self.initial_bet = initial_bet
        self.game_theme = game_theme
        self.moves = []
        self.deck = deck if deck else Deck().create_shuffled_deck()
        self.winners = []

    def remove_unauthorized_players(self):
        # TODO : Save state of removed players
        self.players = [player for player in self.players if player.get_balance() >= self.initial_bet]

    def create_shuffled_deck(self):
        return self.deck

    def distribute_cards(self, num_cards=3):
        for i in range(num_cards):
            for player in self.players:
                player.add_card(self.deck.pop())

    def get_active_players(self):
        return [player for player in self.players if player.is_active()]

    def initialize_game(self, skip_distribution=False):
        self.remove_unauthorized_players()

        for player in self.players:
            player.set_game_theme(self.game_theme)

        if not skip_distribution:
            for player in self.players:
                player.place_initial_bet(10)
                self.pot += 10
            self.deck = self.create_shuffled_deck()
            self.distribute_cards()

    def move(self, player):
        move = player.make_move(self.current_bet, len(self.get_active_players()))
        self.moves.append(move)
        self.pot += move.get_amount()
        self.current_bet = max(self.current_bet, move.get_amount())
        print(move)
        return move

    def game_over(self):
        if len(self.get_active_players()) == 1:
            return True
        if len(self.moves) > 0 and self.moves[-1].get_move() == PlayerAction.SHOW:
            return True
        return False

    def play(self, skip_distribution=False):
        self.initialize_game(skip_distribution)          

        self.current_bet = self.initial_bet

        while True:
            if self.game_over():
                break
            for player in self.get_active_players():
                if self.game_over():
                    break
                self.move(player)

        self.declare_winner()
        pass

    def declare_winner(self, won_players=None):
        if won_players is None:
            if len(self.moves) > 0 and self.moves[-1].get_move() == PlayerAction.SHOW:
                won_players = self.game_theme.who_has_own(self.get_active_players()[0], self.get_active_players()[1])
            else:
                won_players = self.get_active_players()
        
        if not isinstance(won_players, list):
            won_players = [won_players]

        self.winners = won_players

        for winner in self.winners:
            winner.declare_winner(self.pot/len(won_players))
        pass

    def get_winners(self):
        return self.winners

    def __str__(self):
        ret = ""
        if self.winners:
            ret += f"{self.game_theme} Winner is {[winner.name for winner in self.winners]} with pot {self.pot/len(self.winners)}\n"
        ret += "\tPlayers : \n"
        for player in self.players:
            ret += "\t\t" + str(player) + "\n"
        
        ret += "\n"
        ret += "\tMoves : \n"
        for move in self.moves:
            ret += "\t\t" + str(move) + "\n"

        return ret

class Move:
    def __init__(self, player, action, amount):
        self.player = player
        self.action = action
        self.amount = amount

    def get_amount(self):
        return self.amount
    
    def get_move(self):
        return self.action

    def __str__(self):
        return f"{self.player.name:<10} {self.action:<10} : {self.amount}"

class Player:
    def __init__(self, name, balance, cards=None):
        self.name = name
        self.balance = balance
        self.cards =  cards if cards else []
        self._is_active = True
        self.moves = []
        self.should_continue, self.probability, self.combination, self.reason = True, 0, self.cards, ""
        self.set_stop_reason("")

    def set_active(self, is_active):
        self._is_active = is_active
    
    def is_active(self):
        return self._is_active

    def add_move(self, move):
        self.moves.append(move)
        self.balance -= move.get_amount()
        return move

    def place_initial_bet(self, amount):
        if amount > self.get_balance():
            raise ValueError("Insufficient balance to place the bet.")
        self.balance -= amount
        return amount

    def set_game_theme(self, game_theme):
        self.game_theme = game_theme

    def get_balance(self):
        return self.balance

    def add_card(self, card):
        self.cards.append(card)

    def get_best_move(self):
        if len(self.moves) == 0:
            self.should_continue, self.probability, self.combination, self.reason = self.game_theme.should_i_continue(self.cards)
        
        return self.should_continue, self.probability, self.combination, self.reason

    def get_next_move(self, current_bet):
        if current_bet > self.get_balance():
            return PlayerAction.FOLD, "NOT ENOUGH BALANCE"
        should_continue, probability, combination, func_name = self.get_best_move()
        
        # Generate a random number between 1 and 100
        rand_num = random.randint(1, 100)
        if should_continue and rand_num <= probability:
            if probability > 80:
                return PlayerAction.RAISE, func_name
            else:
                return PlayerAction.MATCH, func_name
        return PlayerAction.FOLD, f"MAY BE NOT PROBABLE AFTER {len(self.moves)}"

    def set_stop_reason(self, reason):
        self.stop_reason = reason

    def fold(self, stop_reason="Folded"):
        self.set_active(False)
        self.set_stop_reason(stop_reason)
        return self.add_move(Move(self, PlayerAction.FOLD, 0))

    def show(self, stop_reason="Showed"):
        self.set_stop_reason(stop_reason)
        return self.add_move(Move(self, PlayerAction.SHOW, 0))

    def last_moves_matches(self, moves_to_match, count=2):
        if len(self.moves) < count:
            return False
        for move in self.moves[-count:]:
            if move.action not in moves_to_match:
                return False
        return True

    def make_move(self, current_bet, current_player_count, all_moves=[]) -> Move:
        action, reason = self.get_next_move(current_bet)
        if action == PlayerAction.FOLD:
            return self.fold(reason)
        elif action in (PlayerAction.MATCH, PlayerAction.RAISE):
            if current_bet > self.get_balance():
                raise ValueError("Insufficient balance to make the move.")
            if action == PlayerAction.RAISE:
                current_bet += 10  # Example raise amount
            else:
                # Check if last 2 moves are MATCH. If so, FOLD
                if self.last_moves_matches([PlayerAction.MATCH], count=5):
                    if current_player_count == 2:
                        return self.show("CALLED SHOW")
                    return self.fold("DOING SAME")
            self.balance -= current_bet
            return self.add_move(Move(self, action, current_bet))
        elif action in (PlayerAction.SHOW, PlayerAction.SIDE_SHOW):
            #return Move(self, action, 0)
            return self.fold("SOMETHING ELSE")
        else:
            raise ValueError("Invalid player action.")

    def declare_winner(self, pot):
        self.balance += pot
        self.stop_reason = "WON"

    def __str__(self):
        return f"{self.name:<10} : {self.cards} : {self.balance:<5} : {self.combination} : {self.reason:<20} : {self.probability} : {self.stop_reason}"

class InterativePlayer(Player):
    def make_move(self, current_bet, current_player_count, all_moves=[]) -> Move:
        if current_bet > self.get_balance():
            return self.fold("Not Enough Balance")

        print(f"{self.game_theme} : Current Bet: {current_bet}, Your Balance: {self.get_balance()} : Your Cards: {self.cards}")
        #print("Choose your action:")
        #print("1. Match")
        #print("2. Raise")
        #print("3. Fold")
        #print("4. Show")
        #print("5. Side Show")
        choice = input("Enter the number of your choice: ")

        if choice == '1':
            return self.add_move(Move(self, PlayerAction.MATCH, current_bet))
        elif choice == '2':
            return self.add_move(Move(self, PlayerAction.RAISE, current_bet+10))
        elif choice == '3':
            return self.fold("User Folded")
        elif choice == '4':
            return self.show("User Showed")
        elif choice == '5':
            action = PlayerAction.SIDE_SHOW
            amount = 0
        else:
            raise ValueError("Invalid choice. Please try again.")       


def case1():
    p1 = Player("Alice", 1000, [Card(Rank.FIVE, Suit.CLUBS), Card(Rank.EIGHT, Suit.SPADES), Card(Rank.SIX, Suit.CLUBS)])
    #p2 = Player("Bob", 1000, [Card(Rank.FIVE, Suit.CLUBS), Card(Rank.EIGHT, Suit.SPADES), Card(Rank.SIX, Suit.CLUBS)])
    p2 = InterativePlayer("Ajey", 1000, [Card(Rank.FOUR, Suit.HEARTS), Card(Rank.FIVE, Suit.DIAMONDS), Card(Rank.SIX, Suit.CLUBS)])

    game = TeenPatti([p1, p2], initial_bet=10, game_theme=AllOddJoker(), deck=Deck().create_shuffled_deck())
    game.play(skip_distribution=True)
    print(game)
    return game

def test1(f):
    winner_map = {}
    no_of_runs = 100
    games = []
    for i in range(no_of_runs):
        game = f()
        games.append(game)
        winners = game.get_winners()
        for winner in winners:
            winner_map[winner.name] = winner_map.get(winner.name, 0) + 1

    pass

#test1(case1)

i = 0
while True:
    i += 1
    p1 = Player("Alice", 1000)
    p2 = Player("Bob", 1000)
    p3 = Player("Charlie", 1000)
    p4 = Player("David", 1000)
    p5 = Player("Eve", 1000)
    p6 = Player("Frank", 1000)
    p7 = InterativePlayer("Ajey", 1000)

    players = [p1, p2, p3, p4, p5, p6]
    #players = [p1, p7]
    
    game_themes = [StandardGame(), AllEvenJoker(), AllOddJoker(), AllRedJoker(), AllBlackJoker(), Game1947()]
    game = TeenPatti(players, initial_bet=10, game_theme=random.choice(game_themes), deck=Deck().create_shuffled_deck())
    game.play()
    print(game)
    pass

print(p1)
print(p2)
print(p3)

pass
