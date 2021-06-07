from flask import *
from dotenv import load_dotenv
import os
import time
from numpy.lib.function_base import extract
import module as md
import spotipy
import pandas as pd
import shutil
from werkzeug.utils import secure_filename
import json
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls
import plotly.express as px
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
load_dotenv()


username=os.getenv('PLOT_USERNAME')
plot_api=os.getenv('PLOT_API')
chart_studio.tools.set_credentials_file(username=username,api_key=plot_api)
fileloc=os.getenv('FILESERVER')

app=Flask(__name__,static_folder='../frontend',template_folder='../frontend/views')

app.config['SESSION_TYPE']=os.getenv('SESSION_TYPE')    
app.config.update(
    SECRET_KEY=''+os.getenv('SECRET_KEY')
)


@app.route('/')
def home():
    return render_template('index.html')
    # return app.config['SECRET_KEY']

@app.route('/verify')
def login():
    redirect_link=(md.login()).get_authorize_url()
    return redirect(redirect_link)
    

@app.route('/account')
def manage_token():
    soauth=md.login()
    session.clear()
    code = request.args.get('code')
    token_info = soauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("spotanalyst")

# sp=spotipy.Spotify(auth=session.get('token_info').get('access_token'))


@app.route('/spotanalyst')
def welcome():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/verify')
    # data = request.form
    sp=spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if not md.get_current_song(sp):
        return render_template('spotanalyst.html')
    else:
        current_playing,current_song_id,current_song_cover=md.get_current_song(sp)
        display_name,username,dp,profile_url,followers=md.get_userdetails(sp)
        session['username']=username
        # return current_song
        render_content={
                        'display_name':display_name,
                        'username':username,
                        'dp':dp,
                        'profile_url':profile_url,
                        'followers':followers,
                        'current_playing':current_playing,
                        'current_id':current_song_id,
                        'current_song_cover':current_song_cover
                        }
        return render_template('spotanalyst.html',**render_content)
    
@app.route('/analysis/playlist')
def analysis_playlist():
    sp=spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    username=session.get('username')
    df=md.get_playlist_data(sp,username)
    # return render_template('analysis.html',extract='Successfully Extracted')
    predicted_df=md.predict_data(df)
    predicted_df.to_csv(os.path.join(fileloc,'predicted_data.csv'),index=False)
    no_of_songs=len(predicted_df['name'])
    session['predicted_playlist_data']=predicted_df.to_json()
    plot_df = pd.DataFrame(predicted_df["Label"].value_counts().reset_index().values, columns=["Label", "No. of Songs"])

    plot1=px.pie(plot_df,values=plot_df['No. of Songs'],names=plot_df['Label'],title=('Distribution of Playlist according to Emotion\nTotal Songs: {0}'.format(no_of_songs)))
    plot1=py.plot(plot1,filename='Songs in each emotions',auto_open=False)
    fig1=tls.get_embed(plot1)

    plot2=px.bar(predicted_df,x=predicted_df['name'],y=predicted_df['Score'],
                color=predicted_df['Label'],title='Category of Songs with Prediction of Score')
    plot2=py.plot(plot2,filename='Category of Songs with Prediction Score',auto_open=False)
    fig2=tls.get_embed(plot2)
    features=[predicted_df['acousticness'],predicted_df['danceability'],
                predicted_df['liveness'],predicted_df['loudness'],predicted_df['speechiness']]
    plot3=px.bar(predicted_df,x=predicted_df['name'],
                y=features,title='All Songs with its Features')
    plot3=py.plot(plot3,filename='All Songs with its Features',auto_open=False)
    fig3=tls.get_embed(plot3)
    return render_template('analysis.html',extract='Success',plot1=fig1,plot2=fig2,plot3=fig3)
    # plot3=fig3,plot4=fig4,plot5=fig5,plot6=fig6

@app.route('/analysis/library')
def analysis_library():
    sp=spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    username=session.get('username')
    df=md.get_library_data(sp)
    # return render_template('analysis.html',extract='Successfully Extracted')
    predicted_df=md.predict_data(df)
    predicted_df.to_csv(os.path.join(fileloc,'predicted_data.csv'),index=False)
    no_of_songs=len(predicted_df['name'])
    session['predicted_library_data']=predicted_df.to_json()
    plot_df = pd.DataFrame(predicted_df["Label"].value_counts().reset_index().values, columns=["Label", "No. of Songs"])

    plot1=px.pie(plot_df,values=plot_df['No. of Songs'],names=plot_df['Label'],
                title=('Distribution of Playlist according to Emotion\nTotal Songs: {0}'.format(no_of_songs)))
    plot1=py.plot(plot1,filename='Songs in each emotions',auto_open=False)
    fig1=tls.get_embed(plot1)

    plot2=px.bar(predicted_df,x=predicted_df['name'],y=predicted_df['Score'],
                color=predicted_df['Label'],title='Category of Songs with Prediction of Score')
    plot2=py.plot(plot2,filename='Category of Songs with Prediction Score',auto_open=False)
    fig2=tls.get_embed(plot2)
    features=[predicted_df['acousticness'],predicted_df['danceability'],
                predicted_df['liveness'],predicted_df['loudness'],predicted_df['speechiness']]
    plot3=px.bar(predicted_df,x=predicted_df['name'],
                y=features,title='All Songs with its Features')
    plot3=py.plot(plot3,filename='All Songs with its Features',auto_open=False)
    fig3=tls.get_embed(plot3)
    return render_template('analysis.html',extract='Success',plot1=fig1,plot2=fig2,plot3=fig3)
    # plot3=fig3,plot4=fig4,plot5=fig5,plot6=fig6

@app.route("/download/csv")
def download():
    return send_from_directory(directory=fileloc, filename='predicted_data.csv',as_attachment=True)


# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = md.login()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == '__main__':
    app.run(host=os.getenv('HOSTNAME'),port=os.getenv('PORT'),debug=True)