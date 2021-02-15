import pandas as pd
import numpy as np
import os
import requests
from sklearn import svm
#from billboard import *

class task1_cf:
    def __init__(self, length, features, test_rec, seed_tracks):
        
        self.f = features
        self.length = length
        
        # liked songs
        self.seed = f.loc[f['spotify_track_id'].isin(seed_tracks)]
        # negative training set; fix to get songs in the same timeframe
        self.random = f.loc[~f['spotify_track_id'].isin(seed_tracks) & ~f[f.columns[10:-1]].isnull()].sample(len(seed))
        
        # test set; fix to get songs in the same timeframe
        self.test = f.loc[f['spotify_track_id'].isin(test_rec)]
        
        self.clf = svm.SVC()

    def train_svm(self):
        # train svm
        X = np.concatenate((seed[seed.columns[10:-1]].values, random[random.columns[10:-1]].values))
        y = [1 for i in range(length)] + [0 for i in range(length)]
        
        clf.fit(X, y)

    def getList(self):
        
        self.train_svm()
        
        new_tracks = []
        for index, row in test.iterrows():
            test_features = row[10:-1].values
            if (~pd.isnull(test_features).any()):
                if clf.predict([test_features]) == 1:
                    new_tracks.append(row['spotify_track_id'])
        
        return new_tracks[:length]
    