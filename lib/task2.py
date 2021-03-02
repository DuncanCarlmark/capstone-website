import sys
import json
import os
import pandas as pd
import requests
import spotipy
from collections import defaultdict
import scipy.sparse as sparse
import numpy as np
import random
import implicit
from sklearn.preprocessing import MinMaxScaler
import ipywidgets
from ipywidgets import FloatProgress
from lib.task2_utils import *

class userParent:
    
    def __init__(self, profile, history, age, age_range, selection):
        
        self.parent_age = age
        self.genre_selection = selection
        self.age_range = age_range
        self.users = extract_users(profile, age, age_range)
        self.usersHistory = extract_histories(history, self.users)

        
    def fit(self, sp):
              
        # Building Implicit Model
        
        self.sp = sp
        
        print("PREPARING USER HISTORY GIVEN AGE")
        grouped_df = prepare_dataset(self.usersHistory)
        print("RESULTING DATAFRAME SHAPE:")
        print(grouped_df.shape)

        print("GETTING USER PLAYLISTS")
        playlist_df, current_user = pull_user_playlist_info(self.sp, grouped_df)
        print("RESULTING DATAFRAME SHAPE:")
        print(playlist_df.shape)

        print("COMBINING USER HISTORY WITH LAST.FM HISTORY")
        updated_df = updated_df_with_user(grouped_df, playlist_df)
        print("RESULTING DATAFRAME SHAPE:")
        print(updated_df.shape)

        print("FITTING ALS MODEL")
        alpha = 15
        # Create recommendations for current user
        user_id = current_user
        sparse_user_artist, user_vecs, artist_vecs = build_implicit_model(updated_df, alpha)
        
        
        self.current_user = user_id
        self.user_item_interactions = sparse_user_artist
        self.user_vecs = user_vecs
        self.artist_vecs = artist_vecs
        self.data = updated_df
        
        
    def predict(self, N):
        
        print("GENERATING RECOMMMENDATIONS LIST")
        artist_recommendations = recommend(self.sp, self.current_user, self.user_item_interactions, self.user_vecs, self.artist_vecs, self.data)
        
        print("NUMBER OF RECOMMENDED ARTISTS:")
        print(artist_recommendations.shape)
        
        print("SELECTING TOP " +str(N)+ " RECOMMENDATIONS")
        recommended_tracks = get_top_recommended_tracks(self.sp, artist_recommendations, self.genre_selection, N)
        print(recommended_tracks.shape)
            
        return recommended_tracks
         
        
        
    
    