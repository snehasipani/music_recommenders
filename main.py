# import os
# from flask import Flask, request, redirect, session, url_for

# from spotipy import Spotify
# from spotipy.oauth2 import SpotifyOAuth
# from spotipy.cache_handler import FlaskSessionCacheHandler


# app=Flask(__name__)
# app.config['SECRET_KEY']=os.urandom(64)

# client_id='48dc83bd0da14d33b82e67dadba37c5c'
# client_secret='5b386ff4cf9b4a3ba15d7cd5201fd6e4'
# redirect_uri='http://localhost:5000/callback'
# scope='playlist-read-private'

# cache_handler=FlaskSessionCacheHandler(session)
# sp_oauth=SpotifyOAuth(
#     client_id=client_id,
#     client_secret=client_secret,
#     redirect_uri=redirect_uri,
#     scope=scope,
#     cache_handler=cache_handler,
#     show_dialog=True
# )

# sp= Spotify(auth_manager=sp_oauth)

# @app.route('/')
# def home():
#     if not sp_oauth.validate_token(cache_handler.get_cached_token()):
#         auth_url=sp_oauth.get_authorize_url()
#         return redirect(auth_url)
    
#     return redirect(url_for('get_playlists'))

# @app.route('/callback')
# def callback():
#     sp_oauth.get_access_token(request.args['code'])
#     return redirect(url_for('get_playlists'))

# @app.route('/get_playlists')
# def get_playlists():
#     if not sp_oauth.validate_token(cache_handler.get_cached_token()):
#         auth_url = sp_oauth.get_authorize_url()
#         return redirect(auth_url)
    
#     playlists = sp.current_user_playlists()
#     playlists_info=[(pl['name'],pl['external_urls']["spotify"]) for pl in playlists['items']]
#     playlists_html='<br>'.join([f'{name}: {url}' for name, url in playlists_info])

#     return playlists_html

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('home'))

# if __name__=='__main__':
#     app.run(debug=True)


#different code(above for playlist link, below for accesiing songs)

import os
import time
import pandas as pd
from flask import Flask, request, redirect, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from spotipy.exceptions import SpotifyException

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = 'f30f8f9e73ab46578cec7c47a849c647'
client_secret = 'e63c80427c2f4c8481e316d761f904b0'
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

# Home route
@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    return redirect(url_for('get_playlists'))

# Callback route
@app.route('/callback')
def callback():
    try:
        sp_oauth.get_access_token(request.args['code'])
    except KeyError:
        return "Error: Spotify authentication failed. No 'code' found in the request."
    return redirect(url_for('get_playlists'))

# Function to retrieve track features with rate-limit handling
def get_tracks_features_in_batches(track_ids, batch_size=50):
    features = []
    
    # Break track IDs into batches to prevent hitting API limits
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        try:
            batch_features = sp.audio_features(batch)
            features.extend(batch_features)
        except SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                batch_features = sp.audio_features(batch)
                features.extend(batch_features)
            else:
                print(f"Error retrieving batch features: {e}")
    
    return features

# Function to get playlists and their tracks
@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    all_tracks = []
    
    for playlist in playlists['items']:
        print(f"Fetching tracks for playlist: {playlist['name']}")
        playlist_tracks = sp.playlist_tracks(playlist['id'])
        
        for track in playlist_tracks['items']:
            track_info = track['track']
            all_tracks.append({
                'track_name': track_info['name'],
                'artist': ', '.join([artist['name'] for artist in track_info['artists']]),
                'id': track_info['id']
            })

    # Extract track IDs for fetching audio features
    track_ids = [track['id'] for track in all_tracks if track['id']]

    # Fetch track features in batches
    track_features = get_tracks_features_in_batches(track_ids)

    # Combine track info with features
    track_data = []
    for track, feature in zip(all_tracks, track_features):
        if feature:  # Check if feature data is available
            track_data.append({
                'track_name': track['track_name'],
                'artist': track['artist'],
                'danceability': feature['danceability'],
                'energy': feature['energy'],
                'valence': feature['valence'],
                'tempo': feature['tempo']
            })

    # Create a DataFrame for the track data
    df = pd.DataFrame(track_data)

    # Save data to a CSV file for future use
    save_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'HackX', 'spotify_tracks.csv')
    df.to_csv(save_path, index=False)  # Ensure file path is properly formatted

    # Show a success message to the user
    return f"Track data saved to {save_path}. Total tracks: {len(track_data)}"

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

