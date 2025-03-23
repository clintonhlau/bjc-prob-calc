import json

def load_strategy_from_json(file_path):
    strategy = {}

    with open(file_path, 'r') as f:
        json_data = json.load(f)
    
    for entry in json_data:
        hand_type = entry['hand_type']
        player_total = entry['player_total']
        pair_value = entry['pair_value']
        card_count = entry['card_count']
        dealer_upcard_start = entry['dealer_upcard_start']
        dealer_upcard_end = entry['dealer_upcard_end']
        recommendation = entry['recommendation']

        if dealer_upcard_start == dealer_upcard_end:
            dealer_upcard = dealer_upcard_start
        else:
            dealer_upcard = range(dealer_upcard_start, dealer_upcard_end + 1)

        strategy[(hand_type, player_total, pair_value, card_count, dealer_upcard)] = recommendation
    
    return strategy

def calculate_hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        rank = card[0]
        if rank.isdigit():
            value += int(rank)
        elif rank in ['Jack', 'Queen', 'King']:
            value += 10
        else: 
            ace_count += 1
            value += 11
    
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

def get_recommendation(player_hand, dealer_card, strategy):
    total = calculate_hand_value(player_hand)
    dealer_value = dealer_card[0]
    if dealer_value in ['Jack', 'Queen', 'King']:
        dealer_value = 10
    elif dealer_value == 'Ace':
        dealer_value = 11
    else:
        dealer_value = int(dealer_value)

    ranks = [card[0] for card in player_hand]
    card_count = len(player_hand)

    total = calculate_hand_value(player_hand)

    if card_count == 2 and ranks[0] == ranks[1]:
        hand_type = 'pair'
        if ranks[0] in ['Jack', 'Queen', 'King', 'Ace']:
            pair_value = ranks[0]
        else:
            pair_value = int(ranks[0])
    
    elif 'Ace' in ranks:
        hand_type = 'soft'
        pair_value = None
    else:
        hand_type = 'hard'
        pair_value = None
    
    # Search through strategy dictionary for recommendation
    for key, recommendation in strategy.items():
        k_hand_type, k_total, k_pair, k_card_count, k_dealer_upcard = key

        if hand_type != k_hand_type:
            continue

        if hand_type == 'pair':
            if pair_value != k_pair:
                continue
        else:
            if total != k_total:
                continue

        if card_count != k_card_count:
            continue

        if isinstance(k_dealer_upcard, range):
            if dealer_value not in k_dealer_upcard:
                continue
        elif dealer_value != k_dealer_upcard:
            continue

        return recommendation, total
    
    return 'No recommendation found', total

def card_value(rank):
    if rank in ['Jack', 'Queen', 'King']:
        return 10
    elif rank == 'Ace':
        return 11
    else:
        return int(rank)