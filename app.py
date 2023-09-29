from flask import Flask, send_file, render_template, request

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen

import os
import io
import base64



app = Flask(__name__)


path = './statsbomb/open-data-master/data/events'
filenames=os.listdir(path)
games=[x.split('.')[0] for x in filenames]
#print(games)



def game_list():
    return games

def game_names():
    names = []
    with open('team_names.txt', 'r') as f:
        names = f.read().splitlines()
    return names

@app.route('/')
def plot():
    
    team = request.args.get('team')
    if team is not None:
        game_id = team
    else:
        game_id = 7298

    
    gameList = game_list()
    gameNames = game_names()

    games_and_names = list(zip(gameList,gameNames))

    print("start")
    parser = Sbopen()
    df, related, freeze, tactics = parser.event(game_id)

    #prepare the dataframe of passes that were not throw ins
    mask = (df.type_name == 'Pass') & (df.team_name == df.team_name[0]) & (df.sub_type_name != "Throw-in")
    df_passes = df.loc[mask, ['x', 'y', 'end_x', 'end_y', 'player_name','position_name','outcome_id']]
    #get the list of all players who made a pass
    names = df_passes['player_name'].unique()
    
    #draw 4x4 pitches
    pitch = Pitch(line_color='black', pad_top=20)
    fig, axs = pitch.grid(ncols = 4, nrows = 4, grid_height=0.85, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0.04, endnote_space=0.01)

    #for each player
    for name, position, ax in zip(names, df_passes['position_name'], axs['pitch'].flat[:len(names)]):
    #put player name over the plot
        ax.text(60, -10, f'{name} ({position})', ha='center', va='center', fontsize=8)
    #take only passes by this player
        player_df = df_passes.loc[df_passes["player_name"] == name]
    #scatter
        pitch.scatter(player_df.x, player_df.y, alpha = 0.2, s = 50, color = "blue", ax=ax)
    #set colors based on completion
        colors = np.where(player_df['outcome_id'] == 9, 'red', 'blue')
    #plot arrows
        pitch.arrows(player_df.x, player_df.y, player_df.end_x, player_df.end_y, color = colors, ax=ax, width=1)

    #remove extra pitches
    for ax in axs['pitch'][-1, 16 - len(names):]:
        ax.remove()

    #set title
    axs['title'].text(0.5, 0.5, df.team_name[0] + ' vs ' + df.team_name[1], ha='center', va='center', fontsize=30)
    #plt.show()

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)

    plot_url = base64.b64encode(img_stream.getvalue()).decode('utf8')
    plt.clf()
    plt.close()
    
    return render_template('index.html', plot_url = plot_url, games_and_names = games_and_names)



if __name__ == '__main__':
    app.run(debug=True, port = 5000)