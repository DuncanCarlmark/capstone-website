# Web and Server
from flask import Flask, request, render_template
import spotipy

app = Flask('__name__')

code = None

@app.route('/')
def index():

    # Client Information
    client_id = 'e6be6a0e60124f36ad99038de2f36e91'
    client_secret = '14116a664bd84048a0c7c3004edc9726'

    # Temporary placeholder until we actually get a website going
    redirect_uri = 'http://127.0.0.1:8080/form'

    # The permissions that our application will ask for
    scope = " ".join(['playlist-modify-public',"user-top-read","user-read-recently-played","playlist-read-private"])

    # Oauth object    
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope)

    # Force auth every time
    auth_url = sp_oauth.get_authorize_url()

    return render_template('index.html', auth_url = auth_url)

@app.route('/form')
def form():

    code = request.args.get('code')


    return render_template('form.html')

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


if __name__ == '__main__':

    app.run(port = 8080, debug = True)