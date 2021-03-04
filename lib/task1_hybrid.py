import pandas as pd
import numpy as np
from random import sample

from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import auc_score


# get and build data from parent(=seed)
seed_tracks = set()
seed_artists = []

for track in sp.current_user_top_tracks(limit=50, time_range='medium_term')['items']:
    seed_tracks.add(track['id'])
    for artist in track['artists']:
        seed_artists.append(artist['name'].lower())

counts = dict()
for i in seed_artists:
    counts[i] = counts.get(i, 0) + 1

seed_artists = list(set(seed_artists))

seed_interactions = []
for k,v in counts.items():
    seed_interactions.append((username, k, v))

# get and build data from lastfm
profiles = pd.read_csv('https://capstone-clean-data.s3-us-west-2.amazonaws.com/user_profile.csv')[['user_id', 'age']]
history = pd.read_csv('https://capstone-clean-data.s3-us-west-2.amazonaws.com/user_artist.csv')

INPUT_AGE = 20
age_offset = 2
f_profiles = profiles[(profiles['age'] > INPUT_AGE - age_offset) & (profiles['age'] < INPUT_AGE + age_offset)].reset_index(drop=True)
f_history = history[history['user_id'].isin(f_profiles['user_id'])].reset_index(drop=True)

lastfm_users = f_history.user_id.unique().tolist()
lastfm_artists = f_history.artist_name.unique().tolist()

lastfm_interactions = []
for index, row in f_history.iterrows():
    lastfm_interactions.append((row.user_id, row.artist_name, row.plays))

    
# build lightfm dataset
all_users = [username]+lastfm_users
all_artists = seed_artists+lastfm_artists

LightFM_data = Dataset()
LightFM_data.fit(users=all_users, items=all_artists)
user_id_map, user_feature_map, item_id_map, item_feature_map = lfm_data.mapping()

all_interactions = seed_interactions+lastfm_interactions
interactions_built, weights_built = LightFM_data.build_interactions(all_interactions)
n_users, n_items = interactions_built.shape # no of users * no of items


# build lightfm recommender model
model = LightFM(loss='warp')
model.fit(interactions=interactions_built, sample_weight=weights_built, epochs=30, num_threads=2)

# evaluation
# train_auc = auc_score(model, interactions_built).mean()
# print('Hybrid training set AUC: %s' % train_auc)

# rank artists for parent
test_int, test_weight = LightFM_data.build_interactions([(username, x) for x in lastfm_artists])
ranked_artists = model.predict_rank(test_interactions = test_int, num_threads=2) 
ranked = ranked_artists.toarray()[0].tolist() # parent's id is mapped as 0; can use user_id_map.get(username)

# get top 10 recommended artists for parent 
artist_length = 10
rec_artists = []
for pos in range(1, artist_length+1):
    artist_id = ranked.index(pos)
    artist_name = list(item_id_map.keys())[list(item_id_map.values()).index(artist_id)]
    rec_artists.append(artist_name)

def get_artist_id(artist_name):
    return sp.search(artist_name, type='artist')['artists']['items'][0]['id']

# get top 10 songs for each recommended artist (total = 100 songs)
new_songs = []
for artist in rec_artists:
    for track in sp.artist_top_tracks(get_artist_id(artist))['tracks']:
        new_songs.append(track['id'])
new_songs = list(set(new_songs)-set(seed_tracks))

# get audio features for songs
audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
                  'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

def convert_to_audio_df(song_list):
    dfrow = []
    for song in sp.audio_features(song_list):
        row = [song['id']]
        for feature in audio_features:
            row.append(song[feature])
        dfrow.append(pd.DataFrame([row]))
    df = pd.concat(dfrow).reset_index(drop=True)
    return df

new_df = convert_to_audio_df(new_songs)
seed_df = convert_to_audio_df(seed_tracks)
seed_preference = seed_df.mean()


# rank songs by euclidean distance
distances = []
for index, row in new_df.iterrows():
    euc = 0
    for i in range(1,12):
        euc += (row[i]-seed_preference[i])**2
    distances.append(round(np.sqrt(euc),1))
new_df['distance'] = distances


#return songs with closest distance to mean
playlist_length = 30
recommendations = new_df.sort_values(by='distance')[0][:playlist_length].to_list()

recommendations