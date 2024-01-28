import spotipy
from django.shortcuts import redirect
from decouple import config

# read environment variables
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_REDIRECT_URI')

# This will run every time before the view is loaded
# Make sure you enable this middleware in your settings.py
def is_user_authenticated(get_response):
    # Initialize request.code because we'll be using that in the index function in views.py
    def middleware(request):
        request.code = None
        
        # Liste der URLs, für die die Middleware deaktiviert werden soll
        excluded_paths = ['/admin']

        if any(request.path.startswith(path) for path in excluded_paths):
            # Wenn der Pfad in der Ausnahmeliste ist, fahre fort, ohne die Middleware auszuführen
            response = get_response(request)
            return response
        
        if "authenticate" not in request.path:
            # If the current path is not /authenticate then we run this

            # In the function authenticate in views.py, we passed context["auth_url"] to
            # the html so the user can press the link and get sent to the spotify
            # authentication page, once they accept/refuse they will get redirected back
            # to / that the index function handles, but before that happens we must
            # capture the code that the authentication link gave us and put it in request.code
            if request.method == "GET" and request.GET.get("code"):
                request.code = request.GET.get("code")

            # This ensures that the token is valid aka not expired when every view loads
            if not request.code:
                cache_handler = spotipy.DjangoSessionCacheHandler(request)
                auth_manager = spotipy.oauth2.SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    cache_handler=cache_handler
                )
                if not auth_manager.validate_token(cache_handler.get_cached_token()):
                    return redirect("authenticate")

        response = get_response(request)
        return response

    return middleware
