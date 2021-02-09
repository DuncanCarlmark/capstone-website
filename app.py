# Web and Server
from flask import Flask, request, render_template, url_for
import datetime
import spotipy
import os

# Custom Classes
from scripts.billboard import *

# ------------------------------------------- DECLARE GLOBAL VARIABLES ---------------------------------------------------

testing = True

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
    redirect_uri = 'http://54.200.135.162/form'

# User input
global_vars = {'access_code': None,
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
    print("Creating empty playlist for: " + str(user))


    # Create a blank playlist
    playlist = sp.user_playlist_create(user=user,
                            name='IS DIS WORKING',
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
    sp.playlist_add_items(playlist_id=playlist['id'], 
                            items=parent_to_user, 
                            position=None)
    print("SUCCESS: Playlist populated")



    return render_template('gen_playlist_success.html')



if __name__ == '__main__':

    app.run(port = 8080, debug = True)