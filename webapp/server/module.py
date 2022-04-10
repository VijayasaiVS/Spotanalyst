import os
import spotipy
from spotipy import SpotifyOAuth
# from dotenv import load_dotenv
import pandas as pd
from pycaret.classification import *
from colorthief import ColorThief
import urllib.request
from config import *
import sys

#Importing Secure Keys using ENV (dotenv) Module
# load_dotenv()
imgloc= os.path.join(IMAGE_LOC,"current_song_cover.jpg")
modelloc = MODELLOC
if modelloc == 0:
    sys.exit(1)
#User Credentials
client_id = SPOTIFY_CLIENT_ID
client_secret = SPOTIFY_CLIENT_SECRET
redirect_uri = SPOTIFY_REDIRECT_URL
#Spotify Token Authentication
scope = SPOTIFY_SCOPES
    
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
    current_artist=current_song["item"]["album"]["artists"][0]["name"]
    current_song_id= current_song['item']['uri']
    current_song_cover=current_song["item"]["album"]["images"][0]["url"]
    return current_playing,current_artist,current_song_id,current_song_cover
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
                                            energy=f['energy'],
                                            speechiness=f['speechiness'],
                                            instrumentalness = f['instrumentalness'],
                                            valence = f['valence']
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
    spotanalyst=load_model(modelloc)
    print(df)
    predicted_df=predict_model(spotanalyst,data=df)
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

def imagecolor(imgurl):
    urllib.request.urlretrieve(imgurl,imgloc)
    color_thief = ColorThief(imgloc)
    # get the dominant color
    dominant_color = color_thief.get_color(quality=1)
    print(dominant_color)
    hexcode = '#%02x%02x%02x' % dominant_color
    print(hexcode)
    return hexcode