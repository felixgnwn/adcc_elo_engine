import pandas as pd
import numpy as np
from glicko2 import Player

# Load the CSV
bjj_matches_not_sorted = pd.read_csv("adcc_historical_data.csv", delimiter=";")
bjj_matches = bjj_matches_not_sorted.reset_index()

# Sort matches by year (oldest to newest)
bjj_matches = bjj_matches.sort_values(by=['year'], ascending=True)

# Create unique event IDs
unique_events = bjj_matches[['match_id']].drop_duplicates().reset_index(drop=True)
unique_events['event_id'] = range(1, len(unique_events) + 1)
bjj_matches = bjj_matches.merge(unique_events, on='match_id')

# Clean up win type
bjj_matches['win_type'] = bjj_matches['win_type'].apply(
    lambda x: 'SUB' if 'SUB' in x else ('DECISION' if 'DECISION' in x else 'POINTS')
)

# Define stage adjustments (you already tuned these well)
stage_adjustments = {
    'SPF': 1.4,  # Superfight
    'F': 1.3,    # Final
    '3RD': 1.15, '3PLC': 1.15,
    'SF': 1.2,   # Semifinal
    '4F': 1.1, 'R2': 1.1,
    'R1': 1.0, 'E1': 1.0, '8F': 1.0
}

# Initialize Glicko-2 players
fighters = {}
def get_fighter(name):
    if name not in fighters:
        fighters[name] = Player()  # default μ=1500, φ=350
    return fighters[name]

# Track ratings and peaks
fighter_peak = {}
fighter_years = {}

# Add columns for ratings
bjj_matches['winner_rating_start'] = 0.0
bjj_matches['loser_rating_start'] = 0.0
bjj_matches['winner_rating_end'] = 0.0
bjj_matches['loser_rating_end'] = 0.0

# Process matches
for index, row in bjj_matches.iterrows():
    year = row['year']
    winner_name = row['winner_name']
    loser_name = row['loser_name']
    win_type = row['win_type']
    stage = row['stage']
    adv_pen = row['adv_pen']

    winner = get_fighter(winner_name)
    loser = get_fighter(loser_name)

    # Record pre-fight ratings
    bjj_matches.at[index, 'winner_rating_start'] = winner.rating
    bjj_matches.at[index, 'loser_rating_start'] = loser.rating

    # Base scaling multiplier (hybrid adjustment)
    k_multiplier = 1.0
    if win_type == 'SUB':
        k_multiplier *= 1.15
    elif win_type == 'DECISION':
        k_multiplier *= 0.85
    if adv_pen == 'PEN':
        k_multiplier *= 0.9
    k_multiplier *= stage_adjustments.get(stage, 1.0)

    # Apply time decay (optional)
    current_year = bjj_matches['year'].max()
    years_since = current_year - year
    decay_factor = np.exp(-0.03 * years_since)  # tune this value
    k_multiplier *= decay_factor

    # Store RD and rating before update
    loser_rd, loser_rating = loser.rd, loser.rating

    # Apply match update (winner=1, loser=0)
    winner.update_player([loser_rating], [loser_rd], [1])
    loser.update_player([winner.rating], [winner.rd], [0])

    # Apply our hybrid multiplier scaling
    rating_change_winner = (winner.rating - bjj_matches.at[index, 'winner_rating_start']) * k_multiplier
    rating_change_loser = (bjj_matches.at[index, 'loser_rating_start'] - loser.rating) * k_multiplier

    winner.rating = bjj_matches.at[index, 'winner_rating_start'] + rating_change_winner
    loser.rating = bjj_matches.at[index, 'loser_rating_start'] - rating_change_loser

    # Record post-fight ratings
    bjj_matches.at[index, 'winner_rating_end'] = winner.rating
    bjj_matches.at[index, 'loser_rating_end'] = loser.rating

    # Track peaks and active years
    fighter_peak[winner_name] = max(fighter_peak.get(winner_name, 0), winner.rating)
    fighter_peak[loser_name] = max(fighter_peak.get(loser_name, 0), loser.rating)
    fighter_years[winner_name] = fighter_years.get(winner_name, set()) | {year}
    fighter_years[loser_name] = fighter_years.get(loser_name, set()) | {year}

# === Export results ===

# Matches with ratings
bjj_matches.to_csv('bjj_matches_with_glicko.csv', index=False)

# Current ratings
fighter_current = sorted(
    [(name, player.rating) for name, player in fighters.items()],
    key=lambda x: x[1], reverse=True
)
fighter_current_df = pd.DataFrame(fighter_current, columns=['Fighter', 'Current Rating'])
fighter_current_df.to_csv('current_fighters_glicko.csv', index=False)

# Peak ratings
fighter_peak_df = pd.DataFrame(list(fighter_peak.items()), columns=['Fighter', 'Peak Rating'])
fighter_peak_df = fighter_peak_df.sort_values(by='Peak Rating', ascending=False)
fighter_peak_df.to_csv('peak_fighters_glicko.csv', index=False)

print("✅ Glicko-2 ADCC ranking calculation complete.")
