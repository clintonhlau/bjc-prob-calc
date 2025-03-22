import tkinter as tk
import random
from itertools import chain
import json
import os
import numpy as np

# === Set Working Direction ===
os.chdir(os.path.dirname(os.path.abspath(__file__)))

random = np.random.randint(5, 10)
print(random)
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

two_card_strategy = load_strategy_from_json('strategies/2_card_strategy.json')
strategy = {**two_card_strategy}

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