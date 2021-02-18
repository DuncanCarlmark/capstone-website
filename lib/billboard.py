import pandas as pd
import numpy as np
import datetime
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

class billboard:
    def __init__(self):
        #features = pd.read_csv('Hot 100 Audio Features.csv')
        f = pd.read_csv(BILLBOARD_FEATURES)
        # only include tracks that have a spotify id on file for now
        f = f.dropna(subset=['spotify_track_id', 'spotify_genre']).drop_duplicates(subset='spotify_track_id')#[f.columns[0:5]]
        f['spotify_genre'] = [x.strip('[]').strip('\'').split('\', \'') for x in f['spotify_genre']]
        self.features = f

        #stuff = pd.read_csv('Hot Stuff.csv')
        stuff = pd.read_csv(BILLBOARD_SONGS)
        stuff['WeekID'] = pd.to_datetime(stuff['WeekID'])
        self.stuff = stuff

    def weeklyAvg(self):
        # average weekly position
        avg_pos = self.stuff[['WeekID', 'Week Position', 'SongID']].groupby(by=['SongID']).mean()
        # first week the track appeared in the chart
        minweek = self.stuff[['WeekID', 'SongID']].groupby(by=['SongID']).min().rename(columns={'WeekID':'firstWeekID'})
        # last week the track appeared in the chart
        maxweek = self.stuff[['WeekID', 'SongID']].groupby(by=['SongID']).max().rename(columns={'WeekID':'lastWeekID'})
        # total # of weeks the track was in the chart
        max_occ = self.stuff[['SongID','Instance','Weeks on Chart']].groupby(by=['SongID']).max()

        stats = avg_pos.join(minweek).join(maxweek).join(max_occ)
        self.data = self.features.join(stats, on='SongID').rename(columns={'Week Position':'Avg Weekly'})

    def getList(self, length=20, age=None, genre=[], artist=[]):
        
        startY = 2019
        endY = 2019
        offset_age = 15 # assume music preference starts setting in at 15 yrs old and stop at 30
        
        if age:
            startY = datetime.datetime.now().year - int(age) + start_age
            endY = min(startY + offset_age, 2019)
            
        # songs should have left chart after lower bound (e.g. 2019 songs should still be on chart after 2019/1/1)
        lowerBound = datetime.datetime(startY, 1, 1)
        # songs should have entered chart before upper bound (e.g. 2019 songs should have been on chart before 2019/12/31)
        upperBound = datetime.datetime(endY, 12, 31)

        #if how == '' #implement later for other possible ranking methods
        self.weeklyAvg()

        data = self.data
        filter_t = data[(data['firstWeekID'] < upperBound) & (data['lastWeekID'] > lowerBound)]
        
        filter_g = filter_t[filter_t.spotify_genre.apply(lambda x: bool(set(x) & set(genre)))]
        filter_a = filter_t[filter_t.Performer.apply(lambda x: bool(set(x) & set(artist)))]
        
        playlist = filter_g.append(filter_a)
        
#         if len(playlist) < length:
#             playlist = filter_t
        
        playlist.sort_values(['Instance','Avg Weekly','Weeks on Chart'], ascending=[True,True,False], inplace=True, ignore_index=True)

        return playlist['spotify_track_id'][:length].to_list()