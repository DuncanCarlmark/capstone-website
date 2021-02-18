import os
import requests

# Paths for storing data
DATA_DIR = 'data'
# Data subdirectories
DATA_DIR_RAW = os.path.join(DATA_DIR, 'raw')
DATA_DIR_CLEAN = os.path.join(DATA_DIR, 'clean')
DATA_DIR_RECOMMENDATIONS = os.path.join(DATA_DIR, 'recommendations')

# last.fm files 
USER_PROFILE_PATH_RAW = os.path.join(DATA_DIR_RAW, 'user_profile.csv')
USER_ARTIST_PATH_RAW = os.path.join(DATA_DIR_RAW, 'user_artist.csv')

# billboard files
BILLBOARD_SONGS_PATH_RAW = os.path.join(DATA_DIR_RAW, 'billboard_songs.csv')
BILLBOARD_FEATURES_PATH_RAW = os.path.join(DATA_DIR_RAW, 'billboard_features.csv')

# last.fm files
USER_PROFILE_PATH_CLEAN = os.path.join(DATA_DIR_CLEAN, 'user_profile.csv')
USER_ARTIST_PATH_CLEAN = os.path.join(DATA_DIR_CLEAN, 'user_artist.csv')

# billboard files
BILLBOARD_SONGS_PATH_CLEAN = os.path.join(DATA_DIR_CLEAN, 'billboard_songs.csv')
BILLBOARD_FEATURES_PATH_CLEAN = os.path.join(DATA_DIR_CLEAN, 'billboard_features.csv')



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
r = requests.get('https://capstone-clean-data.s3-us-west-2.amazonaws.com/user_profile.csv')
open(USER_PROFILE_PATH_CLEAN, 'wb').write(r.content)
print("LAST.FM 1")

r = requests.get('https://capstone-clean-data.s3-us-west-2.amazonaws.com/user_artist.csv')
open(USER_ARTIST_PATH_CLEAN, 'wb').write(r.content)
print("LAST.FM 2")

# Billboard files
r = requests.get('https://capstone-clean-data.s3-us-west-2.amazonaws.com/billboard_songs.csv')
open(BILLBOARD_SONGS_PATH_CLEAN, 'wb').write(r.content)
print("BILLBOARD 1")

r = requests.get('https://capstone-clean-data.s3-us-west-2.amazonaws.com/billboard_features.csv')
open(BILLBOARD_FEATURES_PATH_CLEAN, 'wb').write(r.content)
print("BILLBOARD 2")