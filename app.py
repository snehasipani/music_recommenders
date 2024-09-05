from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__, static_folder='static')
CORS(app)

SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    auth_data = auth_response.json()
    return auth_data['access_token']

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'first.html')

@app.route('/api/genres')
def get_genres():
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{SPOTIFY_API_BASE_URL}/recommendations/available-genre-seeds', headers=headers)
    return jsonify(response.json())

@app.route('/api/artists', methods=['POST'])
def get_artists():
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    genres = request.json['genres']
    artists = []
    for genre in genres:
        response = requests.get(f'{SPOTIFY_API_BASE_URL}/search?q=genre:{genre}&type=artist&limit=3', headers=headers)
        data = response.json()
        artists.extend(data['artists']['items'])
    return jsonify(artists)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    artists = request.json['artists']
    artist_ids = ','.join(artists)
    response = requests.get(f'{SPOTIFY_API_BASE_URL}/recommendations?seed_artists={artist_ids}&limit=10', headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)