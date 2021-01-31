# Web and Server
from flask import Flask, request, render_template, url_for
import spotipy

app = Flask('__name__')

global_vars = {}

@app.route('/')
def index():

    # Client Information
    client_id = 'e6be6a0e60124f36ad99038de2f36e91'
    client_secret = '14116a664bd84048a0c7c3004edc9726'

    # Temporary placeholder until we actually get a website going
    redirect_uri = 'http://52.11.255.57/form'

    # The permissions that our application will ask for
    scope = " ".join(['playlist-modify-public',"user-top-read","user-read-recently-played","playlist-read-private"])

    # Oauth object    
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)

    # Force auth every time
    auth_url = sp_oauth.get_authorize_url()

    return render_template('index.html', auth_url = auth_url)

@app.route('/form')
def form():

    global_vars['access_code'] = request.args.get('code')
    
   

    return render_template('form.html', access_code = global_vars['access_code'])

@app.route('/form_success', methods=['POST'])
def form_success():
    age = request.form.get('age')
    genre = request.form.get('genre')
    artist = request.form.get('artist')

    if not age or not genre or not artist:
        error_message = 'Hey! We said to fill out all the forms.'
        return render_template('form_failure.html',
                                age = age,
                                genre = genre,
                                artist = artist)

    return render_template('form_success.html')

@app.route('/gen_playlist')
def gen_playlist():

    # Auth info
    client_id = 'e6be6a0e60124f36ad99038de2f36e91'
    client_secret = '14116a664bd84048a0c7c3004edc9726'
    redirect_uri = 'http://52.11.255.57/form'
    scope = " ".join(['playlist-modify-public',"user-top-read","user-read-recently-played","playlist-read-private"])
    
    # Re make auth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)
    
    # Get the actual access token
    token_info = sp_oauth.get_access_token(global_vars['access_code'])
    access_token = token_info['access_token']


    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()['id']

    sp.user_playlist_create(user=user,
                            name='stonk me daddy',
                            public = True,
                            collaborative = False,
                            description = 'This is a test')
    return render_template('gen_playlist_success.html')



if __name__ == '__main__':

    app.run(port = 8080, debug = True)