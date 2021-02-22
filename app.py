# Web and Server
from flask import Flask, request, render_template, url_for
import datetime
import spotipy
import os
import requests

# Custom Classes
from lib.billboard import *
from lib.task1_cf import *
from lib.model_task2 import *


# ------------------------------------------- PATHS FOR DATA ---------------------------------------------------
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

# ------------------------------------------- DECLARE GLOBAL VARIABLES ---------------------------------------------------

testing = True

# Client Information
client_id = 'e6be6a0e60124f36ad99038de2f36e91'
client_secret = '14116a664bd84048a0c7c3004edc9726'
scope = " ".join(['playlist-modify-public',"user-top-read","user-read-recently-played","playlist-read-private"])

redirect_uri_1_1 = None
redirect_uri_1_2 = None 
redirect_uri_2_0 = None

# Actual Redirect
if testing:
    redirect_uri_1_1 = 'http://localhost:8080/form_1_1'
    redirect_uri_1_2 = 'http://localhost:8080/form_1_2'
    redirect_uri_2_0 = 'http://localhost:8080/form_2_0'
else:
    redirect_uri = 'http://35.166.214.194/form'

# Algorithm Information
AGE_LOWER_BOUND = 15
AGE_UPPER_BOUND = 30
TASK1_LENGTH = 20

# User input
global_vars = {
    'USER_ACCESS_CODE': None,
    'PARENT_ACCESS_CODE': None,
    'USER_AGE': None,
    'PARENT_AGE' : None,
    'PARENT_GENRE' : None,
    'PARENT_ARTIST' : None
}

task_1_1_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_AGE': None,
    'PARENT_GENRE': None,
    'PARENT_ARTIST': None
}

task_1_2_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_ACCESS_CODE': None,
    'USER_AGE': None,
    'PARENT_AGE': None,
    'PARENT_GENRE': None,
    'PARENT_ARTIST': None
}

task_2_0_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_AGE': None,
    'PARENT_GENRE': None,
    'PARENT_ARTIST': None
}


# ------------------------------------------- CREATE APPLICATION ---------------------------------------------------

app = Flask('__name__')

# ------------------------------------------- HOME PAGES ---------------------------------------------------

@app.route('/')
def index():
    '''
    Creates the landing page for the site and also generates the Spotify authorization URL

    Returns:
        The flask template for the landing page of our site
    '''

    # Oauth object    
    sp_oauth_1_1 = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_1_1, scope=scope)
    sp_oauth_1_2 = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_1_2, scope=scope)
    sp_oauth_2_0 = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_2_0, scope=scope)

    # Force auth every time
    auth_url_1_1 = sp_oauth_1_1.get_authorize_url()
    auth_url_1_2 = sp_oauth_1_2.get_authorize_url()
    auth_url_2_0 = sp_oauth_2_0.get_authorize_url()

    return render_template(
        'home/index.html', 
        auth_url_1_1 = auth_url_1_1,
        auth_url_1_2 = auth_url_1_2,
        auth_url_2_0 = auth_url_2_0
    )

@app.route('/about')
def about():
    '''
    Creates a page containing information about our project and it's motivations
    '''

    return render_template('home/about.html')


@app.route('/algorithms')
def algorithms():
    '''
    Creates a page containing information about the algorithms used in our project
    '''

    return render_template('home/algorithms.html')


# ------------------------------------------- FORM PAGES TASK 1.1 ---------------------------------------------------


@app.route('/form_1_1')
def form_1_1():
    

    task_1_1_responses['USER_ACCESS_CODE'] = request.args.get('code')
    
    return render_template('task1.1/form.html', access_code = task_1_1_responses['USER_ACCESS_CODE'])

@app.route('/form_success_1_1', methods=['POST'])
def form_success_1_1():
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
        return render_template('task1.1/form_failure.html',
                                age = age,
                                genre = genre,
                                artist = artist)

    # Set global variables based on correct input
    task_1_1_responses['PARENT_AGE'] = int(age)
    task_1_1_responses['PARENT_GENRE'] = genre
    task_1_1_responses['PARENT_ARTIST'] = artist

    return render_template('task1.1/form_success.html')

@app.route('/gen_playlist_1_1')
def gen_playlist_1_1():

    # Re make auth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_1_1, scope=scope)

    # Get the actual access token from the user's authentication
    token_info = sp_oauth.get_access_token(task_1_1_responses['USER_ACCESS_CODE'])
    access_token = token_info['access_token']

    # Create Spotify Object and get userID
    sp = spotipy.Spotify(auth=access_token)
    
    # Remove any cached tokens
    if os.path.exists('.cache'):
        os.remove('.cache')


    user = sp.current_user()['id']
    print("Creating empty playlists for: " + str(user))

    print("GENERATING SAMPLE PLAYLIST")
    # Create a blank playlist
    playlist_s = sp.user_playlist_create(user=user,
                                         name='Task 1: Sample',
                                         public = True,
                                         collaborative = False,
                                         description = 'This is a test')
    print("SUCCESS: Playlist created")
    

    print("Generating song recommendations")
    # Load in billboard data
    billboard_songs = pd.read_csv(BILLBOARD_SONGS_PATH_CLEAN)
    billboard_features = pd.read_csv(BILLBOARD_FEATURES_PATH_CLEAN)

    # Create billboard recommender object, generate recommendations, add to playlist
    billboard_recommender = billboard(billboard_songs, billboard_features)
    
    # sample playlist for parent_to_user
    sample_parent = billboard_recommender.getList(length = TASK1_LENGTH,
                                                age = task_1_1_responses['PARENT_AGE'],
                                                genre = task_1_1_responses['PARENT_GENRE'],
                                                artist = task_1_1_responses['PARENT_ARTIST']
                                                )
    print("SUCCESS: Recommendations Generated")
    
    
    
    print("Populating playlist with recommendations")
    sp.playlist_add_items(playlist_id=playlist_s['id'],
                          items=sample_parent,
                          position=None)
    print("SUCCESS: Playlist populated")

    return render_template('task1.1/gen_playlist_success.html') 

    # ------------------------------------------- FORM PAGES TASK 1.2 ---------------------------------------------------



    # ------------------------------------------- FORM PAGES TASK 2.0 ---------------------------------------------------



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

    
    
    

    #------------------------------------------------ GENERATING DEFAULT (TASK 1) PLAYLIST --------------------------------------
   

    print("GENERATING SAMPLE PLAYLIST")
    # Create a blank playlist
    playlist_s = sp.user_playlist_create(user=user,
                                         name='Task 1: Sample',
                                         public = True,
                                         collaborative = False,
                                         description = 'This is a test')
    print("SUCCESS: Playlist created")
    

    print("Generating song recommendations")
    # Load in billboard data
    billboard_songs = pd.read_csv(BILLBOARD_SONGS_PATH_CLEAN)
    billboard_features = pd.read_csv(BILLBOARD_FEATURES_PATH_CLEAN)

    # Determining time range for song recommendations
    current_year = datetime.datetime.today().year
    start_year = current_year - abs(global_vars['PARENT_AGE'] - AGE_LOWER_BOUND)
    end_year = current_year - abs(global_vars['PARENT_AGE'] - AGE_UPPER_BOUND)

    # Create billboard recommender object, generate recommendations, add to playlist
    billboard_recommender = billboard(billboard_songs, billboard_features)
    
    # sample playlist for parent_to_user
    sample_parent = billboard_recommender.getList(length = TASK1_LENGTH,
                                                age = global_vars['PARENT_AGE'],
                                                genre=global_vars['PARENT_GENRE'],
                                                artist=global_vars['PARENT_ARTIST']
                                                )
    print("SUCCESS: Recommendations Generated")
    print("Playlist Time Range: " + str(start_year) + " - "  + str(end_year))
    print("Playlist Length: " + str(len(sample_parent)) + " songs")
    
    
    print("Populating playlist with recommendations")
    sp.playlist_add_items(playlist_id=playlist_s['id'],
                          items=sample_parent,
                          position=None)
    print("SUCCESS: Playlist populated")
    

    #------------------------------------------------ GENERATING TASK 1 PLAYLIST ------------------------------------------------
    

    # print("GENERATING PLAYLIST 1")
    # # Create a blank playlist
    # playlist_t1 = sp.user_playlist_create(user=user,
    #                         name='Task1: Playlist',
    #                         public = True,
    #                         collaborative = False,
    #                         description = 'This is a test')
    # print("SUCCESS: Playlist created")
   
    
    # print("LOCATING SAMPLE PLAYLIST")
    # playlists = sp.current_user_playlists()['items']
    # sample_found = False # make user input for this
    # seed_tracks = []
    # #seed_artists = []
    # #seed_genres = set()
    
    # for playlist in playlists:
    #     if playlist['name'] == 'Task 1: Sample':
    #         sample_found = True
    #         print("FOUND SAMPLE PLAYLIST")
    #         # pull songs in sample playlist 
    #         for i in sp.playlist_tracks(playlist_id=playlist['id'])['items']:
    #             track = i['track']
    #             seed_tracks.append(track['id'])
    #             #seed_artists += [track['artists'][0]['id']]
    #             #seed_genres.add(track['genre'])
    #         break
    
    # if sample_found == False:
    #     print("SAMPLE PLAYLIST NOT FOUND, USING MOST RECENT USER DATA...")
    #     seed_tracks = current_user_recently_played(limit=TASK1_LENGTH)
        
    
    # print("Generating song recommendations")
    # billboard_reccomender = billboard(billboard_songs, billboard_features)
    # # bbList needs to get songs in the same timeframe
    # bbList = billboard_reccomender.getList(length=TASK1_LENGTH*2) #, age=global_vars[USER_AGE]); add input for user age
    
    # task1 = task1_cf(
    #     length= TASK1_LENGTH, 
    #     features= billboard_reccomender.billboard_features,
    #     seed_tracks = seed_tracks
    # )

    # parent_to_user = task1.getList(test_rec=bbList)
    
    
    # print("SUCCESS: Recommendations Generated")
    # print("Playlist Length: " + str(len(parent_to_user)) + " songs")
    
    # print("Populating playlist with recommendations")
    # sp.playlist_add_items(playlist_id=playlist_t1['id'], 
    #                         items=parent_to_user, 
    #                         position=None)
    # print("SUCCESS: Playlist populated")

    #------------------------------------------------ GENERATING TASK 2 PLAYLIST ------------------------------------------------
    print("GENERATING PLAYLIST 2")
    # Create a blank playlist
    playlist_t2 = sp.user_playlist_create(user=user,
                            name='Task2: Playlist',
                            public = True,
                            collaborative = False,
                            description = 'This is a test')
    print("SUCCESS: Blank playlist created")

    print("LOADING FILES")
    print("Loading Last.fm")
    user_profile_df, user_artist_df = read_datafiles(USER_PROFILE_PATH_CLEAN, USER_ARTIST_PATH_CLEAN)
    
    age_range = 5
    # Extracting users and user history based on parent age
    chosen_users = extract_users(user_profile_df, global_vars['PARENT_AGE'], age_range)
    chosen_history = extract_histories(user_artist_df, chosen_users)

    # Create additional artist/user statistics for generating recommendations
    grouped_df = prepare_dataset(chosen_history)

    print("GETTING USER PLAYLISTS")
    playlist_df, current_user = pull_user_playlist_info(sp, grouped_df)
    
    print("COMBINING USER HISTORY WITH LAST.FM HISTORY")
    updated_df = updated_df_with_user(grouped_df, playlist_df)

    print("FITTING ALS MODEL")
    alpha = 15
    # Create recommendations for current user
    user_id = current_user
    sparse_user_artist, user_vecs, artist_vecs = build_implicit_model(updated_df, alpha)
    
    print("GENERATING RECOMMMENDATIONS LIST")
    artist_recommendations = recommend(sp, user_id, sparse_user_artist, user_vecs, artist_vecs, updated_df)

    
    N = 50
    
    print("SELECTING TOP " +str(N)+ " RECOMMENDATIONS")
    recommended_tracks = get_top_recommended_tracks(artist_recommendations, GENRES, N)

    print("Populating playlist with recommendation")
    sp.playlist_add_items(playlist_id=playlist_t2['id'], 
                            items=top_song_ids, 
                            position=None)
    print("SUCCESS: Playlist populated")

    return render_template('gen_playlist_success.html')



if __name__ == '__main__':

    app.run(port = 8080, debug = True)