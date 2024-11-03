# ADCC Elo Rating Engine

This project implements an Elo rating engine for ADCC (Abu Dhabi Combat Club) grappling matches. It calculates Elo ratings for each athlete based on match outcomes, with adjustments for winning methods like submissions.

# Dataset

Dataset is obtained through kaggle
Here's the link to the dataset : https://www.kaggle.com/datasets/bjagrelli/adcc-historical-dataset/data

## Features

- Calculates Elo ratings for each ADCC competitor.
- Adjusts the K-factor based on match win method (submission, decision).
- Generates a CSV with updated Elo ratings after each match.
- Provides peak Elo ratings for all competitors.
- Supports querying specific fighter information, including match history and Elo progression.

## Future Improvements

- Dynamic K-Factor: Further refine the K-factor adjustments based on other variables like stage of competition.
- Performance Visualizations: Generate plots to track Elo progress over time for each fighter.
- Enhanced Data Filters: Filter match data by year, weight class, and stage to analyze specific trends.
