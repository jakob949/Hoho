from itertools import combinations
import numpy as np
import random, time

start = time.time()

class Player:
    def __init__(self, player_id, stack):
        self.player_id = player_id
        self.hand = []
        self.stack = stack
        self.is_dealer = False
        self.bet = 0
        self.raise_flag = False
        self.fold = False
        self.all_in = False

    def receive_cards(self, cards):
        self.hand = cards

    # Inside Player class
    def fold_card(self, game):
        self.fold = True
        game.players.remove(self)

    def set_dealer(self, is_dealer):
        self.is_dealer = is_dealer

    def __str__(self):
        return f"Player {self.player_id} (Dealer: {self.is_dealer}): {self.hand}, stack: {self.stack}, folded: {self.fold}, all-in: {self.all_in}"


class game:
    def __init__(self, game_id, pot=0, players=[]):
        self.game_id = game_id
        self.pot = pot
        self.players = players
        self.table = []
        self.side_pots = []



deck = np.array(['14H','02H','03H','04H','05H','06H','07H','08H','09H','10H','11H','12H','13H',
                '14D','02D','03D','04D','05D','06D','07D','08D','09D','10D','11D','12D','13D',
                '14S','02S','03S','04S','05S','06S','07S','08S','09S','10S','11S','12S','13S',
                '14C','02C','03C','04C','05C','06C','07C','08C','09C','10C','11C','12C','13C'])

rank_dict = {'02': 2, '03': 3, '04': 4, '05': 5, '06': 6, '07': 7, '08': 8, '09': 9, '10': 10, '11': 11, '12': 12,
             '13': 13, '14': 14}

def give_cards_start(num_of_players=4, deck=deck):
    """
    The function returns random cards for both the deck and players
    return [0] = [deck cards]
    return[1] = [[cards_p1],[cards_p2]....]
    """
    deck = np.copy(deck)  # Create a copy of the deck to avoid altering the original
    player_cards = []

    for i in range(num_of_players):
        player_hand = []
        for j in range(2):
            temp = random.choice(range(len(deck)))
            player_hand.append(deck[temp])
            deck = np.delete(deck, temp)
        player_cards.append(player_hand)

    return deck, player_cards

def give_cards_table(deck=deck, num_of_cards = None):
    """
    The function returns random cards for table
    return [0] = [deck cards]
    return[1] = [table_cards]
    """
    deck = np.copy(deck)  # Create a copy of the deck to avoid altering the original
    table_cards = []
    if num_of_cards == None:
        return deck, table_cards
    for i in range(num_of_cards):
        temp = random.choice(range(len(deck)))
        table_cards.append(deck[temp])
        deck = np.delete(deck, temp)

    return deck, table_cards
def raise_flag(player, players):
    player.raise_flag = True
    for other_player in players:
        if other_player.player_id != player.player_id:
            other_player.raise_flag = False
def rotate_dealer(players):
    for i, player in enumerate(players):
        if player.is_dealer:
            player.set_dealer(False)
            players[(i + 1) % len(players)].set_dealer(True)
            return


def manage_and_create_side_pots(game, players):
    # Reset side pots
    game.side_pots = []
    # Sort all-in players by their bet amount
    all_in_players = sorted([p for p in players if p.all_in], key=lambda x: x.bet, reverse=False)
    print(f"side pot: {game.pot}", end="\n\n")
    # Keep track of players who have been considered for side pots
    considered_players = []
    # Keep track of players who can win each side pot
    for p_all_in in all_in_players:
        considered_players.append(p_all_in.player_id)
        players_who_can_win_the_side_pot = [p_all_in.player_id]
        side_pot = p_all_in.bet

        for p in players:
            if p.player_id in considered_players:
                continue
            if p.bet < p_all_in.bet:
                side_pot += p.bet
                p.bet = 0
                considered_players.append(p.player_id)
            elif p.bet >= p_all_in.bet:
                side_pot += p_all_in.bet
                p.bet -= p_all_in.bet
                players_who_can_win_the_side_pot.append(p.player_id)


        # The side pot should also have the pot from the previous rounds
        # side_pot += game.pot
        # Create a side pot and associate it with the players who can win it
        # use the player-id as a unique identifier for the side pot in the players_who_can_win_the_side_pot
        game.pot -= side_pot
        print(f"side pot: {side_pot}, players: {players_who_can_win_the_side_pot}")
        print(f"pot: {game.pot}")


        game.side_pots.append({"amount": side_pot, "players": players_who_can_win_the_side_pot})


# Function to evaluate a single 5-card poker hand
# Updating the evaluate_hand function to return the highest card not part of the rank determining cards
def evaluate_hand(hand):
    ranks = [rank_dict[card[:-1]] for card in hand]
    suits = [card[-1] for card in hand]

    # Count occurrences of each rank and each suit
    rank_count = {rank: ranks.count(rank) for rank in ranks}
    suit_count = {suit: suits.count(suit) for suit in suits}

    # Check for flush (5 cards of the same suit)
    flush = max(suit_count.values()) == 5

    # Check for straight (5 consecutive ranks)
    sorted_ranks = sorted(list(set(ranks)))
    straight = len(sorted_ranks) == 5 and sorted_ranks[-1] - sorted_ranks[0] == 4

    remaining_cards = sorted(ranks)
    # Determine hand rank
    if flush and straight:
        remaining_cards.remove(sorted_ranks[-1])
        return 8, sorted_ranks[-1], max(remaining_cards)  # Straight flush
    elif 4 in rank_count.values():
        four_kind_rank = max(rank for rank, count in rank_count.items() if count == 4)
        remaining_cards = [r for r in remaining_cards if r != four_kind_rank]
        return 7, four_kind_rank, max(remaining_cards)  # Four of a kind
    elif 3 in rank_count.values() and 2 in rank_count.values():
        three_kind_rank = max(rank for rank, count in rank_count.items() if count == 3)
        remaining_cards = [r for r in remaining_cards if r != three_kind_rank]
        return 6, three_kind_rank, max(remaining_cards)  # Full house
    elif flush:
        remaining_cards.remove(sorted_ranks[-1])
        return 5, sorted_ranks[-1], max(remaining_cards)  # Flush
    elif straight:
        remaining_cards.remove(sorted_ranks[-1])
        return 4, sorted_ranks[-1], max(remaining_cards)  # Straight
    elif 3 in rank_count.values():
        three_kind_rank = max(rank for rank, count in rank_count.items() if count == 3)
        remaining_cards = [r for r in remaining_cards if r != three_kind_rank]
        return 3, three_kind_rank, max(remaining_cards)  # Three of a kind
    elif len([rank for rank, count in rank_count.items() if count == 2]) == 2:
        pair_rank = max(rank for rank, count in rank_count.items() if count == 2)
        remaining_cards = [r for r in remaining_cards if r != pair_rank]
        return 2, pair_rank, max(remaining_cards)  # Two pair
    elif 2 in rank_count.values():
        pair_rank = max(rank for rank, count in rank_count.items() if count == 2)
        remaining_cards = [r for r in remaining_cards if r != pair_rank]
        return 1, pair_rank, max(remaining_cards)  # One pair
    else:
        return 0, sorted_ranks[-1], max(sorted(ranks[:-1]))  # High card



def evaluate_hands(game):
    table = game.table
    players = game.players
    hands = [(player.hand, player.player_id) for player in players if not player.fold]

    best_hand_value = (-1, -1)
    best_hand = None
    index_for_best_hand = None
    for i, hand_and_id in enumerate(hands):
        hand = hand_and_id[0]
        player_id = hand_and_id[1]
        # Generate all possible 5-card hands from the player's hand and the table
        possible_hands = list(combinations(hand + table, 5))
        # Evaluate each possible hand and keep track of the best one
        for possible_hand in possible_hands:
            hand_value = evaluate_hand(possible_hand)
            if hand_value > best_hand_value:
                index_for_best_hand = player_id
                best_hand_value = hand_value
                best_hand = possible_hand
    return best_hand, best_hand_value, hands[index_for_best_hand]
def check_if_bet_raise_call_is_valid(player, bet_size, big_blind, current_bet):
    if bet_size >= (player.stack+player.bet):
        # all-in
        print(f"player {player.player_id} is all in. With a bet/raise to {player.bet + player.stack}")
        player.all_in = True
        return "all_in", player.bet + player.stack
    elif big_blind+current_bet > bet_size:
        # Bet is too small (< big_blind)
        print(bet_size, 'big blind', big_blind+current_bet)
        while big_blind+current_bet > bet_size:
            bet_size = int(input(f"Raise amount is too small, of {bet_size}. Minimum raise is to {big_blind + current_bet}: "))
        return "valid", bet_size
    else:
        return "valid", bet_size
def ask_for_bets(players, game, current_bet=0, before_flop=False, big_blind=20):
    dealer_index = 0
    for i, player in enumerate(players):
        if player.is_dealer:
            dealer_index = i
            break

    if before_flop:
        off_set = 3
    else:
        off_set = 1

    while True:
        for i in range(dealer_index + off_set, dealer_index + len(players) + off_set):
            print(f"Player {players[i % len(players)].player_id} is next\n")
            player = players[i % len(players)]

            if player.raise_flag:
                print("Break - raise_flag")
                break

            if player.fold or player.stack == 0:
                continue

            diff_bet = current_bet - player.bet

            if diff_bet > 0:
                print(f"Player {player.player_id}, it's your turn. To call add: {diff_bet}. You have {player.stack} left (stack). You have bet already: {player.bet}")
                action = input("What would you like to do? (/fold/call/raise): ").strip().lower()
                while action not in ["fold", "call", "raise"]:
                    action = input("What would you like to do? (/fold/call/raise): ").strip().lower()

            else:
                print(f"Player {player.player_id}, it's your turn. To call add: {diff_bet}. You have {player.stack} left (stack). You have bet already: {player.bet}")
                action = input("What would you like to do? (/check/bet/fold): ").strip().lower()
                while action not in ["check", "bet", "fold"]:
                    action = input("What would you like to do? (/check/bet/fold): ").strip().lower()

            if action == "check":
                print("Player checked")
                continue

            elif action == "bet":
                bet_amount = int(input("How much would you like to bet?: "))
                valid, bet_amount = check_if_bet_raise_call_is_valid(player, bet_amount, big_blind, current_bet)
                if valid == "valid":
                    game.pot += bet_amount
                    current_bet = bet_amount
                    player.bet += bet_amount
                    player.stack -= bet_amount
                    raise_flag(player, players)
                elif valid == "all_in":
                    game.pot += player.bet
                    player.bet += player.stack
                    player.stack = 0
                    raise_flag(player, players)

            elif action == "fold":
                player.fold = True  # Mark the player as folded

            elif action == "call":
                valid, call_amount = check_if_bet_raise_call_is_valid(player, (diff_bet+player.bet), 0, current_bet)
                if valid == "valid":
                    game.pot += diff_bet
                    player.stack -= diff_bet
                    player.bet += diff_bet
                elif valid == "all_in":
                    game.pot += player.stack
                    player.bet += player.stack
                    player.stack = 0
                    # raise_flag(player, players)

            elif action == "raise":
                raise_amount = int(input("How much would you like to raise to?: "))
                valid, raise_amount = check_if_bet_raise_call_is_valid(player, raise_amount, big_blind, current_bet)
                if valid == "valid":
                    diff = raise_amount - player.bet
                    player.stack -= diff
                    game.pot += diff
                    current_bet = raise_amount
                    player.bet = raise_amount
                    raise_flag(player, players)
                elif valid == "all_in":
                    current_bet = raise_amount
                    player.bet += player.stack
                    game.pot += player.bet
                    player.stack = 0
                    raise_flag(player, players)
            print(f"Pot: {game.pot}")
            for player in players:
                print(f"Player {player.player_id}\tbet: {player.bet},\tstack: {player.stack},\tfolded: {player.fold},\tall-in: {player.all_in}")
        print("----")

        # Check if the round of betting is over
        players_left = [p for p in players if not p.fold or not p.all_in]
        # remove players who are all-in
        players_left = [p for p in players_left if not p.all_in]

        if all(p.bet == players_left[0].bet for p in players_left):
            break
        # elif all but a single player is all-in
        elif len([p for p in players if p.all_in]) == len(players) - 1:
            break

        # this is the case when a player or more is all-in, and side-pots are needed
    if any(p.all_in for p in players):
        manage_and_create_side_pots(game, players)


    # Remove folded players from the game
    game.players = [p for p in game.players if not p.fold]

    # Reset flags and bets for the remaining players
    for player in game.players:
        player.raise_flag = False
        player.bet = 0

    return

# Initialize players
num_of_players = 7
players = [Player(player_id=i, stack=((i+1)*1000)) for i in range(num_of_players)]

# Set the first player as the dealer
players[0].set_dealer(True)

# Initialize blinds
big_blind = 20
small_blind = int(big_blind / 2)

# Main game loop (for demonstration, let's run it 3 times)
for game_round in range(1):
    game = game(game_id=game_round, pot=0, players=players)

    # Rotate dealer
    rotate_dealer(players)

    # Deal cards
    deck, player_cards = give_cards_start(num_of_players=num_of_players)
    for i, player in enumerate(players):
        player.receive_cards(player_cards[i])

    # Set blinds
    for i, player in enumerate(players):
        if player.is_dealer:
            players[(i + 1) % len(players)].stack -= small_blind
            players[(i + 2) % len(players)].stack -= big_blind
            players[(i + 1) % len(players)].bet += small_blind
            players[(i + 2) % len(players)].bet += big_blind
            game.pot += small_blind + big_blind
    for player in players:
        print(player)

    # Ask for bets
    current_bet = ask_for_bets(players, game, current_bet=big_blind, before_flop=True, big_blind=big_blind)

    print(f"sub pot: {game.side_pots}")

    # Print player info
    for player in players:
        print(f"Player {player.player_id}\tbet: {player.bet},\tstack: {player.stack},\tfolded: {player.fold},\tall-in: {player.all_in}")
    print(f"pot: {game.pot}")
    # flop
    deck, table = give_cards_table(deck, 3)
    # add the list table to the game table, so that there it is not a list of lists

    game.table = table
    print("The flop is: ", table)

    # Ask for bets
    current_bet = ask_for_bets(players, game, current_bet=0, before_flop=False, big_blind=big_blind)
    for player in players:
        print(f"Player {player.player_id}\tbet: {player.bet},\tstack: {player.stack},\tfolded: {player.fold},\tall-in: {player.all_in}")
    print(f"sub pot: {game.side_pots}")
    print(f"pot: {game.pot}")


    # Print player info
    for player in players:
        print(f"Player {player.player_id}\tbet: {player.bet},\tstack: {player.stack},\tfolded: {player.fold},\tall-in: {player.all_in}")
    # turn
    deck, table = give_cards_table(deck, 1)
    game.table.extend(table)
    print("The turn is: ", game.table)
    player = game.players
    # Ask for bets
    current_bet = ask_for_bets(players, game, current_bet=0, before_flop=False, big_blind=big_blind)


    # Print player info
    for player in players:
        print(f"Player {player.player_id}\tbet: {player.bet},\tstack: {player.stack},\tfolded: {player.fold},\tall-in: {player.all_in}")
    # river
    deck, table = give_cards_table(deck, 1)
    game.table.extend(table)
    print("The river is: ", game.table)
    player = game.players
    # Ask for bets
    current_bet = ask_for_bets(players, game, current_bet=0, before_flop=False, big_blind=big_blind)


    best_hand, best_hand_value, best = evaluate_hands(game)
    print(f"Best hand: {best_hand}, value: {best_hand_value}, player: {best}")

    break
    print("----")


end = time.time()