import pandas as pd
import numpy as np

# Load and sort matches oldest to newest
bjj_matches = (
    pd.read_csv("adcc_historical_data.csv", delimiter=";")
    .sort_values(by="year", ascending=True)
    .reset_index(drop=True)
)

# Assign unique event IDs
unique_events = bjj_matches[["match_id"]].drop_duplicates().reset_index(drop=True)
unique_events["event_id"] = range(1, len(unique_events) + 1)
bjj_matches = bjj_matches.merge(unique_events, on="match_id")

# Standardise win type to SUB / DECISION / POINTS
def classify_win_type(x):
    if "SUB" in x:
        return "SUB"
    if "DECISION" in x:
        return "DECISION"
    return "POINTS"

bjj_matches["win_type"] = bjj_matches["win_type"].apply(classify_win_type)

# K-factor multipliers — tune these values to adjust rating sensitivity
STAGE_MULT = {
    "SPF": 1.4,
    "F":   1.3,
    "3RD": 1.15, "3PLC": 1.15,
    "SF":  1.2,
    "4F":  1.1,  "R2": 1.1,
    "R1":  1.0,  "E1": 1.0, "8F": 1.0,
}

WIN_TYPE_MULT = {
    "SUB":      1.15,
    "DECISION": 0.85,
    "POINTS":   1.0,
}

# PEN = win by penalty, treated as a less convincing result
ADV_PEN_MULT = {
    "PEN": 0.90,
}

BASE_K = 40

def get_k_factor(win_type, adv_pen, stage):
    k = BASE_K
    k *= WIN_TYPE_MULT.get(win_type, 1.0)
    k *= ADV_PEN_MULT.get(adv_pen, 1.0)
    k *= STAGE_MULT.get(stage, 1.0)
    return k

# Standard Elo expected score formula
INITIAL_ELO = 1000

def expected_score(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def update_elo(winner_elo, loser_elo, k):
    exp = expected_score(winner_elo, loser_elo)
    return round(winner_elo + k * (1 - exp), 2), round(loser_elo + k * (0 - (1 - exp)), 2)

# Process all matches, collect results into a list, then assign once
elo_ratings = {}
peak_elo = {}
results = []

for _, row in bjj_matches.iterrows():
    winner, loser = row["winner_name"], row["loser_name"]

    elo_ratings.setdefault(winner, INITIAL_ELO)
    elo_ratings.setdefault(loser, INITIAL_ELO)

    w_start = elo_ratings[winner]
    l_start = elo_ratings[loser]

    k = get_k_factor(row["win_type"], row["adv_pen"], row["stage"])
    w_end, l_end = update_elo(w_start, l_start, k)

    elo_ratings[winner] = w_end
    elo_ratings[loser] = l_end

    peak_elo[winner] = max(peak_elo.get(winner, 0), w_end)
    peak_elo[loser] = max(peak_elo.get(loser, 0), l_end)

    results.append({
        "winner_elo_start": w_start,
        "loser_elo_start":  l_start,
        "winner_elo_end":   w_end,
        "loser_elo_end":    l_end,
    })

# Bulk assign results — avoids slow .at[] calls inside the loop
results_df = pd.DataFrame(results, index=bjj_matches.index)
bjj_matches = pd.concat([bjj_matches, results_df], axis=1)

# Export matches with Elo ratings
bjj_matches.to_csv("bjj_matches_with_elo.csv", index=False)

# Export current ratings
(
    pd.DataFrame(sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True),
                 columns=["Fighter", "Elo Rating"])
    .to_csv("current_fighters_elo.csv", index=False)
)

# Export peak ratings
(
    pd.DataFrame(sorted(peak_elo.items(), key=lambda x: x[1], reverse=True),
                 columns=["Fighter", "Peak Elo"])
    .to_csv("peak_elo.csv", index=False)
)

print("Elo calculation complete.")