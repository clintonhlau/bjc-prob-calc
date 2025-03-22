import tkinter as tk
import random
from itertools import chain
import json
import os
from bjc_strategy_loader import load_strategy_from_json

# === Set Working Direction ===
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# === Strategy Guide ===
# Key = (hand_type, player_total, pair_value, card_count, dealer_upcard)
# Value = Recommended move
# 3 Card Strategies
strategy ={}

for total in [9, 12]:
    strategy[('hard', total, None, 3, range(2, 12))] = 'Hit'

for dealer_upcard in chain([2], range(7, 12)):
    strategy[('hard', 10, None, 3, dealer_upcard)] = 'Hit'
for dealer_upcard in range(3, 7):
    strategy[('hard', 10, None, 3, dealer_upcard)] = 'Double'

for dealer_upcard in range(2, 7):
    strategy[('hard', 11, None, 3, dealer_upcard)] = 'Double'
for dealer_upcard in range(7, 12):
    strategy[('hard', 11, None, 3, dealer_upcard)] = 'Hit'

for dealer_upcard in chain([2], range(7, 12)):
    strategy[('hard', 13, None, 3, dealer_upcard)] = 'Hit'
for dealer_upcard in range(3, 7):
    strategy[('hard', 13, None, 3, dealer_upcard)] = 'Stand'

for total in [14, 15, 16]:
    strategy[('hard', total, None, 3, range(2, 7))] = 'Stand'
for total in [14, 15]:
    strategy[('hard', total, None, 3, range(7, 12))] = 'Hit'

for dealer_upcard in [7, 8, 11]:
    strategy[('hard', 16, None, 3, dealer_upcard)] = 'Hit'

for dealer_upcard in range(2, 11):
    strategy[('hard', 17, None, 3, dealer_upcard)] = 'Stand'
strategy[('hard', 17, None, 3, 11)] = 'Hit'

for total in range(18, 22):
    strategy[('hard', total, None, 3, range(2, 12))] = 'Stand'

for total in range(2, 19):
    strategy[('soft', total, None, 3, range(2, 12))] = 'Hit'

for dealer_upcard in range(2, 9):
    strategy[('soft', 19, None, 3, dealer_upcard)] = 'Stand'
for dealer_upcard in range(9, 12):
    strategy[('soft', 19, None, 3, dealer_upcard)] = 'Hit'

for total in [20, 21]:
    strategy[('soft', total, None, 3, range(2, 12))] = 'Stand'

def export_three_card_strategy(strategy_dict, output_file):
    json_strategy = []

    for key, recommendation in strategy_dict.items():
        hand_type, player_total, pair_value, card_count, dealer_upcard = key
        
        # Handle dealer upcard (range or int)
        if isinstance(dealer_upcard, range):
            dealer_upcard_start = dealer_upcard.start
            dealer_upcard_end = dealer_upcard.stop - 1  # Adjust because range is exclusive
        else:
            dealer_upcard_start = dealer_upcard_end = dealer_upcard
        
        json_strategy.append({
            "hand_type": hand_type,
            "player_total": player_total,
            "pair_value": pair_value,
            "card_count": card_count,
            "dealer_upcard_start": dealer_upcard_start,
            "dealer_upcard_end": dealer_upcard_end,
            "recommendation": recommendation
        })

    with open(output_file, 'w') as f:
        json.dump(json_strategy, f, indent=4)
    
    print(f"3-card strategy exported to {output_file}")

export_three_card_strategy(strategy, 'strategies/3_card_strategy.json')

# === Load Strategies JSON files ===
two_card_strategy = load_strategy_from_json('strategies/2_card_strategy.json')
three_card_strategy = load_strategy_from_json('strategies/3_card_strategy.json')
strategy = {**two_card_strategy, **three_card_strategy}

# === Game Logic Section ===
def create_deck():
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

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

def get_recommendation(player_hand, dealer_card):
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
    

# === UI Section ===

def deal_cards():
    global deck, player_hand, dealer_hand, dealer_hidden_card
    
    deck = create_deck()
    player_hand = []
    dealer_hand = []
    
    # Deal alternately
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hidden_card = deck.pop()  # Hidden initially
    
    # Update UI
    recommendation, total = get_recommendation(player_hand, dealer_hand[0])

    player_label.config(text=f"Player Hand: {total}, {player_hand}")
    dealer_label.config(text=f"Dealer's Visible Card: {dealer_hand[0]}")
    decision_label.config(text=f"Recommendation: {recommendation}")

# Main Window Setup
root = tk.Tk()
root.title("Blackjack Challenge Calculator")

# UI Components
player_label = tk.Label(root, text="Player Hand: ")
player_label.grid(row=0, column=0, columnspan=2)

dealer_label = tk.Label(root, text="Dealer's Visible Card: ")
dealer_label.grid(row=1, column=0, columnspan=2)

decision_label = tk.Label(root, text="Recommendation: ")
decision_label.grid(row=2, column=0, columnspan=2)

deal_button = tk.Button(root, text="Deal", command=deal_cards)
deal_button.grid(row=3, column=0, pady=10)

exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.grid(row=3, column=1, pady=10)

# Start GUI loop
root.mainloop()