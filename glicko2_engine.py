import pandas as pd
import numpy as np
from collections import defaultdict
from glicko2 import Player

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

# Outcome weighting — instead of overriding ratings post-hoc (which breaks RD
# consistency), we pass a weighted float outcome directly to Glicko-2.
# Glicko-2 accepts floats, so 1.15 for a submission win is valid.
# Tune these multipliers to adjust how much each factor influences ratings.
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

def outcome_weight(win_type, adv_pen, stage):
    w = 1.0
    w *= WIN_TYPE_MULT.get(win_type, 1.0)
    w *= ADV_PEN_MULT.get(adv_pen, 1.0)
    w *= STAGE_MULT.get(stage, 1.0)
    return min(max(w, 0.1), 2.0)  # clamp to a sensible range

# Fighter registry — lazily initialised with Glicko-2 defaults (μ=1500, φ=350, σ=0.06)
fighters: dict[str, Player] = {}

def get_fighter(name: str) -> Player:
    if name not in fighters:
        fighters[name] = Player()
    return fighters[name]

# Glicko-2 requires rating periods — each year is treated as one period.
# All results within a period are collected first, then ratings update once.
# This is the correct way to use Glicko-2 (unlike Elo which updates per match).
bjj_matches["winner_rating_start"] = 0.0
bjj_matches["loser_rating_start"]  = 0.0
bjj_matches["winner_rating_end"]   = 0.0
bjj_matches["loser_rating_end"]    = 0.0
bjj_matches["winner_rd_end"]       = 0.0
bjj_matches["loser_rd_end"]        = 0.0

fighter_peak  = {}
fighter_years = defaultdict(set)

years = sorted(bjj_matches["year"].unique())

for year in years:
    period_matches = bjj_matches[bjj_matches["year"] == year]

    # Snapshot all ratings at the start of the period so match order within
    # a year does not affect results (order independence)
    start_ratings = {name: (p.rating, p.rd) for name, p in fighters.items()}

    # Collect each fighter's full set of results for this period
    period_data: dict[str, dict] = defaultdict(
        lambda: {"opponents": [], "opponent_rds": [], "outcomes": [], "indices": []}
    )

    for idx, row in period_matches.iterrows():
        w_name = row["winner_name"]
        l_name = row["loser_name"]

        get_fighter(w_name)
        get_fighter(l_name)

        weight = outcome_weight(row["win_type"], row["adv_pen"], row["stage"])

        w_rating, w_rd = start_ratings.get(w_name, (1500, 350))
        l_rating, l_rd = start_ratings.get(l_name, (1500, 350))

        bjj_matches.at[idx, "winner_rating_start"] = w_rating
        bjj_matches.at[idx, "loser_rating_start"]  = l_rating

        period_data[w_name]["opponents"].append(l_rating)
        period_data[w_name]["opponent_rds"].append(l_rd)
        period_data[w_name]["outcomes"].append(weight)
        period_data[w_name]["indices"].append(idx)

        period_data[l_name]["opponents"].append(w_rating)
        period_data[l_name]["opponent_rds"].append(w_rd)
        period_data[l_name]["outcomes"].append(1.0 - weight)
        period_data[l_name]["indices"].append(idx)

        fighter_years[w_name].add(year)
        fighter_years[l_name].add(year)

    # Update all fighters who competed this period
    for name, data in period_data.items():
        fighters[name].update_player(
            data["opponents"],
            data["opponent_rds"],
            data["outcomes"],
        )

    # Fighters who did not compete get their RD widened manually.
    # The library crashes on empty lists, so we apply the Glicko-2 RD
    # decay formula directly: RD_new = min(sqrt(RD^2 + sigma^2), 350)
    for name, player in fighters.items():
        if name not in period_data:
            player.rd = min((player.rd ** 2 + player.vol ** 2) ** 0.5, 350)

    # Write end-of-period ratings back to the matching rows
    for name, data in period_data.items():
        player = fighters[name]
        fighter_peak[name] = max(fighter_peak.get(name, 0), player.rating)
        for idx in data["indices"]:
            row = bjj_matches.loc[idx]
            if row["winner_name"] == name:
                bjj_matches.at[idx, "winner_rating_end"] = player.rating
                bjj_matches.at[idx, "winner_rd_end"]     = player.rd
            elif row["loser_name"] == name:
                bjj_matches.at[idx, "loser_rating_end"] = player.rating
                bjj_matches.at[idx, "loser_rd_end"]     = player.rd

# Export matches with Glicko-2 ratings
bjj_matches.to_csv("bjj_matches_with_glicko.csv", index=False)

# Export current ratings — RD column indicates confidence (lower = more certain)
current = [
    {"Fighter": name, "Rating": p.rating, "RD": round(p.rd, 2)}
    for name, p in fighters.items()
]
(
    pd.DataFrame(current)
    .sort_values("Rating", ascending=False)
    .to_csv("current_fighters_glicko.csv", index=False)
)

# Export peak ratings
(
    pd.DataFrame(sorted(fighter_peak.items(), key=lambda x: x[1], reverse=True),
                 columns=["Fighter", "Peak Rating"])
    .to_csv("peak_fighters_glicko.csv", index=False)
)

print("Glicko-2 calculation complete.")