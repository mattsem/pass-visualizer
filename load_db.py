import sqlite3
from mplsoccer import Sbopen
import os
import json



path = './statsbomb/open-data-master/data/events'
filenames=os.listdir(path)

conn = sqlite3.connect("games.db")

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS game(home, away, file_num)")


for file in filenames:
    with open('./statsbomb/open-data-master/data/lineups/' + file, 'r') as x:
        data = json.load(x)
        #insert to table here    
        game_id = file.split('.')[0]
        team_1 = data[0]['team_name']
        team_2 = data[1]['team_name']
        cur.execute("INSERT INTO game(home,away,file_num) VALUES(?,?,?)", (team_1, team_2, game_id))
        print(team_1 + ' ' + team_2 + ' ' + game_id)
        conn.commit()

cur.execute('''CREATE TABLE IF NOT EXISTS passes(
        file_num TEXT,
        x FLOAT,
        y FLOAT,
        end_x FLOAT,
        end_y FLOAT,
        player_name TEXT,
        position_name TEXT,
        outcome_id INTEGER,
        team_name TEXT)
            ''')

parser = Sbopen()
x=0
for file in filenames:
    filename = file.split('.')[0]
    df, related, freeze, tactics = parser.event(filename)
    mask = (df.type_name == 'Pass') & (df.sub_type_name != "Throw-in")
    df_passes = df.loc[mask, ['x', 'y', 'end_x', 'end_y', 'player_name','position_name','outcome_id', 'team_name']]
    df_passes['file_num'] = filename
    df_passes.to_sql('passes', conn, if_exists='append', index=False)

    print(x)
    x=x+1
    conn.commit()


conn.close()