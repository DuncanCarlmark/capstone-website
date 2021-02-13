import os
import requests

# Directory Paths
DATA_DIR = 'data'
DATA_DIR_RAW = os.path.join(DATA_DIR, 'raw')
DATA_DIR_CLEAN = os.path.join(DATA_DIR, 'clean')
DATA_DIR_RECOMMENDATIONS = os.path.join(DATA_DIR, 'recommendations')

USER_PROFILE = os.path.join(DATA_DIR_RAW, 'user_profile.csv')
USER_ARTIST = os.path.join(DATA_DIR_RAW, 'user_artist.csv')

BILLBOARD_SONGS = os.path.join(DATA_DIR_RAW, 'billboard_songs.csv')
BILLBOARD_FEATURES = os.path.join(DATA_DIR_RAW, 'billboard_features.csv')


# Make data directory and subfolders for billboard and last.fm
print("------------------------- DOWNLOADING RAW TRAINING DATA -------------------------")

# Make necessary directories if they do not already exist
print("CREATING DATA DIRECTORIES")
os.mkdir(DATA_DIR)
os.mkdir(DATA_DIR_RAW)
os.mkdir(DATA_DIR_CLEAN)
os.mkdir(DATA_DIR_RECOMMENDATIONS)
print('Data directory files created')

# LAST.FM files
r = requests.get('https://capstone-raw-data.s3-us-west-2.amazonaws.com/user_profile.csv')
open(USER_PROFILE, 'wb').write(r.content)
print("LAST.FM 1")

r = requests.get('https://capstone-raw-data.s3-us-west-2.amazonaws.com/user_artist.csv')
open(USER_ARTIST, 'wb').write(r.content)
print("LAST.FM 2")

# Billboard files
r = requests.get('https://capstone-raw-data.s3-us-west-2.amazonaws.com/billboard_songs.csv')
open(BILLBOARD_SONGS, 'wb').write(r.content)
print("BILLBOARD 1")

r = requests.get('https://capstone-raw-data.s3-us-west-2.amazonaws.com/billboard_features.csv')
open(BILLBOARD_FEATURES, 'wb').write(r.content)
print("BILLBOARD 2")