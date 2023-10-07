from flask import Flask, send_file, render_template, request

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen
import pandas as pd

import os
import io
import base64
import sqlite3



app = Flask(__name__)



home_team = 'Barcelona'

def get_all_teams():
    conn = sqlite3.connect("games.db")
    cur = conn.cursor()
    cur.execute('''
    SELECT team_name FROM (
        SELECT home AS team_name FROM game
        UNION
        SELECT away AS team_name FROM game
    ) AS teams
    ORDER BY team_name ASC;
                ''')
    rows = cur.fetchall()
    # Extract unique team names from the rows
    teams_names= {row[0] for row in rows if row[0]}
    teams_names = sorted(list(teams_names))
   #print(teams_names)
    return teams_names

def get_opponents(homeTeam):
    conn = sqlite3.connect("games.db")
    cur = conn.cursor()
    cur.execute(''' 
    
   SELECT DISTINCT opponent
        FROM (
            SELECT
                CASE
                    WHEN home = ? THEN away
                    ELSE home
                END AS opponent
            FROM game
            WHERE home = ? OR away = ?
        ) AS opponents
        ORDER BY opponent ASC;
    ''', (homeTeam, homeTeam, homeTeam))

    opponents = [row[0] for row in cur.fetchall()]
    conn.close()
    #print(opponents)
    return opponents

def find_game(homeTeam, opponent):
    conn = sqlite3.connect("games.db")
    cur = conn.cursor()
    cur.execute('''
        SELECT file_num
        FROM game
        WHERE (home = ? AND away = ?)
           OR (home = ? AND away = ?);

        ''', (homeTeam, opponent, opponent, homeTeam))
    
    game_ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return game_ids


@app.route('/')
def plot():
    global home_team
    global selectedTeam
    global selectedOpponent
    

    home = request.args.get('home')
    if home == '' or home is None:
        home_team = home_team
    else:
        home_team = home
        
    

    teams = get_all_teams()
    opponents = get_opponents(home_team)

    away = request.args.get('away')
    if away == '' or away is None:
        selectedOpponent = opponents[0]
    else:
        selectedOpponent = away

    
    select = request.args.get('select')
    if select is not None:
        if select == home_team:
            selectedTeam = selectedOpponent 
        else:
            selectedTeam = home_team
    else:
        selectedTeam = home_team


    game_id = find_game(home_team, selectedOpponent)[0]
    conn = sqlite3.connect("games.db")
    df = pd.read_sql_query('SELECT * FROM passes WHERE file_num IS ?', conn, params = (game_id,))
  

    mask = df.team_name == selectedTeam
    df_passes = df.loc[mask, ['x', 'y', 'end_x', 'end_y', 'player_name','position_name','outcome_id']]

    name_to_position = df_passes.groupby('player_name')['position_name'].first().to_dict()
    #get the list of all players who made a pass
    names = df_passes['player_name'].unique()
    
    #draw 4x4 pitches
    pitch = Pitch(line_color='black', pad_top=20)
    fig, axs = pitch.grid(ncols = 4, nrows = 4, grid_height=0.85, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0.04, endnote_space=0.01)

    #plot passes for each player
    for name, ax in zip(names, axs['pitch'].flat[:len(names)]):
        position = name_to_position[name]
        ax.text(60, -10, f'{name} ({position})', ha='center', va='center', fontsize=8)
        player_df = df_passes.loc[df_passes["player_name"] == name]
        pitch.scatter(player_df.x, player_df.y, alpha = 0.2, s = 50, color = "blue", ax=ax)
        colors = np.where(player_df['outcome_id'] == 9, 'red', 'blue')
        pitch.arrows(player_df.x, player_df.y, player_df.end_x, player_df.end_y, color = colors, ax=ax, width=1)

    #remove extra pitches
    for ax in axs['pitch'][-1, 16 - len(names):]:
        ax.remove()

    #set title
    axs['title'].text(0.5, 0.5,selectedTeam, ha='center', va='center', fontsize=20)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)

    plot_url = base64.b64encode(img_stream.getvalue()).decode('utf8')
    plt.clf()
    plt.close()
    
    return render_template('index.html', plot_url = plot_url, team1 = home_team, team2 = selectedOpponent, teams = teams, opponents = opponents, selectedTeam = selectedTeam)



if __name__ == '__main__':
    app.run(debug=True, port = 5001)