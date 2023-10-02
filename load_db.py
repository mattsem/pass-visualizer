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
        print(data[0]['team_name'] + ' ' + data[1]['team_name'] + ' ' + game_id)
        conn.commit()
conn.close()