import tkinter as tk
import random
from itertools import chain

# === Strategy Guide ===
# Key = (hand_type, player_total, pair_value, card_count, dealer_upcard)
# Value = Recommended move
strategy = {}

for total in range(4, 9):
    strategy[('hard', total, None, 2, range(2, 12))] = 'Hit'

for dealer_upcard in chain(range(2, 4), range(7, 12)):
    strategy[('hard', 9, None, 2, dealer_upcard)] = 'Hit'
strategy[('hard', 9, None, 2, range(4, 7))] = 'Double'

strategy[('hard', 10, None, 2, range(2, 9))] = 'Double'
strategy[('hard', 10, None, 2, range(9, 12))] = 'Hit'

strategy[('hard', 11, None, 2, range(2, 11))] = 'Double'
strategy[('hard', 11, None, 2, 11)] = 'Hit'

for dealer_upcard in chain(range(2, 4), range(7, 12)):
    strategy[('hard', 12, None, 2, dealer_upcard)] = 'Hit'
strategy[('hard', 12, None, 2, range(4, 7))] = 'Stand'

for total in range(13, 16):
        strategy[('hard', total, None, 2, range(2, 7))] = 'Stand'
        strategy[('hard', total, None, 2, range(7, 12))] =  'Hit'

for dealer_upcard in chain(range(2, 7), [10]):
    strategy[('hard', 16, None, 2, dealer_upcard)] = 'Stand'
for dealer_upcard in chain(range(7, 10), [11]):
    strategy[('hard', 16, None, 2, dealer_upcard)] = 'Hit'

for dealer_upcard in chain(range(2, 8), range(9,11)):
    strategy[('hard', 17, None, 2, dealer_upcard)] = 'Stand'
for dealer_upcard in [8, 11]:
    strategy[('hard', 17, None, 2, dealer_upcard)] =  'Hit'

for total in range(18, 22):
    strategy[('hard', total, None, 2, range(2, 12))] = 'Stand'

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
        else:  # Ace
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
    
    # Example rule: Auto-hit under 12
    if total <= 11:
        return "Hit"
    elif total >= 17:
        return "Stand"
    elif 12 <= total <= 16:
        if dealer_value >= 7:
            return "Hit"
        else:
            return "Stand"
    else:
        return "Stand"

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
    player_label.config(text=f"Player Hand: {player_hand}")
    dealer_label.config(text=f"Dealer's Visible Card: {dealer_hand[0]}")
    
    recommendation = get_recommendation(player_hand, dealer_hand[0])
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