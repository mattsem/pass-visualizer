from mplsoccer import Sbopen
import os
import json

path = './statsbomb/open-data-master/data/events'
filenames=os.listdir(path)




with open('team_names.txt','w') as f:
    for file in filenames:
        with open('./statsbomb/open-data-master/data/lineups/' + file, 'r') as x:
            data = json.load(x)
        f.write(data[0]['team_name'] + ' vs ' + data[1]['team_name'] + '\n')
        print(data[0]['team_name'] + ' vs ' + data[1]['team_name'])
        

