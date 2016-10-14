# Overview
This project accomplishes data sanitization and feature engineering for models to predict: (1) if a player is injured, will he play in the upcoming week? (2) How long will he have that injury for? 

# Data
The data utilizes NFL game data from 2009 - 2015. Each records describes a given week, player's name, physical attributes, team information, injury status, injury type, and whether or not that they play. After sanitization, the data was grouped such that it described a player's information, how long their injury lasted, and whether or not they played in that period.

# Model
Random forest models were selected for this project. 

# Validation
80/20/20 split of training, validation, and test. In addition, I note the accuracy of the models with the current 2016 NFL season.

# Use
The model is available to use online at injurycast.win

# Other notes
This was a 3-week project for the Insight Data science program.

