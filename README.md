# blackjack-challenge-probability-calc
A Python-based Blackjack Challenge tool that:
* Provides move recommendations based on optimal strategy.
* Calculates the player's win/loss/draw probabilities using Mote Carlo simulations.
* Features a user-friendly Tkinter GUI
* Implements Blackjack Challenge-specific rules, special Blackjack conditions and pay out odds

## Features:
* Recommendation System:
  Determines optimal moves (Hit, Stand, Split, Double) based on preloaded strategy JSON files 2,3 and 4-card hands.
* Monte Carlo Simulations:
  Simulates 10,000 rounds to calculate winnning probabilities based on current player's hand and dealer's upcard.
*Blackjack Challenge Rules:
  Special handling of player/dealer Blackjacks
    - Face cards (King > Queen >  Jack > 10) impact Blackjack payouts.
* Graphical User Interface:
  Built with Tkinter, allowing easy interaction and displaying recommendations and simulation results.
  
## Project Structure
/bjc-prob-calc/

 ┣ strategies/                   # JSON strategy files (2, 3, 4 card hands)
 
 ┣ bjc_helpers.py                # Shared functions: strategy loader, hand value, recommendations
 
 ┣ bjc_prob_calc_main.py         # Main Tkinter GUI + game logic
 
 ┣ bjc_monte_carlo_sim.py        # Monte Carlo simulation logic
 
 ┣ README.md

## Key Components
### 1. bjc_helpers.py:
  * load_strategy_from_json() - Loads and parses strategy JSON files
  * calculate_hand_value() - Calculates hand total, handles Ace as 1 or 11
  * get_recommendation() - Provides optimal moves based on strategy
  * card_value() - Converts card ranks (Jack, Queen, etc.) to numerical values
### 2. bjc_prob_calc_main.py:
  * Handles game flow and card dealing
  * Integrates UI components (buttons, labels)
  * Displays strategy recommendations and player/dealer hands
  * Includes action buttons:
    * Hit
    * Stand
    * Deal
    * Simulate Odds (run Monte Carlo Simulation and display win probabilities)
    * Exit
### 3. bjc_monte_carlo_sim.py:
  * Runs 10,000 of simulated Blackjack rounds based on the current hand
  * Follows optimal strategy from get_recommendation() in each simulation
  * Outputs estimated win,draw, and loss percentages

## Planned Improvements
  * Allow player to make bets
  * Add double and split options
  * Improve Monte Carlo simulation
  * Improve quality of GUI
