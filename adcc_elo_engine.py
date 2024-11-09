import pandas as pd
import numpy as np

# Load the CSV
bjj_matches_not_sorted = pd.read_csv("adcc_historical_data.csv", delimiter=";")
bjj_matches = bjj_matches_not_sorted.reset_index()

# Sort with the most recent at the bottom
bjj_matches = bjj_matches.sort_values(by=['year'], ascending=True)

# Create unique event IDs
unique_events = bjj_matches[['match_id']].drop_duplicates().reset_index(drop=True)
unique_events['event_id'] = range(1, len(unique_events) + 1)
bjj_matches = bjj_matches.merge(unique_events, on='match_id')

# Clean up win type to standardize (e.g., SUB, DECISION)
bjj_matches['win_type'] = bjj_matches['win_type'].apply(lambda x: 'SUB' if 'SUB' in x else ('DECISION' if 'DECISION' in x else 'POINTS'))

# Function to adjust K-factor based on win type and stages
def get_k_factor(win_type, adv_pen, stage, base_k=40):
    # Increase or decrease K based on win type
    if win_type == 'SUB':
        k_factor = base_k * 1.15  # Increase by 15% for submission
    elif win_type == 'DECISION':
        k_factor = base_k * 0.85  # Decrease by 15% for decision
    else:
        k_factor = base_k  # Default K for other outcomes

    if adv_pen == 'PEN':
        k_factor *= 0.9

    # Adjust K-factor based on stage
    stage_adjustments = {
        'SPF': 1.4,     # Super fight - 40% more

        'F': 1.3,       # Finals - 30% more

        '3RD': 1.15,    # Third Place - 15% more
        '3PLC': 1.15,

        'SF': 1.2,      # Semifinals - 20% more

        '4F': 1.1,      # Quarterfinals - 10% more
        'R2': 1.1,

        'R1': 1.0,       # First Round - no change
        'E1': 1.0,
        '8F': 1.0,
    }

    # Apply stage multiplier, default to 1 if stage isn't in adjustments
    k_factor *= stage_adjustments.get(stage, 1.0)
    
    return k_factor

# Initialize Elo ratings
initial_elo = 1000
elo_ratings = {}
base_k_factor = 40
peak_elo_ratings = {}

# Function to calculate expected score
def expected_score(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

# Function to update Elo ratings
def update_elo(winner_elo, loser_elo, k_factor):
    expected_win = expected_score(winner_elo, loser_elo)
    new_winner_elo = winner_elo + k_factor * (1 - expected_win)
    new_loser_elo = loser_elo + k_factor * (0 - (1 - expected_win))
    return round(new_winner_elo, 2), round(new_loser_elo, 2)

# Add columns for Elo ratings
bjj_matches['winner_elo_start'] = 0.0
bjj_matches['loser_elo_start'] = 0.0
bjj_matches['winner_elo_end'] = 0.0
bjj_matches['loser_elo_end'] = 0.0

# Calculate Elo ratings for each match
for index, row in bjj_matches.iterrows():
    winner = row['winner_name']
    loser = row['loser_name']

    # Initialize Elo ratings if fighters are encountered for the first time
    if winner not in elo_ratings:
        elo_ratings[winner] = initial_elo
    if loser not in elo_ratings:
        elo_ratings[loser] = initial_elo

    # Get starting Elo ratings
    winner_elo_start = elo_ratings[winner]
    loser_elo_start = elo_ratings[loser]

    # Adjust K-factor based on win type
    win_type = row["win_type"]
    adv_pen = row["adv_pen"]
    stage = row['stage']
    current_k = get_k_factor(win_type, adv_pen, stage, base_k_factor)

    # Record starting Elo ratings
    bjj_matches.at[index, 'winner_elo_start'] = winner_elo_start
    bjj_matches.at[index, 'loser_elo_start'] = loser_elo_start

    # Update Elo ratings based on match outcome
    new_winner_elo, new_loser_elo = update_elo(winner_elo_start, loser_elo_start, current_k)

    # Update peak Elo if necessary
    if winner not in peak_elo_ratings or new_winner_elo > peak_elo_ratings[winner]:
        peak_elo_ratings[winner] = new_winner_elo
    if loser not in peak_elo_ratings or new_loser_elo > peak_elo_ratings[loser]:
        peak_elo_ratings[loser] = new_loser_elo

    # Record updated Elo ratings
    bjj_matches.at[index, 'winner_elo_end'] = new_winner_elo
    bjj_matches.at[index, 'loser_elo_end'] = new_loser_elo

    # Update Elo ratings in the dictionary
    elo_ratings[winner] = new_winner_elo
    elo_ratings[loser] = new_loser_elo

# Function to get fighter information
def get_fighter_info(fighter_name, elo_ratings, bjj_matches, initial_elo=1000):
    if fighter_name in elo_ratings:
        elo = elo_ratings[fighter_name]
    else:
        elo = initial_elo

    # Find all matches involving the fighter
    fighter_matches = bjj_matches[(bjj_matches['winner_name'] == fighter_name) | 
                                  (bjj_matches['loser_name'] == fighter_name)]
    
    # Return Elo rating and their matches
    if not fighter_matches.empty:
        print(f"{fighter_name}'s current Elo rating: {elo}\n")
        print(f"{fighter_name}'s matches:")
        return fighter_matches[['match_id', 'winner_name', 'loser_name', 'win_type', 'winner_elo_start', 'loser_elo_start', 'winner_elo_end', 'loser_elo_end']]
    else:
        return f"{fighter_name} has no recorded matches."

# Export the updated matches with Elo ratings to CSV
bjj_matches.to_csv('bjj_matches_with_elo.csv', index=False)

# Peak Elo export
peak_elo = sorted(peak_elo_ratings.items(), key=lambda x: x[1], reverse=True)
peak_elo_df = pd.DataFrame(peak_elo, columns=['Fighter', 'Peak Elo'])
peak_elo_df.to_csv('peak_elo_bjj.csv', index=False)

# Export all fighters' current Elo ratings
all_fighters = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
all_fighters_df = pd.DataFrame(all_fighters, columns=['Fighter', 'Elo Rating'])
all_fighters_df.to_csv('current_fighters_elo_bjj.csv', index=False)