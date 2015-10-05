__author__ = 'YASH'


import pandas as pd
import numpy as np

filepath = "result_data\E0.csv"
teams = []
all_data = []
home_data = []
away_data = []
team_stats = []
result_types = ['A', 'D', 'H']
league_avg_gf = 0.0
league_avg_ga = 0.0
league_avg_home_gf = 0.0
league_avg_home_ga = 0.0
league_avg_away_gf = 0.0
league_avg_away_ga = 0.0

def get_result_data(file):
    csv_delimiter= ","
    df = pd.read_csv(file, sep=csv_delimiter)
    global all_data, teams
    teams = sorted(list(set(df['HomeTeam']).union(set(df['AwayTeam']))))
    all_data = df
    process_team_data()
    compute_league_statistics()
    compute_team_statistics()

def process_team_data():
    home_row_list =[]
    away_row_list =[]
    for team in teams:
        home_goals = (all_data['FTHG'][all_data['HomeTeam']==team])
        away_goals = (all_data['FTAG'][all_data['AwayTeam']==team])
        home_conceded = (all_data['FTAG'][all_data['HomeTeam']==team])
        away_conceded = (all_data['FTHG'][all_data['AwayTeam']==team])
        gp = float(min(len(home_goals), len(away_goals), len(home_conceded), len(away_conceded)))
        home_score = {"Team": team, 'Played':gp, 'GF':sum(home_goals), 'AVG_GF':sum(home_goals)/gp, 'GA':sum(home_conceded), 'AVG_GA':sum(home_conceded)/gp}
        away_score = {"Team": team, 'Played':gp, 'GF':sum(away_goals), 'AVG_GF':sum(away_goals)/gp, 'GA':sum(away_conceded), 'AVG_GA':sum(away_conceded)/gp}
        home_row_list.append(home_score)
        away_row_list.append(away_score)
    global home_data, away_data
    home_data = rearrange_cols(pd.DataFrame(home_row_list))
    away_data = rearrange_cols( pd.DataFrame(away_row_list))


def compute_league_statistics():
    global league_avg_gf, league_avg_ga, league_avg_home_ga, league_avg_home_gf, league_avg_away_ga, league_avg_away_gf
    league_avg_home_gf = np.mean(home_data['AVG_GF'])
    league_avg_home_ga = np.mean(home_data['AVG_GA'])
    league_avg_away_gf = np.mean(away_data['AVG_GF'])
    league_avg_away_ga = np.mean(away_data['AVG_GA'])
    league_avg_gf = (league_avg_home_gf + league_avg_away_gf)/2
    league_avg_ga = (league_avg_home_ga + league_avg_away_ga)/2

def compute_team_statistics():
    stats_list = []
    for team in teams:
        home_attacking =  float(home_data['AVG_GF'][home_data['Team']==team]/league_avg_home_gf)
        away_attacking =  float(away_data['AVG_GF'][home_data['Team']==team]/league_avg_away_gf)
        home_defence =  float(home_data['AVG_GA'][home_data['Team']==team]/league_avg_home_ga)
        away_defence = float(away_data['AVG_GA'][home_data['Team']==team]/league_avg_away_ga)
        score_hash= {'Team':team, 'H_Attacking': home_attacking, 'A_Attacking':away_attacking, 'H_Defence':home_defence, 'A_Defence':away_defence}
        stats_list.append(score_hash)
    global team_stats
    team_stats = rearrange_cols(pd.DataFrame(stats_list))

def rearrange_cols(x):
    cols = x.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    return x[cols]

def print_statistics(*args, **kwargs):
    all = False
    if not len(kwargs): all = True
    if bool(kwargs.get('home_data')) | (all) :
        print "****************** Home Data ********************* \n"
        print home_data
        print
    if bool(kwargs.get('away_data')) | (all):
        print "****************** Away Data ********************* \n"
        print away_data
        print
    if bool(kwargs.get('team_stats')) | (all):
        print "************************** Team Stats **************************** \n"
        print team_stats
        print

import math
def poisson_probability(actual, mean):
    if actual > 1 : added = 0.01
    else : added = 1
    p = math.exp(-mean*added)
    for i in xrange(actual):
        p *= mean
        p /= i+1
    return p

def predict_result(home_team, away_team):
    HG = float(team_stats['H_Attacking'][team_stats['Team']==str(home_team)])*float(team_stats['A_Defence'][team_stats['Team']==str(away_team)])
    AG = float(team_stats['H_Defence'][team_stats['Team']==str(home_team)])*float(team_stats['A_Attacking'][team_stats['Team']==str(away_team)])
    max_likelihood = 0
    home_team_goals = 0
    away_team_goals = 0
    for i in range(0,11):
        home_prob =  poisson_probability(i, HG)
        for j in range(0,11):
            away_prob = poisson_probability(j, AG)
            likelihood = home_prob*away_prob
            if likelihood > max_likelihood :
                max_likelihood = likelihood
                home_team_goals = i
                away_team_goals = j
    print "Prediction : " + str(home_team) + "  " + str(home_team_goals) + " - " + str(away_team_goals)  + "  " +  str(away_team)
    print
    probability = "%.2f%%" % (max_likelihood*100)
    print "Probability: " + str(probability)



get_result_data(filepath)
predict_result(home_team='Chelsea', away_team='Southampton')
