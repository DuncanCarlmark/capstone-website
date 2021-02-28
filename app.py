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
from lib.input_validation import *


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

testing = False
ec2_ip = '34.221.89.23'

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
    redirect_uri_1_1 = 'http://' + ec2_ip + '/form_1_1'
    redirect_uri_1_2 = 'http://' + ec2_ip + '/form_1_2'
    redirect_uri_2_0 = 'http://' + ec2_ip + '/form_2_0'
# Algorithm Information
AGE_LOWER_BOUND = 15
AGE_UPPER_BOUND = 30
TASK1_LENGTH = 20


task_1_1_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_AGE': None,
    'PARENT_GENRES': [],
    'PARENT_ARTIST': None
}

task_1_2_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_ACCESS_CODE': None,
    'USER_AGE': None,
    'PARENT_AGE': None,
    'PARENT_GENRES': [],
    'PARENT_ARTIST': None
}

task_2_0_responses = {
    'USER_ACCESS_CODE': None,
    'PARENT_AGE': None,
    'PARENT_GENRES': [],
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

# ===============================================================================================================================
# ===================================================== FORM PAGES TASK 1.1 =====================================================
# ===============================================================================================================================


@app.route('/form_1_1')
def form_1_1():
    
    # Load in genre list for datalist options
    genres_list = pd.read_csv('genre_list.csv')['genre_name']

    # Retrieve code from authentication
    task_1_1_responses['USER_ACCESS_CODE'] = request.args.get('code')
    
    return render_template('task1.1/form.html', genres_list = genres_list)

@app.route('/form_success_1_1', methods=['POST'])
def form_success_1_1():
    '''
    Generates the success page for when the user completes their form. Also pulls the
    information from the form (age, genre, artist) and store them in global variables to
    be referenced later by recommendation logic.

    Returns:
        The Flask template for the form success page
    '''
    # Results from form
    age = request.form.get('age')
    genre_1 = request.form.get('genre_1')
    genre_2 = request.form.get('genre_2')
    genre_3 = request.form.get('genre_3')
    artist = request.form.get('artist')

    # Condense genre input
    genre_input = [genre_1, genre_2, genre_3]

    # List of valid genres
    genres_list = pd.read_csv('genre_list.csv')['genre_name']

    print("GENRES PROVIDED BY USER")
    print(genre_input)
    
    # INPUT CHECK 1
    # Redirect to form if any required fields are not present
    if check_for_empty_fields(age, artist, genre_input):
        error_message = "Hey! You didn't fill out all the forms we asked you too. Please try again!"
        return render_template('task1.1/form_failure.html',
                                error_message = error_message,
                                genres_list = genres_list,
                                age = age,
                                genre_1 = genre_1,
                                genre_2 = genre_2,
                                genre_3 = genre_3,
                                artist = artist)

    # INPUT CHECK 2
    # Store valid and invalid genres separately
    valid_genres, invalid_genres = define_genre_input(genre_input, genres_list)

    # If there are no vaild genres, error and send the user back to form
    if len(invalid_genres) > 0:
        error_message = "Hey! These genres are invalid: " + str(invalid_genres) + ". Please use the drop down to ensure your entry is valid!"

        return render_template('task1.1/form_failure.html',
                                error_message = error_message,
                                genres_list = genres_list,
                                age = age,
                                genre_1 = genre_1,
                                genre_2 = genre_2,
                                genre_3 = genre_3,
                                artist = artist)

    # INPUT CHECK 3
    # Check if age is actually an integer
    if not check_age_is_int(age):
        error_message = "Hey! Please enter a valid integer for Parent Age"

        return render_template('task1.1/form_failure.html',
                                error_message = error_message,
                                genres_list = genres_list,
                                age = age,
                                genre_1 = genre_1,
                                genre_2 = genre_2,
                                genre_3 = genre_3,
                                artist = artist)


    # Populate global response tracker   
    task_1_1_responses['PARENT_AGE'] = int(age)
    task_1_1_responses['PARENT_ARTIST'] = artist

    for genre in valid_genres:
        task_1_1_responses['PARENT_GENRES'].append(genre)

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
    playlist = sp.user_playlist_create(user=user,
                                         name='Task 1.1 Playlist',
                                         public = True,
                                         collaborative = False,
                                         description = 'This is a test')
    print("SUCCESS: Playlist created")
    

    print("Generating song recommendations")
    # Load in billboard data
    billboard_songs = pd.read_csv(BILLBOARD_SONGS_PATH_CLEAN)
    billboard_features = pd.read_csv(BILLBOARD_FEATURES_PATH_CLEAN)

    print("CHECKING DATA")

    print(billboard_songs.shape)
    print(billboard_features.shape)

    # Create billboard recommender object, generate recommendations, add to playlist
    billboard_recommender = billboard(billboard_songs, billboard_features)
    
    # sample playlist for parent_to_user
    sample_parent = billboard_recommender.getList(length = TASK1_LENGTH,
                                                age = task_1_1_responses['PARENT_AGE'],
                                                genre = task_1_1_responses['PARENT_GENRES'],
                                                artist = task_1_1_responses['PARENT_ARTIST']
                                                )
    print("SUCCESS: Recommendations Generated")
        
    
    print("Populating playlist with recommendations")
    sp.playlist_add_items(playlist_id=playlist['id'],
                          items=sample_parent,
                          position=None)
    print("SUCCESS: Playlist populated")

    return render_template('task1.1/gen_playlist_success.html') 


# ===============================================================================================================================
# ===================================================== FORM PAGES TASK 1.2 =====================================================
# ===============================================================================================================================


@app.route('/form_1_2')
def form_1_2():
    

    task_1_2_responses['USER_ACCESS_CODE'] = request.args.get('code')
    
    return render_template('task1.2/form.html', access_code = task_1_2_responses['USER_ACCESS_CODE'])

@app.route('/form_success_1_2', methods=['POST'])
def form_success_1_2():
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
        return render_template('task1.2/form_failure.html',
                                age = age,
                                genre = genre,
                                artist = artist)

    # Set global variables based on correct input
    task_1_2_responses['PARENT_AGE'] = int(age)
    task_1_2_responses['PARENT_GENRES'] = genre
    task_1_2_responses['PARENT_ARTIST'] = artist

    return render_template('task1.2/form_success.html')

@app.route('/gen_playlist_1_2')
def gen_playlist_1_2():

    # Re make auth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_1_2, scope=scope)

    # Get the actual access token from the user's authentication
    token_info = sp_oauth.get_access_token(task_1_2_responses['USER_ACCESS_CODE'])
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
    playlist = sp.user_playlist_create(user=user,
                                         name='Task 1.2 Playlist',
                                         public = True,
                                         collaborative = False,
                                         description = 'This is a test')
    print("SUCCESS: Playlist created")
    

   

    return render_template('task1.2/gen_playlist_success.html') 


# ===============================================================================================================================
# ===================================================== FORM PAGES TASK 2.0 =====================================================
# ===============================================================================================================================


@app.route('/form_2_0')
def form_2_0():
    

    task_2_0_responses['USER_ACCESS_CODE'] = request.args.get('code')
    
    return render_template('task2.0/form.html', access_code = task_2_0_responses['USER_ACCESS_CODE'])

@app.route('/form_success_2_0', methods=['POST'])
def form_success_2_0():
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
        return render_template('task2.0/form_failure.html',
                                age = age,
                                genre = genre,
                                artist = artist)

    # Set global variables based on correct input
    task_2_0_responses['PARENT_AGE'] = int(age)
    task_2_0_responses['PARENT_GENRES'] = genre
    task_2_0_responses['PARENT_ARTIST'] = artist

    return render_template('task2.0/form_success.html')

@app.route('/gen_playlist_2_0')
def gen_playlist_2_0():

    # Re make auth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri_2_0, scope=scope)

    # Get the actual access token from the user's authentication
    token_info = sp_oauth.get_access_token(task_2_0_responses['USER_ACCESS_CODE'])
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
    playlist = sp.user_playlist_create(user=user,
                                         name='Task 2.0 Playlist',
                                         public = True,
                                         collaborative = False,
                                         description = 'This is a test')
    print("SUCCESS: Playlist created")

    print("LOADING FILES")
    print("Loading Last.fm")
    user_profile_df, user_artist_df = read_datafiles(USER_PROFILE_PATH_CLEAN, USER_ARTIST_PATH_CLEAN)

    
    
    age_range = 5
    # Extracting users and user history based on parent age
    chosen_users = extract_users(user_profile_df, task_2_0_responses['PARENT_AGE'], age_range)
    chosen_history = extract_histories(user_artist_df, chosen_users)

    # Create additional artist/user statistics for generating recommendations
    print("PREPARING USER HISTORY GIVEN AGE")
    grouped_df = prepare_dataset(chosen_history)
    print("RESULTING DATAFRAME SHAPE:")
    print(grouped_df.shape)

    print("GETTING USER PLAYLISTS")
    playlist_df, current_user = pull_user_playlist_info(sp, grouped_df)
    print("RESULTING DATAFRAME SHAPE:")
    print(playlist_df.shape)

    print("COMBINING USER HISTORY WITH LAST.FM HISTORY")
    updated_df = updated_df_with_user(grouped_df, playlist_df)
    print("RESULTING DATAFRAME SHAPE:")
    print(updated_df.shape)

    # Create recommendations for current user
    print("FITTING ALS MODEL")
    alpha = 15
    user_id = current_user
    sparse_user_artist, user_vecs, artist_vecs = build_implicit_model(updated_df, alpha)
    
    # Get a list of recommended artists
    print("GENERATING RECOMMMENDATIONS LIST")
    artist_recommendations = recommend(sp, user_id, sparse_user_artist, user_vecs, artist_vecs, updated_df)
    print("NUMBER OF RECOMMENDED ARTISTS:")
    print(artist_recommendations.shape)

    # Get a list of recommended tracks from recommended artists
    N = 50
    print("SELECTING TOP " +str(N)+ " RECOMMENDATIONS")
    recommended_tracks = get_top_recommended_tracks(artist_recommendations, task_2_0_responses['PARENT_GENRES'], N)

    print(recommended_tracks.shape)
   
    top_song_ids = get_recommended_song_ids(recommended_tracks['artist_top_tracks'], sp)

    print("Populating playlist with recommendation")
    sp.playlist_add_items(playlist_id=playlist['id'], 
                            items=top_song_ids, 
                            position=None)
    print("SUCCESS: Playlist populated")
    

   

    return render_template('task2.0/gen_playlist_success.html') 


# ===============================================================================================================================
# ===================================================== GARBAGE =====================================================
# ===============================================================================================================================





if __name__ == '__main__':

    app.run(port = 8080, debug = True)