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


# === Load Strategies JSON files ===
two_card_strategy = load_strategy_from_json('strategies/2_card_strategy.json')
three_card_strategy = load_strategy_from_json('strategies/3_card_strategy.json')
four_card_strategy = load_strategy_from_json('strategies/4_card_strategy.json')
strategy = {**two_card_strategy, **three_card_strategy, **four_card_strategy}

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

def dealer_play():
    global dealer_hand, deck
    dealer_total = calculate_hand_value(dealer_hand)
    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = calculate_hand_value(dealer_hand)
    return dealer_total

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
face_card_rankings = {
    'King' : 4,
    'Queen' : 3,
    'Jack' : 2,
    '10' : 1
}

def get_face_card(hand):
    for card in hand:
        rank = card[0]
        if rank != 'Ace':
            return rank
    return '10'

def deal_cards():
    global deck, player_hand, dealer_hand, dealer_hidden_card
    
    deck = create_deck()
    player_hand.clear()
    dealer_hand.clear()
    
    # Deal alternately
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hidden_card = deck.pop()  # Hidden initially

    update_ui()

    # CHeck for Blackjacks
    player_total = calculate_hand_value(player_hand)
    dealer_total = calculate_hand_value([dealer_hand[0], dealer_hidden_card])

    if player_total == 21:
        if dealer_total == 21:
            dealer_hand.append(dealer_hidden_card)
            update_ui()
            compare_blackjack(player_hand, dealer_hand)
        else:
            result_label.config(text = f"BLACKJACK! (2 to 1)")
            disable_action_buttons()
        return
    elif dealer_total == 21:
        dealer_hand.append(dealer_hidden_card)
        update_ui()
        result_label.config(text = "Unlucky, Dealer Blackjack! Dealer Wins!")
        disable_action_buttons()
        return
    
    enable_action_buttons()

def compare_blackjack(player_hand, dealer_hand):
    player_face = get_face_card(player_hand)
    dealer_face = get_face_card(dealer_hand)

    if face_card_rankings[player_face] > face_card_rankings[dealer_face]:
        result_label.config(text = f"BLACKJACK ALL AROUND! (5 to 1)\nPlayer's {player_face} beats the Dealer's {dealer_face}")
        disable_action_buttons()
    elif face_card_rankings[player_face] < face_card_rankings[dealer_face]:
        result_label.config(text = f"BLACKJACK ALL AROUND! (3 to 1)\nBut Dealer's {dealer_face} beats Player's {player_face}")
        disable_action_buttons()
    else:
        result_label.config(text = f"BLACKJACK ALL AROUND! (4 to 1)\nPlayer and Dealer have the same 10 value card.")
        disable_action_buttons()

    # Update UI
def update_ui():
    recommendation, total = get_recommendation(player_hand, dealer_hand[0])

    player_label.config(text=f"Player Hand: {total}, {player_hand}")
    
    if len(dealer_hand) == 1:
        dealer_label.config(text=f"Dealer's Visible Card: {dealer_hand[0]}")
    else:
        dealer_label.config(text=f"Dealer's Hand: {dealer_hand}")
    
    decision_label.config(text=f"Recommendation: {recommendation}")
    result_label.config(text="")  # Clear result

def player_hit():
    player_hand.append(deck.pop())
    total = calculate_hand_value(player_hand)
    update_ui()
    
    if total > 21:
        dealer_hand.append(dealer_hidden_card)
        update_ui()
        result_label.config(text="Player BUSTS! Dealer wins.")
        disable_action_buttons()

def player_stand():
    dealer_hand.append(dealer_hidden_card)
    
    dealer_total = dealer_play()
    player_total = calculate_hand_value(player_hand)
    
    update_ui()  # Update to show both dealer cards
    
    if dealer_total > 21:
        result_label.config(text=f"Dealer BUSTS! Player wins!")
        disable_action_buttons()
    elif dealer_total > player_total:
        result_label.config(text=f"Dealer wins with {dealer_total}")
        disable_action_buttons()
    elif dealer_total < player_total:
        result_label.config(text=f"Player wins with {player_total}!")
        disable_action_buttons()
    else:
        result_label.config(text="Push (Draw)")
        disable_action_buttons()

def disable_action_buttons():
    hit_button.config(state='disabled')
    stand_button.config(state='disabled')

def enable_action_buttons():
    hit_button.config(state='normal')
    stand_button.config(state='normal')

deck = []
player_hand = []
dealer_hand = []
dealer_hidden_card = None

# Main Window Setup
root = tk.Tk()
root.title("Blackjack Challenge Calculator")
root.geometry("600x320")

# UI Components
default_font = ("Helvetica", 12)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
for i in range(7):  # Adjust based on total rows
    root.grid_rowconfigure(i, weight=1)

player_label = tk.Label(root, text = "Player Hand: ", font=default_font)
player_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

dealer_label = tk.Label(root, text = "Dealer's Visible Card: ", font=default_font)
dealer_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")

decision_label = tk.Label(root, text="Recommendation: ", font=default_font)
decision_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")

result_label = tk.Label(root, text="", wraplength=500, justify="center", font=default_font)
result_label.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

deal_button = tk.Button(root, text="Deal", command=deal_cards, bg="blue", fg="white")
deal_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
deal_button.config(width=20)

hit_button = tk.Button(root, text="Hit", command=player_hit, bg="green", fg="white")
hit_button.grid(row=5, column=0, pady=10, padx=10, sticky="nsew", ipadx=20, ipady=10)
hit_button.config(width=10)

stand_button = tk.Button(root, text="Stand", command=player_stand, bg="red", fg="white")
stand_button.grid(row=5, column=1, pady=10, padx=10, sticky="nsew", ipadx=20, ipady=10)
stand_button.config(width=10)

exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="nsew")
exit_button.config(width=20)

# Start GUI loop
root.mainloop()