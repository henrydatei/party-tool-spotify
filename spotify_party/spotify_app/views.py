from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID = '***REMOVED***'
SPOTIPY_CLIENT_SECRET = '***REMOVED***'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'

sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope="user-library-read")

def login(request):
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    token_info = sp_oauth.get_access_token(request.GET.get('code'))
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Hier könntest du die Daten wie gewünscht verarbeiten
    results = sp.current_user_saved_tracks()
    liked_songs = [(item['track']['artists'][0]['name'], item['track']['name']) for item in results['items']]
    return render(request, 'songs.html', {'songs': liked_songs})
