# ADCC Elo Rating Engine

A Python-based rating engine for analyzing competitive performance in ADCC (Abu Dhabi Combat Club) submission grappling matches.

This project implements and compares two ranking systems; a traditional Elo model and a Glicko-2 model - across more than 1,000 historical ADCC matches. The engine tracks athlete performance over time, measures ranking stability, and visualizes how different rating systems evaluate elite competitors.

The project also includes a full exploratory analysis notebook with ranking comparisons, fighter career trajectories, rating distributions, rank-correlation analysis, and confidence-based evaluation using Glicko rating deviation (RD).

## Dataset

Historical ADCC match data sourced from Kaggle:
https://www.kaggle.com/datasets/bjagrelli/adcc-historical-dataset/data

### Dataset Overview

* 1,028 historical ADCC matches
* 614 unique competitors
* Coverage from 1998–2022
* Includes match outcomes, divisions, and win methods

---

# Features

## Dual Rating Engines

### Traditional Elo System

* Dynamic Elo updates after every match
* Stage-weighted K-factors for finals and medal matches
* Additional weighting based on win method (submission vs decision)
* Inactivity decay to reduce inflated legacy ratings
* Peak rating tracking for every athlete

### Glicko-2 System

* Rating + rating deviation (RD) tracking
* Confidence-aware rankings that penalize uncertainty
* Better handling of inactive or low-sample competitors
* Volatility modeling for rapidly improving athletes

---

# Analysis Notebook

The `analysis.ipynb` notebook compares both systems using statistical analysis and visualizations.

### Included Analysis

* Match volume and dataset distribution by year
* Top-ranked competitors under both systems
* Fighter career rating trajectories
* Rating distribution histograms
* Glicko rating vs rating deviation analysis
* Elo vs Glicko ranking comparison
* Spearman rank correlation between systems
* Biggest ranking disagreements between engines
* Peak vs current rating decline analysis
* Rating volatility per match
* Upset rate analysis

### Key Findings

* Spearman rank correlation between Elo and Glicko-2: **0.8962**
* 614 fighters appear in both ranking systems
* Traditional Elo produces more legacy-heavy rankings
* Glicko-2 favors active competitors while accounting for rating uncertainty through RD (Rating Deviation)
* Fighters with fewer matches can achieve high ratings in Glicko-2, but with larger uncertainty values
* Both systems strongly agree on elite competitors overall, despite major disagreements for certain mid- and lower-ranked athletes

---

<table width="100%">
<tr>
<td width="50%" valign="top">

### Glicko-2 Rankings

| Rank | Fighter          | Rating  |
| ---- | ---------------- | ------- |
| 1    | Gordon Ryan      | 2639.55 |
| 2    | Ricardo Arona    | 2431.53 |
| 3    | Royler Gracie    | 2380.82 |
| 4    | Rubens Charles   | 2340.81 |
| 5    | Rafael Mendes    | 2318.80 |
| 6    | Marcelo Garcia   | 2256.03 |
| 7    | Roger Gracie     | 2234.70 |
| 8    | Kaynan Duarte    | 2233.32 |
| 9    | Gabrielle Garcia | 2231.16 |
| 10   | Amy Campo        | 2214.70 |

</td>

<td width="50%" valign="top">

### Traditional Elo Rankings

| Rank | Fighter         | Rating  |
| ---- | --------------- | ------- |
| 1    | Gordon Ryan     | 1327.69 |
| 2    | Andre Galvao    | 1278.39 |
| 3    | Marcelo Garcia  | 1263.64 |
| 4    | Rubens Charles  | 1256.34 |
| 5    | Ricardo Arona   | 1245.74 |
| 6    | Roger Gracie    | 1221.22 |
| 7    | Marcus Almeida  | 1209.77 |
| 8    | Royler Gracie   | 1207.25 |
| 9    | Yuri Simoes     | 1200.51 |
| 10   | Fabricio Werdum | 1198.54 |

</td>
</tr>
</table>

---

# Interpretation

The two systems broadly agree on elite competitors, but they reward performance differently.

* Traditional Elo heavily rewards long-term dominance and accumulated wins
* Glicko-2 prioritizes recent consistency and rating confidence
* Legacy competitors such as Andre Galvao, Marcelo Garcia, and Roger Gracie remain highly ranked in Elo
* Active modern competitors such as Amy Campo, Kaynan Duarte, and Kade Ruotolo rank significantly higher in Glicko-2
* Gordon Ryan remains dominant across both systems

---

# Tech Stack

* Python
* Pandas
* NumPy
* Matplotlib
* Jupyter Notebook

---

# Project Structure

```bash
.
├── elo-engine-result/
│   ├── bjj_matches_with_elo.csv
│   ├── current_fighters_elo.csv
│   └── peak_elo.csv
├── glicko2-engine-result/
│   ├── bjj_matches_with_glicko.csv
│   ├── current_fighters_glicko.csv
│   └── peak_fighters_glicko.csv
├── adcc_historical_data.csv
├── analysis.ipynb
├── elo_engine.py
├── glicko2_engine.py
├── requirements.txt
└── README.md
```

---

# Future Improvements

* Weight matches by opponent strength and tournament prestige
* Add interactive dashboards for fighter comparisons
* Build prediction models for future ADCC matches
* Compare against TrueSkill and Bayesian ranking systems
* Deploy as a web application with searchable athlete profiles
