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

    # === Determine hand_type and pair_value (if needed) ===
    if card_count == 2 and ranks[0] == ranks[1]:
        hand_type = 'pair'
        if ranks[0] in ['Jack', 'Queen', 'King', 'Ace']:
            pair_value = ranks[0]
        else:
            pair_value = int(ranks[0])
    else:
        ace_count = ranks.count('Ace')
        if ace_count > 0:
            # Temporarily count all Aces as 11, then reduce if needed
            raw_value = 0
            for r in ranks:
                if r in ['Jack', 'Queen', 'King']:
                    raw_value += 10
                elif r == 'Ace':
                    raw_value += 11
                else:
                    raw_value += int(r)
            if raw_value > 21:
                hand_type = 'hard'
            else:
                hand_type = 'soft'
        else:
            hand_type = 'hard'
        pair_value = None

    # === Search for matching strategy ===
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