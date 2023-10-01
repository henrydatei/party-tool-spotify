# Spotify Party Tool
A tool that can generate playlists for partys

I've always wanted to have a tool that can generate playlists for partys. On a party you have several people with different taste of music. To find music that anymore more or less likes is a pretty hard job and ususally results in a massive queue of songs because someone added 100s of his favourite songs to it. This is my attempt to create such a helping tool to solve this issue. Once set up you can create a party, users can join it and through the login process with Spotify this tool can access the liked songs of every party guest. It analyses them by calling Spotify's own [Audio Features API](https://developer.spotify.com/documentation/web-api/reference/get-audio-features). After that you can create a playlist from that list of songs using the [Recommendation API](https://developer.spotify.com/documentation/web-api/reference/get-recommendations) from Spotify. To find some songs suitable for partys we can use the audio features extraced earlier. This tool supports a blacklist for unwanted songs too. You can blacklist certains songs or artists and you can even extract these from a playlist on Spotify. I've already added a preset for the genre "Deutschrap" because I hate it and I never want to listen to that on a party. After creating the playlist you can export it to your Spotify and play it. Have fun!

## Setup
Create an .env file in the root directory with the following content:
```
# True for development, False for production
DEBUG=True

# Deployment SERVER address
SERVER=.appseed.us

# Used for CDN (in production)
# No Slash at the end
ASSETS_ROOT=/static/assets

# Spotify credentials
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=YOUR_REDIRECT_URI
```
To get the Spotify credentials, you need to create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and add the redirect URI to the app. The redirect URI should end with /callback (e.g. http://localhost:8000/callback).

Run with (after clone and cd into the directory)
```bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```
The first two commands are just nessesary for the first time and setup the database. The last one starts the server. You can access the tool on http://localhost:8000. If you want to have a look at the admin interface and edit/view/delete/... the database, you can access it on http://localhost:8000/admin. You can login with the superuser you created earlier.

**Attention:** The tool needs a Spotify account to start. This account must also be the account that created the Spotify App on the Developer Dashboard. I am currently unable to provide a convenient way to login into this account, solution is to open a Python Shell in your home directory and run the following commands on your home computer (or any computer that has a web browser):
```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp_oauth = SpotifyOAuth("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "http://localhost:8080", scope="user-library-read,playlist-modify-public")
my_sp = spotipy.Spotify(auth_manager=sp_oauth)
```
Obviously you have to add "http://localhost:8080" to your created Spotify App in the Developer Dashboard as a redirect URL. After doing all of this your browser should open, you log in and Spotipy creates a file named `.cache` in your home directory. Copy this file to your server where you want to deploy the application in the directory of the repository. Luckily all of this is not necessary if you're running this tool on your local computer.
