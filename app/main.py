import os
from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from .road2music.road2music import *
import uuid
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Client Credentials should be secret
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                                    client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                                    redirect_uri='https://road2music.herokuapp.com/createplaylist2',
                                                    scope='playlist-modify-public'))

# Spotify Environment Variables
# os.environ['SPOTIPY_CLIENT_ID'] = '********************'
# os.environ['SPOTIPY_CLIENT_SECRET'] = '****************************'
# os.environ['SPOTIPY_REDIRECT_URI'] = 'https://road2music.herokuapp.com/createplaylist2' #old one: os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:9090'
    # os.environ['SPOTIPY_CALLBACK_URL'] = 'https://road2music.herokuapp.com/'
# os.environ['SPOTIPY_FRONTEND_URI'] = 'http://localhost:300'

app = Flask(__name__)
app.config['98449a5d11c5430eb76c8b4d'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SPOTIPY_REDIRECT_URI'] = 'https://road2music.herokuapp.com/createplaylist2' #old one: os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:9090'
app.config['SPOTIPY_CALLBACK_URL'] = 'https://road2music.herokuapp.com/'
app.config['SPOTIPY_FRONTEND_URI'] = 'http://localhost:300'
Session(app)


# creating caches folder for Spotify
caches_folder = './.spotify_caches/'
# if not os.path.exists(caches_folder):
#     os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

# base
@app.route('/base')
def base():
    return render_template("base.html")

# homepage
@app.route('/')
def home():
   return render_template("home.html")

# Spotify Login Page
@app.route('/createplaylist', methods=["get"]) #formular
def createplaylist():
    # Step 1. User is unknown and is given random ID
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(os.environ['SPOTIPY_CLIENT_ID'],
                                                os.environ['SPOTIPY_CLIENT_SECRET'],
                                                app.config['SPOTIPY_REDIRECT_URI'],
                                                scope='playlist-modify-public',
                                                cache_path=session_cache_path(),
                                                show_dialog=True)

    # Step 3. Being redirected from Spotify auth page
    if request.args.get("code"):
       auth_manager.get_access_token(request.args.get("code"))
       return redirect('https://road2music.herokuapp.com/createplaylist2')

    # Step 2. Display sign in link when no token
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return render_template('createplaylist.html', signin_url=auth_url) # originally login.html

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    post["username"] = spotify.me()["display_name"]
    post["playlist_src"] = ''
    playlists = spotify.current_user_playlists()
    list_playlists = []
    for playlist in playlists["items"]:
        print(playlist["owner"]["display_name"])
        if playlist["owner"]["display_name"] == post["username"]:
            list_playlists.append(playlist["name"])
    list_playlists = sorted(list_playlists)
    return render_template("index_form.html", posts=post,list_playlists = list_playlists)


# Get route details
# form:
@app.route('/createplaylist2', methods=["get"])
def createplaylist2_get():
    return render_template("index_form.html")

@app.route('/createplaylistverify', methods=['GET'])
def createplaylistverify():
    # Get data from /createplaylist
    selected_playlist = request.args.get("selected_playlist")
    user_origin = request.args.get("origin")
    user_destination = request.args.get("destination")
    d = directions(user_origin, user_destination)
    origin_resolved, destination_resolved = resolve_origin_and_destination(d)
    # print("Origin: %s\nDestination: %s\nSelected playlist: %s" % (origin, destination, selected_playlist))
    # auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    return render_template("index.html", origin = origin_resolved, destination = destination_resolved)
    if not auth_manager.get_cached_token():
        return redirect('/createplaylist')

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    username = spotify.current_user()['id']
    playlist_data = Playlist(origin_resolved, destination_resolved, selected_playlist, spotify, username)
    playlist_src = "https://open.spotify.com/embed/playlist/" + playlist_data.playlist_id
    playlist_data.make_roadtrip_playlist()
    return jsonify({'src':playlist_src, 'playlist':playlist_data.selected_playlist})

# get route & create playlist
@app.route('/submit', methods=["get"])
def submit_get():
    origin = session.get("origin", None)
    destination = session.get("destination")
    playlist_name = "Road2Music - " + str(origin) + " to " + str(destination)
    print(f"Creating playlist with the name {playlist_name} in your Spotify account.")
#    spotify.user_playlist_create(user=spotify.me()['id'], name=playlist_name)
    # Get playlist id from previously created empty playlist by searching for the name within user's playlists
#    playlist_id = search_playlist_id(spotify, playlist_name)
    return render_template("submit.html", playlist_name = playlist_name)

# playlists from other users
@app.route('/userplaylists')
def userplaylists():
    return render_template("userplaylists.html")

# about
@app.route('/about')
def about():
    return render_template("about.html")

# contact
@app.route('/contact', methods=["get"])
def contact():
    # songname = request.args.get('songname')
    # artistname = request.args.get('artistname')
    # print(songname, artistname)
    return render_template("contact.html") #, songname=songname, artistname=artistname)

@app.route('/config.php', methods=["get"])
def config():
    songname = request.args.get('songname')
    artistname = request.args.get('artistname')
    print(f"song name: {songname}, artist's name: {artistname}")
    # with open("form-save.txt", "w") as variable_file:
    #     variable_file.write(songname)
    return render_template("contact.php", songname=songname, artistname=artistname)

if __name__ == "__main__":
    app.run(debug=True)
