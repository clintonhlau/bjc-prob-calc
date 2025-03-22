import json

# === Load Strategies JSON files ===
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