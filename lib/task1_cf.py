import pandas as pd
import numpy as np
import os
import requests
from sklearn import svm
#from billboard import *

class task1_cf:
    def __init__(self, length, features, seed_tracks):
        
        self.length = length
        self.f = features
        self.seed_tracks = seed_tracks

    def train_svm(self):
        
        # liked songs
        seed = f.loc[f['spotify_track_id'].isin(seed_tracks)]
        # negative training set; fix to get songs in the same timeframe
        random = f.loc[~f['spotify_track_id'].isin(seed_tracks) & ~f[f.columns[10:-1]].isnull()].sample(len(seed))
        
        # train svm
        clf = svm.SVC()
        X = np.concatenate((seed[seed.columns[10:-1]].values, random[random.columns[10:-1]].values))
        y = [1 for i in range(length)] + [0 for i in range(length)]
        clf.fit(X, y)
        return clf

    def getList(self, test_rec):
        
        clf_ = self.train_svm()
        
        # test set; test_rec gets songs in the same timeframe
        test = f.loc[f['spotify_track_id'].isin(test_rec)]
        
        new_tracks = []
        for index, row in test.iterrows():
            test_features = row[10:-1].values
            if (~pd.isnull(test_features).any()):
                if clf_.predict([test_features]) == 1:
                    new_tracks.append(row['spotify_track_id'])
        
        return new_tracks[:length]
    