import requests
import pandas as pd
import datetime
import json
import time
from random import randint

# The csv file to save the data to
filename1 = "ohl-players-2023-24.csv"
filename2 = "ohl-scoring-2023-24.csv"

# The GameID for the game we want to scrape
event_list = [*range(26478, 27157+1, 1)]
# event_list = []

game_no = 0
while game_no < len(event_list):
    # The URL of the game we want to scrape, including the GameID
    event_id = event_list[game_no]
    url = "https://lscluster.hockeytech.com/feed/?feed=gc&key=f1aa699db3d81487&game_id={event_id}&client_code=ohl&tab=gamesummary&lang_code=en&fmt=json".format(event_id=event_id)

    # Sends a request to the URL to grab the data
    response = requests.get(url)

    # Gives the website a quick breather between attempts. It's earned it.
    time.sleep(randint(4,7))

    # Stores the JSON response
    fjson = response.json()

    # Extracts the home team lineup and the away team lineup AND GOALS
    hdata = fjson['GC']['Gamesummary']['home_team_lineup']['players']
    adata = fjson['GC']['Gamesummary']['visitor_team_lineup']['players']
    goals = fjson['GC']['Gamesummary']['goals']

    # Converts the JSON to a Pandas dataframe
    dfh = pd.DataFrame(hdata)
    dfa = pd.DataFrame(adata)

    # Appends the game number and a home/away flag to the dataframes
    gamenodfh = pd.DataFrame(data={'GAME_ID' : [event_list[game_no]], 'H_A' : ['H']})
    finaldfh = dfh.assign(**gamenodfh.iloc[0])
    gamenodfa = pd.DataFrame(data={'GAME_ID' : [event_list[game_no]], 'H_A' : ['A']})
    finaldfa = dfa.assign(**gamenodfa.iloc[0])

    # Specify columns to keep in our final file and their order
    col_list = ['GAME_ID', 'H_A', 'player_id', 'person_id', 'first_name', 'last_name', 'jersey_number', 'position_str', 'shots', 'shots_on', 'goals', 'assists', 'faceoff_wins', 'faceoff_attempts', 'plusminus', 'hits', 'pim']
    finaldfh = finaldfh[col_list]
    finaldfa = finaldfa[col_list]

    # Writes the lineups to a CSV file
    finaldfh.to_csv(filename1, mode='a', sep='|', encoding='utf-8', header=False)
    finaldfa.to_csv(filename1, mode='a', sep='|', encoding='utf-8', header=False)

    try:
        dfg = pd.json_normalize(goals)

        plus = []
        minus = []
        for i in [*range(0, len(dfg['plus']), 1)]:
            if len(dfg['plus'][i]) > 0:
                plus.append(' '.join(pd.json_normalize(dfg['plus'][i])['player_id'].values))
            else:
                plus.append("")
        for i in [*range(0, len(dfg['minus']), 1)]:
            if len(dfg['minus'][i]) > 0:
                minus.append(' '.join(pd.json_normalize(dfg['minus'][i])['player_id'].values))
            else:
                minus.append("")
        gamenodfg = pd.DataFrame(data={'GAME_ID': [event_list[game_no]], 'plus_ids': [plus], 'minus_ids': [minus]})
        finaldfg = dfg.assign(**gamenodfg.iloc[0])
        finaldfg = pd.concat([finaldfg, pd.DataFrame(plus), pd.DataFrame(minus)], axis=1, join="inner")

        col_list_goals = ['GAME_ID', 'home', 'period_id', 'time', 'goal_type', 'power_play', 'empty_net',
                          'penalty_shot', 'short_handed', 'goal_scorer.player_id', 'assist1_player.player_id',
                          'assist2_player.player_id', 'plus_ids', 'minus_ids']
        finaldfg = finaldfg[col_list_goals]

        finaldfg.to_csv(filename2, mode='a', sep='|', encoding='utf-8', header=False)
    except NotImplementedError:
        print("1-0 shootout game")

    game_no = game_no + 1
    print(event_id)
    print(game_no)