import pandas as pd
import numpy as np
#from random import sample

from lightfm import LightFM
from lightfm.data import Dataset
#from lightfm.evaluation import auc_score


class parentUser:
    
    def __init__(username, top_tracks, user_profile, user_artist, input_age, age_offset):

        # get and build data from parent(=seed)
        seed_tracks = set()
        seed_artists = []

        for track in top_tracks:
            seed_tracks.add(track['id'])
            for artist in track['artists']:
                seed_artists.append(artist['name'].lower())

        counts = dict()
        for i in seed_artists:
            counts[i] = counts.get(i, 0) + 1

        seed_interactions = []
        for k,v in counts.items():
            seed_interactions.append((username, k, v))
        
        # get and build data from lastfm (filter by age)
        lower_age = input_age - age_offset
        upper_age = input_age + age_offset
        
        f_profiles = user_profile[(user_profile['age'] > lower_age) & (user_profile['age'] < upper_age)].reset_index(drop=True)
        f_history = user_artist[user_artist['user_id'].isin(f_profiles['user_id'])].reset_index(drop=True)

        lastfm_interactions = []
        for index, row in f_history.iterrows():
            lastfm_interactions.append((row.user_id, row.artist_name, row.plays))
        
        # init
        self.username = username
        self.seed_tracks = seed_tracks
        self.seed_artists = list(set(seed_artists))
        self.seed_interactions = seed_interactions
            
        self.lastfm_users = f_history.user_id.unique().tolist()
        self.lastfm_artists = f_history.artist_name.unique().tolist()
        self.lastfm_interactions = lastfm_interactions
        
    def fit(loss='warp'):
        # build lightfm dataset
        all_users = [self.username]+self.lastfm_users
        all_artists = self.seed_artists+self.lastfm_artists

        LightFM_data = Dataset()
        LightFM_data.fit(users=all_users, items=all_artists)
        user_id_map, user_feature_map, item_id_map, item_feature_map = LightFM_data.mapping()
        
        self.item_id_map = item_id_map
        self.lfm_data = LightFM_data

        # build lightfm recommender model
        all_interactions = self.seed_interactions+self.lastfm_interactions
        
        interactions_built, weights_built = lfm_data.build_interactions(all_interactions)
        n_users, n_items = interactions_built.shape # no of users * no of items
        
        model = LightFM(loss=loss)
        model.fit(interactions=interactions_built, sample_weight=weights_built, epochs=30, num_threads=2)
        self.lfm_model = model
    
    
    def predict_artists(artist_length=10):
        # rank artists for parent
        test_int, test_weight = self.lfm_data.build_interactions([(self.username, x) for x in self.lastfm_artists])
        
        ranked_artists = self.lfm_model.predict_rank(test_interactions = test_int, num_threads=2)
        ranked = ranked_artists.toarray()[0].tolist() # parent's id is mapped as 0; can use user_id_map.get(username)

        # get top (10) recommended artists for parent 
        rec_artists = []
        for pos in range(1, artist_length+1):
            artist_id = ranked.index(pos)
            artist_name = list(item_id_map.keys())[list(item_id_map.values()).index(artist_id)]
            rec_artists.append(artist_name)
        
        return rec_artists

#     def evaluate():
#         # train_auc = auc_score(model, interactions_built).mean()
#         # print('Hybrid training set AUC: %s' % train_auc)
    
    def predict_songs(top_artists, playlist_length, sp):
        
                # get audio features for songs
        def get_audio_df(song_features):
            audio_feature_list = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
                          'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
            dfrow = []
            for song in song_features:
                row = [song['id']]
                for feature in audio_feature_list:
                    row.append(song[feature])
                dfrow.append(pd.DataFrame([row]))
            df = pd.concat(dfrow).reset_index(drop=True)
            return df

        # get euclidean distance for features
        def euclidean(row_a, row_b, n=range(1,12):
            euc = 0
            for i in n:
                euc += (row_a[i]-row_b[i])**2
            return round(np.sqrt(euc),1)
                      
        # get top 10 songs for each recommended artist (total = 100 songs)
        new_songs = []
        for artist_id in top_artists:
            for track in sp.artist_top_tracks(artist_id)['tracks']:
                new_songs.append(track['id'])
        new_songs = list(set(new_songs)-set(seed_tracks))
        
        new_sf = sp.audio_features(new_songs)
        seed_sf = sp.audio_features(seed_tracks)
        
        new_df = get_audio_df(new_sf)
        seed_df = get_audio_df(seed_sf)
        seed_preference = seed_df.mean()
        
        # rank songs by euclidean distance
        distances = []
        for index, row in new_df.iterrows():
            distances.append(euclidean(row, seed_preference))
        new_df['distance'] = distances

        # return songs with closest distance to mean
        recommendations = new_df.sort_values(by='distance')[0][:playlist_length].to_list()
        
        return recommendations