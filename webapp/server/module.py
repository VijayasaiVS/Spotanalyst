import os
import spotipy
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
import json
import pandas as pd
from sklearn import preprocessing
import pandas as pd
import plotly.express as px
from pycaret.classification import *
#Importing Secure Keys using ENV (dotenv) Module
load_dotenv()

#User Credentials
client_id=os.getenv('SPOTIFY_CLIENT_ID')
client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri=os.getenv('REDIRECT_URI')
#Spotify Token Authentication
scope = os.getenv('SCOPES')
    
sp=spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret,
                                                redirect_uri=redirect_uri, scope=scope))

def login():
    soauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret,
                                            redirect_uri = redirect_uri, scope = scope)
    return soauth

def get_userdetails(sp):
    user_details=sp.current_user()
    display_name=user_details["display_name"]
    username=user_details["id"]
    dp=user_details["images"][0]["url"]
    profile_url=user_details["external_urls"]["spotify"]
    followers=user_details["followers"]["total"]
    # print(user_details["external_urls"]["spotify"])
    return display_name,username,dp,profile_url,followers

def get_current_song(sp):
    current_song=sp.current_user_playing_track()
    if current_song==None:
        return None
    current_playing=current_song['item']['name']
    current_song_id= current_song['item']['uri']
    current_song_cover=current_song["item"]["album"]["images"][0]["url"]
    return current_playing,current_song_id,current_song_cover
    # print(current_playing,current_song_id,current_song_cover)
    

def get_track_features(track_id,sp):
    if track_id is None:
        return None
    else:
        features = sp.audio_features([track_id])
    return features

def get_features_playlist(tracks,sp):
    print("Getting Features....")
    tracks_with_features=[]

    for track in tracks:
        features = get_track_features(track['id'],sp)
        print (track['name'])
        if not features:
            print("passing track %s" % track['name'])
            pass
        else:
            f = features[0]
            tracks_with_features.append(dict(
                                            name=track['name'],
                                            artist=track['artist'],
                                            id=track['id'],
                                            acousticness=f['acousticness'],
                                            danceability=f['danceability'],
                                            liveness=f['liveness'],
                                            loudness=f['loudness'],
                                            speechiness=f['speechiness']
                                            ))

        # time.sleep(0.1)
    print("Finished...")
    # print(tracks_with_features[0])
    return tracks_with_features

def get_tracks_from_playlists(username, sp):
    playlists = sp.user_playlists(username)
    trackList = []
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            # print (playlist['name'],' no. of tracks: ',playlist['tracks']['total'])
            results = sp.user_playlist(username, playlist['id'],fields="tracks,next")
            tracks = results['tracks']
            for i, item in enumerate(tracks['items']):
                track = item['track']
                trackList.append(dict(name=track['name'], id=track['id'], artist=track['artists'][0]['name']))

    # print(trackList[0])
    return trackList

def write_to_csv(track_features):
    df = pd.DataFrame(track_features)
    df.drop_duplicates(subset=['name','artist'])
    return df

def get_playlist_data(sp,username):
    tracks = get_tracks_from_playlists(username,sp)
    tracks_with_features = get_features_playlist(tracks,sp)
    tracks_csv=write_to_csv(tracks_with_features)
    return tracks_csv

def get_library_data(sp):
    tracks = get_library(sp)
    tracks_with_features = get_features_playlist(tracks,sp)
    tracks_csv=write_to_csv(tracks_with_features)
    return tracks_csv

def predict_data(df):
    data=df
    from sklearn import preprocessing
    loudness=data[['loudness']].values
    min_max_scaler=preprocessing.MinMaxScaler()
    loudness_scaled=min_max_scaler.fit_transform(loudness)
    data['loudness']=pd.DataFrame(loudness_scaled)
    spotanalyst=load_model('..\prediction\model\songanalysis_model')
    predicted_df=predict_model(spotanalyst,data=data)
    predicted_df.to_csv(r'predicted_playlist_data.csv',index=False)
    return predicted_df

def get_library(sp):
    print("Getting Library Tracks...")
    saved_tracks=[]
    hello=sp.current_user_saved_tracks()
    for j in range(0,hello["total"]+1):
        temp=sp.current_user_saved_tracks(limit=1,offset=j)
        for i in temp["items"]:
            # print(i)
            saved_tracks.append(dict(name=i["track"]["name"],id=i["track"]["id"],artist=i["track"]["artists"][0]["name"]))
    
    return saved_tracks