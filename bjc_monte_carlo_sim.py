import numpy as np
from bjc_helpers import calculate_hand_value, get_recommendation, card_value

def create_sim_deck():
    ranks = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace'])
    deck = np.tile(ranks, 4)
    return deck

def run_monte_carlo_sim(player_hand_ranks, dealer_upcard_rank, strategy):
    win_count = 0
    loss_count = 0
    draw_count = 0
    nsims = 10000

    player_total = calculate_hand_value(player_hand_ranks)
    dealer_upcard_value = card_value(dealer_upcard_rank)

    if player_total == 21:
    # 100% win rate
        return 100.0, 0.0, 0.0

    if dealer_upcard_value == 10 or dealer_upcard_value == 11:
    # Assume dealer has Blackjack (conservative)
        return 0.0, 0.0, 100.0


    for _ in range(nsims):
        deck = create_sim_deck()
        np.random.shuffle(deck)

        temp_deck = list(deck)
        for rank in player_hand_ranks:
            temp_deck.remove(rank)
        temp_deck.remove(dealer_upcard_rank)

        player_hand = [(rank, 'Hearts') for rank in player_hand_ranks]  # Dummy suits (suits dont matter)
        dealer_upcard_tuple = (dealer_upcard_rank, 'Spades')

        recommendation, total = get_recommendation(player_hand, dealer_upcard_tuple, strategy)

        while recommendation == 'Hit':
            next_card = temp_deck.pop()
            player_hand.append((next_card, 'Diamonds'))  # Dummy suit
            recommendation, total = get_recommendation(player_hand, dealer_upcard_tuple, strategy)
            if total > 21:
                break  # Bust

        player_total = calculate_hand_value([card[0] for card in player_hand])

        player_hand = player_hand_ranks.copy()
        player_total = calculate_hand_value(player_hand)
        temp_idx = 0

        while player_total < 17:
            next_card = temp_deck.pop(temp_idx)
            player_hand.append(next_card)
            player_total = calculate_hand_value(player_hand)
            if player_total > 21:
                break 

        # --- Dealer's Turn ---
        dealer_hand = [dealer_upcard_rank]
        dealer_total = calculate_hand_value(dealer_hand)

        while dealer_total < 17:
            next_card = temp_deck.pop()
            dealer_hand.append(next_card)
            dealer_total = calculate_hand_value(dealer_hand)
            if dealer_total > 21:
                break
        
        # --- Calculate Results ---
        if player_total > 21:
            loss_count += 1
        elif dealer_total > 21:
            win_count += 1
        elif player_total > dealer_total:
            win_count += 1
        else:
            draw_count += 1
    
    win_rate = (win_count / nsims) * 100
    draw_rate = (draw_count / nsims) * 100
    loss_rate = (loss_count / nsims) * 100

    return win_rate, draw_rate, loss_rate