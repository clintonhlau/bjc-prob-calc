import tkinter as tk
import random
from itertools import chain
import json
import os
from bjc_helpers import calculate_hand_value, get_recommendation, load_strategy_from_json
from bjc_monte_carlo_sim import run_monte_carlo_sim

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


def dealer_play():
    global dealer_hand, deck
    dealer_total = calculate_hand_value(dealer_hand)
    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = calculate_hand_value(dealer_hand)
    return dealer_total

def run_simulation():
    # Extract current hand & dealer card
    player_ranks = [card[0] for card in player_hand]  # Extract ranks like '10', 'Jack'
    dealer_upcard_rank = dealer_hand[0][0]

    win_rate, draw_rate, loss_rate = run_monte_carlo_sim(player_ranks, dealer_upcard_rank, strategy)
    
    # Display result in UI
    simulation_label.config(
        text=f"Win: {win_rate:.2f}% | Draw: {draw_rate:.2f}% | Loss: {loss_rate:.2f}%"
    )
    
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

player_balance = 100
bet_amount = 10
current_bet = 0

def deal_cards():
    global deck, player_hand, dealer_hand, dealer_hidden_card, player_balance, current_bet

    if player_balance < bet_amount:
        result_label.config(text="Balance is too low!")
        disable_action_buttons()
        return
    
    player_balance -= bet_amount
    current_bet = bet_amount
    update_balance_label()
    
    deck = create_deck()
    player_hand.clear()
    dealer_hand.clear()
    
    # Deal alternately
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hidden_card = deck.pop()  # Hidden initially

    update_ui()
    run_simulation()

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
            payout_win("blackjack")
        return
    elif dealer_total == 21:
        dealer_hand.append(dealer_hidden_card)
        update_ui()
        result_label.config(text = "Unlucky, Dealer Blackjack! Dealer Wins!")
        disable_action_buttons()
        return
    
    current_bet = bet_amount
    enable_action_buttons()

def update_balance_label():
    balance_label.config(text=f"Balance: ${player_balance}")

def payout_win(result):
    global player_balance, current_bet

    if result == "standard" or result == "blackjack":
        player_balance += current_bet * 2
    elif result == "blackjack5":
        player_balance += current_bet * 5
    elif result == "blackjack4":
        player_balance += current_bet * 4
    elif result == "blackjack3":
        player_balance += current_bet * 3

    update_balance_label()
    disable_action_buttons()

def payout_draw():
    global player_balance
    player_balance += current_bet  # Return bet
    update_balance_label()
    disable_action_buttons()

def compare_blackjack(player_hand, dealer_hand):
    player_face = get_face_card(player_hand)
    dealer_face = get_face_card(dealer_hand)

    if face_card_rankings[player_face] > face_card_rankings[dealer_face]:
        result_label.config(text = f"BLACKJACK ALL AROUND! (5 to 1)\nPlayer's {player_face} beats the Dealer's {dealer_face}")
        payout_win("blackjack5")
    elif face_card_rankings[player_face] < face_card_rankings[dealer_face]:
        result_label.config(text = f"BLACKJACK ALL AROUND! (3 to 1)\nBut Dealer's {dealer_face} beats Player's {player_face}")
        payout_win("blackjack3")
    else:
        result_label.config(text = f"BLACKJACK ALL AROUND! (4 to 1)\nPlayer and Dealer have the same 10 value card.")
        payout_win("blackjack4")

    # Update UI
def update_ui():
    recommendation, total = get_recommendation(player_hand, dealer_hand[0], strategy)

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
    run_simulation()
    
    if total > 21:
        dealer_hand.append(dealer_hidden_card)
        update_ui()
        result_label.config(text="Player BUSTS! Dealer wins.")
        disable_action_buttons()

def player_double():
    global player_balance, current_bet
    
    if player_balance < bet_amount:
        result_label.config(text="Not enough balance to double!")
        return
    
    # Deduct additional bet
    player_balance -= bet_amount
    current_bet += bet_amount
    update_balance_label()
    
    # Draw one card
    player_hand.append(deck.pop())
    update_ui()
    run_simulation()
    
    total = calculate_hand_value(player_hand)
    
    if total > 21:
        dealer_hand.append(dealer_hidden_card)
        update_ui()
        result_label.config(text="Player BUSTS after Double! Dealer wins.")
        disable_action_buttons()
    else:
        player_stand()
        disable_action_buttons()

def player_stand():
    dealer_hand.append(dealer_hidden_card)
    
    dealer_total = dealer_play()
    player_total = calculate_hand_value(player_hand)
    
    update_ui()  # Update to show both dealer cards
    run_simulation()

    if dealer_total > 21:
        result_label.config(text=f"Dealer BUSTS! Player wins!")
        payout_win("standard")
    elif dealer_total > player_total:
        result_label.config(text=f"Dealer wins with {dealer_total}")
        disable_action_buttons()
    elif dealer_total < player_total:
        result_label.config(text=f"Player wins with {player_total}!")
        payout_win("standard")
    else:
        result_label.config(text="Push (Draw)")
        payout_draw()

def disable_action_buttons():
    hit_button.config(state='disabled')
    stand_button.config(state='disabled')
    double_button.config(state='disabled')

def enable_action_buttons():
    hit_button.config(state='normal')
    stand_button.config(state='normal')

    if len(player_hand) in [2, 3] and player_balance >= bet_amount:
        double_button.config(state='normal')
    else:
        double_button.config(state='disabled')

deck = []
player_hand = []
dealer_hand = []
dealer_hidden_card = None

# Main Window Setup
root = tk.Tk()
root.title("Blackjack Challenge Calculator")
root.geometry("800x500")

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

simulation_label = tk.Label(root, text="Simulation Results: Calculating...", font=default_font)
simulation_label.grid(row=8, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", wraplength=500, justify="center", font=default_font)
result_label.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

balance_label = tk.Label(root, text=f"Balance: ${player_balance}", font=default_font)
balance_label.grid(row=9, column=0, columnspan=2, pady=10)

deal_button = tk.Button(root, text="Deal", command=deal_cards, bg="blue", fg="white")
deal_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
deal_button.config(width=20)

hit_button = tk.Button(root, text="Hit", command=player_hit, bg="green", fg="white")
hit_button.grid(row=5, column=0, pady=10, padx=10, sticky="nsew", ipadx=20, ipady=10)
hit_button.config(width=10)

double_button = tk.Button(root, text="Double", command=player_double, bg="orange", fg="white")
double_button.grid(row=5, column=2, pady=10, padx=10, sticky="nsew", ipadx=20, ipady=10)
double_button.config(width=10)

stand_button = tk.Button(root, text="Stand", command=player_stand, bg="red", fg="white")
stand_button.grid(row=5, column=1, pady=10, padx=10, sticky="nsew", ipadx=20, ipady=10)
stand_button.config(width=10)

exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="nsew")
exit_button.config(width=20)

# Start GUI loop
if __name__ == "__main__":
    root.mainloop()