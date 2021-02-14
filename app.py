# Web and Server
from flask import Flask, request, render_template, url_for
import datetime
import spotipy
import os
import requests

# Custom Classes
from lib.billboard import *
from lib.cf_recommender import *


# Directory Paths
DATA_DIR = 'data'
DATA_DIR_RAW = os.path.join(DATA_DIR, 'raw')
DATA_DIR_CLEAN = os.path.join(DATA_DIR, 'clean')
DATA_DIR_RECOMMENDATIONS = os.path.join(DATA_DIR, 'recommendations')

USER_PROFILE = os.path.join(DATA_DIR_RAW, 'user_profile.csv')
USER_ARTIST = os.path.join(DATA_DIR_RAW, 'user_artist.csv')

BILLBOARD_SONGS = os.path.join(DATA_DIR_RAW, 'billboard_songs.csv')
BILLBOARD_FEATURES = os.path.join(DATA_DIR_RAW, 'billboard_features.csv')

# ------------------------------------------- DECLARE GLOBAL VARIABLES ---------------------------------------------------

testing = False

# Client Information
client_id = 'e6be6a0e60124f36ad99038de2f36e91'
client_secret = '14116a664bd84048a0c7c3004edc9726'
scope = " ".join(['playlist-modify-public',"user-top-read","user-read-recently-played","playlist-read-private"])
redirect_uri = None

# Algorithm Information
AGE_LOWER_BOUND = 15
AGE_UPPER_BOUND = 25
TASK1_LENGTH = 20


# Actual Redirect
if testing:
    redirect_uri = 'http://127.0.0.1:8080/form'
else:
    redirect_uri = 'http://35.161.20.39/form'

# User input
global_vars = {
    'access_code': None,
    'PARENT_AGE' : None,
    'PARENT_GENRE' : None,
    'PARENT_ARTIST' : None
}


# ------------------------------------------- CREATE APPLICATION ---------------------------------------------------

app = Flask('__name__')

@app.route('/')
def index():
    '''
    Creates the landing page for the site and also generates the Spotify authorization URL

    Returns:
        The flask template for the landing page of our site
    '''

    # Oauth object    
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)

    # Force auth every time
    auth_url = sp_oauth.get_authorize_url()

    return render_template('index.html', auth_url = auth_url)

@app.route('/form')
def form():
    '''
    ALSO serves as callback page from Spotify auth
    Generates the form page in which users input their age, genre, and artist information. Also
    retrieves the access_code from the Spotify authentication callback.

    Returns:
        The flask template for the form page
        Also sets the global_variable access code
    '''

    global_vars['access_code'] = request.args.get('code')
    
    return render_template('form.html', access_code = global_vars['access_code'])

@app.route('/form_success', methods=['POST'])
def form_success():
    '''
    Generates the success page for when the user completes their form. Also pulls the
    information from the form (age, genre, artist) and store them in global variables to
    be referenced later by recommendation logic.

    Returns:
        The Flask template for the form success page
    '''

    age = request.form.get('age')
    genre = request.form.get('genre')
    artist = request.form.get('artist')

    # Redirect to form if all fields are not present
    if not age or not genre or not artist:
        error_message = 'Hey! We said to fill out all the forms.'
        return render_template('form_failure.html',
                                age = age,
                                genre = genre,
                                artist = artist)

    # Set global variables based on correct input
    global_vars['PARENT_AGE'] = int(age)
    global_vars['PARENT_GENRE'] = genre
    global_vars['PARENT_ARTIST'] = artist

    return render_template('form_success.html')

@app.route('/gen_playlist')
def gen_playlist():
    '''
    Generates the success page for when a playlist is created and also handles the logic for
    when a playlist is created. This method completes both the task1 and task2 recommendations
    and then finally outputs them as a playlist on the user's account. 

    Returns:
        The flask template for the playlist success page. Technically also returns a playlist of
        song recommendations, but this playlist is generated directly on the user's Spotify account.
    '''

    # Re make auth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    # Get the actual access token
    token_info = sp_oauth.get_access_token(global_vars['access_code'])
    access_token = token_info['access_token']
    # Create Spotify Object and get userID
    sp = spotipy.Spotify(auth=access_token)
    
    # Remove any cached tokens
    if os.path.exists('.cache'):
        os.remove('.cache')


    user = sp.current_user()['id']
    print("Creating empty playlists for: " + str(user))

    #------------------------------------------------ GENERATING TASK 1 PLAYLIST ------------------------------------------------
    print("GENERATING PLAYLIST 1")
    # Create a blank playlist
    playlist_t1 = sp.user_playlist_create(user=user,
                            name='Task1: Playlist',
                            public = True,
                            collaborative = False,
                            description = 'This is a test')
    print("SUCCESS: Playlist created")


    print("Generating song recommendations")
    current_year = datetime.datetime.today().year
    start_year = current_year - abs(global_vars['PARENT_AGE'] - AGE_LOWER_BOUND)
    end_year = current_year - abs(global_vars['PARENT_AGE'] - AGE_UPPER_BOUND)

    # Create billboad recommender object, generate recommendations, add to playlist
    billboard_recommender = billboard()
    parent_to_user = billboard_recommender.getList(length = TASK1_LENGTH,
                                                genre=['rock'],
                                                startY = start_year, 
                                                endY = end_year)
    print("SUCCESS: Recommendations Generated")
    print("Playlist Time Range: " + str(start_year) + " - "  + str(end_year))
    print("Playlist Length: " + str(len(parent_to_user)))

    
    print("Populating playlist with reccomendation")
    sp.playlist_add_items(playlist_id=playlist_t1['id'], 
                            items=parent_to_user, 
                            position=None)
    print("SUCCESS: Playlist populated")

    #------------------------------------------------ GENERATING TASK 2 PLAYLIST ------------------------------------------------
    print("GENERATING PLAYLIST 2")
    # Create a blank playlist
    playlist_t2 = sp.user_playlist_create(user=user,
                            name='Task2: Playlist',
                            public = True,
                            collaborative = False,
                            description = 'This is a test')
    print("SUCCESS: Blank playlist created")

    print("Loading Last.fm dataset")
    lastfm_profile = pd.read_csv(USER_PROFILE)
    lastfm_usersong = pd.read_csv(USER_ARTIST)
        

    print("CLEANING USER DATA")
    # Cleaning user data and filtering out all non US users
    cleaned_users = lastfm_profile[['user_id', 'age', 'country']].dropna().reset_index(drop=True)
    cleaned_users_us = cleaned_users[cleaned_users['country'] == 'United States']
    cleaned_users = cleaned_users_us[cleaned_users_us['age'] > 0]
    # Choose users based on the user's specified age
    chosen_users = extract_users(cleaned_users, global_vars['PARENT_AGE'], 5)

    print("CLEANING HISTORY DATA")
    cleaned_history = lastfm_usersong[['user_id', 'artist_id', 'artist_name', 'plays']].dropna().reset_index(drop=True)
    # Filters down the cleaned history dataframe to only include users with propper profile values
    cleaned_history = extract_histories(cleaned_history, cleaned_users)
    # Filters down the dataframe again to only include users that were chosen based on age
    chosen_history = extract_histories(cleaned_history, chosen_users)
    ap = chosen_history


    print("CREATING NEW ARTIST FEATURES")
    # Create a DataFrame of artist statistics
    # For each artist finds: totalUniqueUsers, totalArtistPlays, avgUserPlays
    artist_rank = ap.groupby(['artist_name']) \
    .agg({'user_id' : 'count', 'plays' : 'sum'}) \
    .rename(columns={"user_id" : 'totalUniqueUsers', "plays" : "totalArtistPlays"}) \
    .sort_values(['totalArtistPlays'], ascending=False)
    artist_rank['avgUserPlays'] = artist_rank['totalArtistPlays'] / artist_rank['totalUniqueUsers']


    print("COMBINING NEW FEATURES WITH EXISTING DATA")
    # Joins new artist information with user-artist listening history
    ap = ap.join(artist_rank, on="artist_name", how="inner") \
    .sort_values(['plays'], ascending=False)


    print("MIN MAX SCALING ARTIST 'play' DATA")
    # Min max scales play count
    pc = ap.plays
    play_count_scaled = (pc - pc.min()) / (pc.max() - pc.min())
    ap = ap.assign(playCountScaled=play_count_scaled)


    print("ENSURING ALL DATASET ENTRIES ARE UNIQUE")
    # Drop duplicates just in case?
    ap = ap.drop_duplicates()
    # Everything is already a unique pairing, but in case groupby the identifying information
    grouped_df = ap.groupby(['user_id', 'artist_id', 'artist_name']).sum().reset_index()


    # Convert columns to category codes for implicit
    grouped_df['artist_name'] = grouped_df['artist_name'].astype("category")
    grouped_df['user_id'] = grouped_df['user_id'].astype("category")
    grouped_df['artist_id'] = grouped_df['artist_id'].astype("category")
    grouped_df['user_id'] = grouped_df['user_id'].cat.codes
    grouped_df['artist_id'] = grouped_df['artist_id'].cat.codes

    print("GETTING USER PLAYLISTS")
    r = sp.current_user_playlists()
    playlist_ids = parse_playlist_ids(r)

    print("EXTRACTING ARTISTS FROM USER PLAYLISTS")
    # Pull all the tracks from a playlist
    tracks = []
    albums = []
    artists = []

    # Loop through each playlist one by one
    for pid in playlist_ids:
        # Request all track information
        r = sp.playlist_items(pid)
        tracks, albums, artists = parse_track_info(r)
        
    
    # Condense into a series of normalized artist counts
    playlist_artists = pd.Series(artists)
    playlist_grouped = playlist_artists.value_counts(normalize=True)

    # Essentially create a fake user-ID for our listening history
    no_artist = playlist_grouped.shape[0]
    curr_user = grouped_df.iloc[-1]['user_id'] + 1
    curr_user_id = [curr_user] * no_artist

    # Creates a df of all artists in a users listening history, their normalized playcounts, 
    # and the user_id of the last user in the last.fm dataset?
    playlist_df = pd.DataFrame(playlist_grouped, columns=['playCountScaled']) 
    playlist_df.reset_index(level=0, inplace=True)
    playlist_df.columns = ['artist_name', 'playCountScaled']
    playlist_df['user_id'] = pd.Series(curr_user_id)
    
    # Reorganize df columns so that user_id comes first
    cols = playlist_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    playlist_df = playlist_df[cols]
    # Clean artist_name strings
    playlist_df['artist_name'] = playlist_df['artist_name'].str.lower() 

    # Create a dictionary that maps artist_names from last.fm with their artist_ids
    artist_pairing = dict(zip(grouped_df.artist_name, grouped_df.artist_id))

    # In the playlist df give artists their corresponding last.fm ID
    # Also drop any artists (NA values) that are not in the last.fm dataset
    playlist_df['artist_id'] = playlist_df['artist_name'].map(artist_pairing)
    playlist_df = playlist_df.dropna().reset_index(drop=True)
    playlist_df['artist_id'] = playlist_df['artist_id'].astype(int)

    # Append new user's listening history to the dataframe of last.fm user histories
    updated_df = grouped_df.append(playlist_df)

    # Create new user_ids and artist_ids to ensure consistiency before creating CF matricies
    updated_df['artist_name'] = updated_df['artist_name'].astype("category")
    updated_df['user_id'] = updated_df['user_id'].astype("category")
    updated_df['artist_id'] = updated_df['artist_id'].astype("category")
    updated_df['user_id'] = updated_df['user_id'].cat.codes
    updated_df['artist_id'] = updated_df['artist_id'].cat.codes

    print("CREATING ARTIST-USER AND USER-ARTIST MATRICIES")
    # Take user-artist pairings and their associated normalized playcounts and properly scale them
    sparse_artist_user = sparse.csr_matrix((updated_df['playCountScaled'].astype(float), (updated_df['artist_id'], updated_df['user_id'])))
    sparse_user_artist = sparse.csr_matrix((updated_df['playCountScaled'].astype(float), (updated_df['user_id'], updated_df['artist_id'])))
    model = implicit.als.AlternatingLeastSquares(factors=20, regularization=0.1, iterations=50)

    alpha = 15
    data = (sparse_artist_user * alpha).astype('double')
    print("FITTING ALS MODELS")
    model.fit(data)

    user_vecs = model.user_factors
    artist_vecs = model.item_factors
    # Create recommendations for current user
    user_id = curr_user
    print("GENERATING RECOMMMENDATIONS LIST")
    recommendations = recommend(user_id, sparse_user_artist, user_vecs, artist_vecs, updated_df)
    updated_df.loc[updated_df['user_id'] == curr_user].sort_values(by=['playCountScaled'], ascending=False)[['artist_name', 'user_id', 'playCountScaled']].head(10)
    artist_list = recommendations['artist_name'].to_list()

    # Take the given list of top artists recommendations and get each artist's top songs
    top_song_names, top_song_ids = get_top_recommended_tracks(artist_list, sp)

    print("Populating playlist with reccomendation")
    sp.playlist_add_items(playlist_id=playlist_t2['id'], 
                            items=top_song_ids, 
                            position=None)
    print("SUCCESS: Playlist populated")

    return render_template('gen_playlist_success.html')



if __name__ == '__main__':

    app.run(port = 8080, debug = True)