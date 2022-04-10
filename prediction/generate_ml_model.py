from matplotlib.cbook import silent_list
import pandas as pd
from pycaret.classification import setup as classi_setup
from pycaret.classification import create_model as classi_create_model
from pycaret.classification import finalize_model as classi_finalize
from pycaret.classification import save_model as classi_save_model
from pycaret.classification import tune_model as classi_tune_model
from pycaret.clustering import setup as cluster_setup
from pycaret.clustering import create_model as cluster_create_model
from pycaret.clustering import assign_model as cluster_assign
import numpy as np
import os
import zipfile
import time
from sklearn import cluster
import sys
from sklearn.preprocessing import MinMaxScaler
from pycaret.classification import *
from config import KAGGLE_CREDS

def get_kaggle_dataset(data_folder):
    print("Getting dataset from Kaggle...")
    if os.path.exists(os.path.join(data_folder,"tracks_features.csv")):
        print("Dataset already present!")
        return True
    else:
        print("No data found already, Getting dataset from Kaggle")
        os.environ['KAGGLE_USERNAME'] = KAGGLE_CREDS["KAGGLE_USERNAME"]
        os.environ['KAGGLE_KEY'] = KAGGLE_CREDS["KAGGLE_KEY"]
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        for _ in range(3):
            try:
                print("Downloading...")
                data_setup = api.dataset_download_file("rodolfofigueroa/spotify-12m-songs",file_name="tracks_features.csv",force=True)
                if data_setup:
                    with zipfile.ZipFile('tracks_features.csv.zip','r') as zips:
                        zips.extractall(data_folder)
                    os.remove('tracks_features.csv.zip')
                    if os.path.exists(os.path.join(data_folder,"tracks_features.csv")):
                        return True
                else:
                    print("Please check internet connection and try again")
                    raise Exception
            except Exception as ex:
                print(ex)
                print("Problem getting dataset, retrying in 30 seconds")
                time.sleep(30)
        return False
    
def get_min_max_details(features_list,df):
    print("Min:\n",df[features_list].min().reset_index())
    print("Max:\n",df[features_list].max().reset_index())
    print("Mean:\n",df[features_list].mean().reset_index())

def clean_data(df,fture_list):
    print("Records before cleaning: ",df.size)
    df.replace('',np.nan,inplace=True)
    df.dropna(how="any",axis=0,inplace=True)
    df = df.drop(df[fture_list].loc[(df[fture_list] == 0).all(axis=1)].index)
    df.drop_duplicates(inplace=True)
    print("Records after cleaning: ",df.size)
    return df

def scale_data(df,fture_list):
    print("Records before scaling")
    get_min_max_details(fture_list,df)
    minmaxscalar = MinMaxScaler()
    df[fture_list] = minmaxscalar.fit_transform(df[fture_list])
    print("Records after scaling")
    get_min_max_details(fture_list,df)
    return df

def kmeans_clustering(df):
    print("Setting up DF for Kmeans")
    feature_setup = cluster_setup(data=df,silent=True)
    print("Creating KMeans model...")
    kmeans=cluster_create_model(model='kmeans',num_clusters=4,round=4)
    # assign labels using trained model
    print("Assigning model to DF..")
    kmeans_df = cluster_assign(model=kmeans,transformation=True)
    print(kmeans_df.info())
    print(kmeans_df['Cluster'].value_counts())
    return kmeans_df

def classifiers_setup(df):
    print("Setting up for Classifiers")
    classify_setup=classi_setup(data=df,target="Label",silent=True)
    print("Creating model for lightgbm")
    lightgbm=classi_create_model(estimator='lightgbm',round=4)
    print("Finalizing model...")
    tuned_light=classi_tune_model(estimator=lightgbm,round=4,optimize='Accuracy')
    finalized_light=classi_finalize(estimator=tuned_light)
    model_folder = os.path.join(os.getcwd(),"model")
    if not os.path.exists(model_folder):
        os.makedirs(model_folder)
    print("Saving Lightgbm model")
    songanalysis_model=classi_save_model(finalized_light,os.path.join(model_folder,"song_emotion_predict"))


def main():

    data_folder = os.path.join(os.getcwd(),"data")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    bools = get_kaggle_dataset(data_folder)
    if bools == False:
        sys.exit(1)
    features_list = ['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness', 'valence', 'tempo']
    print("Reading CSV")
    spotify_track_data = pd.read_csv(os.path.join(data_folder,'tracks_features.csv'))
    spotify_track_data = clean_data(spotify_track_data,features_list)
    spotify_track_data = scale_data(spotify_track_data,features_list)
    spotify_track_data[features_list] = spotify_track_data[features_list].astype('float32')
    print("Removing Loudness & Tempo from Feature List")
    features_list_new = features_list
    features_list_new.remove("loudness")
    features_list_new.remove("tempo")
    print(features_list_new)
    songs_features = spotify_track_data[features_list_new]
    # songs_features.hist(column=None,bins=50,figsize=(20,15))
    clustered_df = kmeans_clustering(songs_features)
    print("Mean of features of songs from each Clusters")
    print("\nCluster 0:\n\n",clustered_df[clustered_df['Cluster']=='Cluster 0'].mean())
    print("\nCluster 1:\n\n",clustered_df[clustered_df['Cluster']=='Cluster 1'].mean())
    print("\nCluster 2:\n\n",clustered_df[clustered_df['Cluster']=='Cluster 2'].mean())
    print("\nCluster 3:\n\n",clustered_df[clustered_df['Cluster']=='Cluster 3'].mean())
    cluster_info = list(map(str(input("Please enter category of emotion for each Cluster separated by , (Comma)").split(','))))
    cluster_info = {f"Cluster {i}":cluster_info[i] for i in range(4)}
    clustered_df=clustered_df.replace({"Cluster":cluster_info})
    clustered_df.rename(columns={'Cluster':'Label'},inplace=True)
    print("Label Info\n",clustered_df['Label'].value_counts())
    faa_result=clustered_df.astype({'Label':'category'})
    faa_result[features_list_new] = faa_result[features_list_new].astype('float32')
    classifiers_setup(faa_result)


if __name__ == "__main__":
    main()
