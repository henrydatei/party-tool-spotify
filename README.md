# spotify-party-tool
A tool that can generate playlists for partys

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
cd spotify_party
python3 manage.py runserver
```