# ADCC Elo Rating Engine

This project implements rating systems for ADCC (Abu Dhabi Combat Club) grappling matches. It calculates ratings for each athlete based on match outcomes using two different systems:

1. **Traditional Elo Rating System** - Classic Elo implementation with K-factor adjustments for winning methods
2. **Glicko Rating System** - More sophisticated rating system that accounts for rating reliability and rating deviation

# Dataset

Dataset is obtained through kaggle
Here's the link to the dataset : https://www.kaggle.com/datasets/bjagrelli/adcc-historical-dataset/data

## Features

- Calculates both Elo and Glicko ratings for each ADCC competitor.
- Adjusts the K-factor based on match win method (submission, decision) for Elo system.
- Generates CSV/Excel files with updated ratings after each match.
- Provides peak ratings for all competitors.
- Supports querying specific fighter information, including match history and rating progression.

## Top 10 Rankings Comparison

### Glicko-Based Results

| Rank | Fighter | Current Rating |
|------|---------|----------------|
| 1 | Amy Campo | 2194.14 |
| 2 | Gordon Ryan | 2184.67 |
| 3 | Giancarlo Bodoni | 2122.88 |
| 4 | Kaynan Duarte | 2120.60 |
| 5 | Yuri Simoes | 2086.76 |
| 6 | Diogo Reis | 2077.02 |
| 7 | Rubens Charles | 2065.65 |
| 8 | Rafael Mendes | 2057.13 |
| 9 | Kade Ruotolo | 2033.40 |
| 10 | Marcus Almeida | 1987.49 |

### Traditional Elo-Based Results

| Rank | Fighter | Elo Rating |
|------|---------|------------|
| 1 | Gordon Ryan | 1327.69 |
| 2 | Andre Galvao | 1278.39 |
| 3 | Marcelo Garcia | 1263.64 |
| 4 | Rubens Charles | 1256.34 |
| 5 | Ricardo Arona | 1245.74 |
| 6 | Roger Gracie | 1221.22 |
| 7 | Marcus Almeida | 1209.77 |
| 8 | Royler Gracie | 1207.25 |
| 9 | Yuri Simoes | 1200.51 |
| 10 | Fabricio Werdum | 1198.54 |

### Key Differences

- **Gordon Ryan** remains #1 in traditional Elo but drops to #2 in Glicko
- **Amy Campo** tops the Glicko rankings but doesn't appear in the traditional Elo top 10
- **Kaynan Duarte** and **Kade Ruotolo** rank higher in Glicko (4th and 9th) compared to their positions outside the Elo top 10
- Several legends like **Andre Galvao**, **Marcelo Garcia**, **Ricardo Arona**, and **Roger Gracie** appear in the Elo top 10 but not in Glicko's current top 10
- Both systems agree on **Rubens Charles**, **Marcus Almeida**, and **Yuri Simoes** being elite competitors