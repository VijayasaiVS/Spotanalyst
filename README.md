# Spotanalyst

⚠ _**For other Detailed Information visit our Wiki Page: [Click Here](https://github.com/VijayasaiVS/spotanalyst/wiki)**_

## Initial Setup

### Installation:

1. Git clone: [Github Link](https://github.com/VijayasaiVS/spotanalyst.git)

2. In Terminal, 
              _pip install -r requirements.txt_ 
   to install the pre-requisites

### Setup ENV & Spotify Developer Account:

  *   **Setup Config.py file @ prediction/config.py:**

        1. Login with Kaggle Account [Click Here](https://www.kaggle.com)
        2. Once logged in, generate new API Key from Accounts Tab
        3. Save those details in required empty fields in _**prediction/config.py**_ file


   *   **Setup Config.py file @ webapp/server/config.py:**

        1. Login with Spotify Developer [Click Here](https://developer.spotify.com/dashboard/) 

        2. Create a new App on Spotify Developer Console
            * Create a New App [#1](https://imgur.com/a/JjOiss1)
            * Collect Spotify Client ID, Secret and also set Redirect URI in "Edit Settings" [#2](https://imgur.com/a/zwZobZj)

        3. Edit the file at _**webapp/server/config.py**_

        4. **Setup Chart Studio:**

             * Create a chart studio account [Click Here](https://plotly.com/chart-studio/)

             * Get the API Key from here [Click Here](https://chart-studio.plotly.com/settings/api)

        5. Edit the details on _**webapp/server/config.py**_ with respective data

***


## Create Prediction Model

1. Run _generate_ml_model.py_
2. Make sure a _.pkl_ file is made finally


***

## Front End

### Run App:

1. Setup correct location of training model and make sure every field is changed as per instructions.

2. Run _**app.py**_ to start the app

3. If everything goes well, your app will be posted at [http://localhost:9090](http://localhost:9090)
