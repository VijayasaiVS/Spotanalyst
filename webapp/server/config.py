import os
import random
import string

PLOTLY_CREDS = {
    "PLOT_USERNAME" : "",
    "PLOT_API_KEY" : ""
}

def file_server_path_setup():
    file_server_path = os.path.join(os.getcwd(),"fileserver")
    if os.path.exists(file_server_path):
        return file_server_path
    else:
        os.makedirs(file_server_path)
        return file_server_path

def current_play_server_path():
    image_server_path = os.path.join(os.getcwd(),"image")
    if os.path.exists(image_server_path):
        return image_server_path
    else:
        os.makedirs(image_server_path)
        return image_server_path

def get_model_dir():
    parent_dir = os.path.abspath(os.pardir)
    print(parent_dir)
    modeloc = os.path.join(parent_dir,"..","prediction","model","song_emotion_predict.pkl")
    if os.path.exists(modeloc):
        modeloc = modeloc.split(".pkl")[0]
        return modeloc
    else:
        print("ML model not found in default loc")
        print("Searching for ML Model in alternate location")
        modeloc = os.path.join(parent_dir,"..","model","song_emotion_predict.pkl")
        print(modeloc)
        if os.path.exists(modeloc):
            print("Found ML model at alternate location")
            modeloc = modeloc.split(".pkl")[0]
            return modeloc
        else:
            print("Model not found! Please generate the ML model")
            return 0

def generate_random_secret_key():
    strings = string.ascii_letters + string.digits + string.punctuation
    random_strings = ''.join(random.choice(strings) for i in range(32))
    return random_strings

FILESERVER_LOC = file_server_path_setup()
SESSION_TYPE = "memcached"
SECRET_KEY = generate_random_secret_key()
HOSTNAME = "localhost"
PORT = 9090
SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
SPOTIFY_REDIRECT_URL = "http://localhost:9090/account"
SPOTIFY_SCOPES = "user-read-currently-playing user-library-read user-top-read user-read-playback-position"
IMAGE_LOC = current_play_server_path()
MODELLOC = get_model_dir()