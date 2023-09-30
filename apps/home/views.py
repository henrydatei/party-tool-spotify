# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import numpy as np
from datetime import datetime
from decouple import config
import pandas as pd

from .models import Party, Song, Blacklist, Playlist, User, Artist

# read environment variables
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = config('SPOTIFY_REDIRECT_URI')

# login to spotify
sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope="user-library-read,playlist-modify-public")
my_sp = spotipy.Spotify(auth_manager=sp_oauth)
my_id = my_sp.me()["id"]

# filter for songs
PARTY_FILTER = {
    "min_danceability": 0.8, 
    "min_energy": 0.6,
    "max_liveness": 0.3, 
    "max_duration_ms": 240000, 
    "max_instrumentalness": 0.1, 
    "max_speechiness": 0.3, 
    "min_valence": 0.5,
    "min_popularity": 20
}
CLUB_FILTER = {
    "min_energy": 0.9, 
    "min_danceability": 0.5, 
    "max_liveness": 0.3, 
    "max_duration_ms": 240000, 
    "min_tempo": 120, 
    "max_speechiness": 0.3,
    "min_popularity": 20
}

def convert_dict_filter_to_orm_filter(dict_filter: dict):
    filter_conditions = {}
    for key, value in dict_filter.items():
        if key.startswith("min_"):
            filter_key = key[4:] + "__gte"  # Verwende den "__gte" (greater than or equal) Lookup
        elif key.startswith("max_"):
            filter_key = key[4:] + "__lte"  # Verwende den "__lte" (less than or equal) Lookup
        else:
            filter_key = key  # Wenn es kein "min_" oder "max_" gibt, verwende den Schlüssel direkt
        filter_conditions[filter_key] = value
        
    return filter_conditions

def index(request: HttpRequest):
    currentParty = Party.objects.filter(active=True).first()
    if not currentParty:
        return render(request, 'home/noParty.html')
    if not currentParty.users.all():
        return render(request, 'home/noUsers.html')
    if not currentParty.playlists.all():
        return render(request, 'home/noPlaylists.html')
    
    allSongsinPlaylists = []
    for playlist in currentParty.playlists.all():
        allSongsinPlaylists += playlist.songs.all()
    
    context = {
        'party': currentParty,
        'danceability': np.mean([song.danceability for song in allSongsinPlaylists]) * 100,
        'energy': np.mean([song.energy for song in allSongsinPlaylists]) * 100,
        'loudness': np.mean([song.loudness for song in allSongsinPlaylists]),
        'speechiness': np.mean([song.speechiness for song in allSongsinPlaylists]) * 100,
        'acousticness': np.mean([song.acousticness for song in allSongsinPlaylists]) * 100,
        'instrumentalness': np.mean([song.instrumentalness for song in allSongsinPlaylists]) * 100,
        'liveness': np.mean([song.liveness for song in allSongsinPlaylists]) * 100,
        'valence': np.mean([song.valence for song in allSongsinPlaylists]) * 100,
        'tempo': np.mean([song.tempo for song in allSongsinPlaylists]),
        'popularity': np.mean([song.popularity for song in allSongsinPlaylists]),
        'playlists': currentParty.playlists.all(),
        'filtered_by_blacklist': sum([playlist.songs_filtered_by_blacklist.count() for playlist in currentParty.playlists.all()]),
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def joinParty(request: HttpRequest):
    party = Party.objects.filter(active=True).first()
    if not party:
        return render(request, 'home/noParty.html')
    else:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

def callback(request: HttpRequest):
    token_info = sp_oauth.get_access_token(request.GET.get('code'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    # Create a new User
    user = User()
    user.spotify_id = sp.me()['id']
    user.access_token = token_info['access_token']
    user.name = sp.me()['display_name']
    user.save()
    
    # Add User to Party
    party = Party.objects.filter(active=True).first()
    party.users.add(user)

    # Process Songs
    number_of_liked_songs = sp.current_user_saved_tracks(limit=1)['total']
    i = 0
    while i < number_of_liked_songs:
        results = sp.current_user_saved_tracks(limit=50, offset=i)
        for item in results['items']: # TODO: Process multiple songs at once, max 50
            # Check if song is already in database
            if Song.objects.filter(spotify_id=item['track']['id']).exists():
                song = Song.objects.get(spotify_id=item['track']['id'])
                party.songs_from_users.add(song)
                continue
            song = Song()
            song.title = item['track']['name']
            song.spotify_id = item['track']['id']
            song.popularity = item['track']['popularity']
            song.duration_ms = item['track']['duration_ms']
            song.cover = item['track']['album']['images'][0]['url']
            song.save()
            for artist in item['track']['artists']:
                if not Artist.objects.filter(spotify_id=artist['id']).exists():
                    a = Artist()
                    a.name = artist['name']
                    a.spotify_id = artist['id']
                    a.save()
                song.artists.add(Artist.objects.get(spotify_id=artist['id']))
            song.save()
            party.songs_from_users.add(song)
        i += 50
    party.save()
    return redirect('home')

def newParty(request: HttpRequest):
    if request.method == 'POST':
        # set status of all partys to inactive
        for party in Party.objects.all():
            party.active = False
            party.save()
        # create new party
        party = Party()
        party.date = request.POST['date']
        party.description = request.POST['description']
        party.save()
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'home/newParty.html')

def processSongs(request: HttpRequest):
    not_processed_songs = Song.objects.filter(processed=False)
    for song in not_processed_songs: # TODO: Process multiple songs at once, max 50
        features = my_sp.audio_features(song.spotify_id)[0]
        song.danceability = features["danceability"]
        song.energy = features["energy"]
        song.key = features["key"]
        song.loudness = features["loudness"]
        song.mode = features["mode"]
        song.speechiness = features["speechiness"]
        song.acousticness = features["acousticness"]
        song.instrumentalness = features["instrumentalness"]
        song.liveness = features["liveness"]
        song.valence = features["valence"]
        song.tempo = features["tempo"]
        song.save()
    return redirect('home')

def newPlaylist(request: HttpRequest):
    currentParty = Party.objects.filter(active=True).first()
    if not currentParty:
        return render(request, 'home/noParty.html')
    if not currentParty.users.all():
        return render(request, 'home/noUsers.html')
    allSongs = currentParty.songs_from_users.all()
    processedSongs = currentParty.songs_from_users.filter(processed=True)
    
    # The Blacklist
    blacklist_songs = Blacklist.objects.filter(type="title")
    blacklist_artists_ids = [item.spotify_id for item in Blacklist.objects.filter(type="artist")]
    songs_from_blacklisted_artists = Song.objects.filter(artists__spotify_id__in=blacklist_artists_ids)
    blacklisted_song_ids = [item.spotify_id for item in blacklist_songs]
    blacklisted_artist_song_ids = [song.spotify_id for song in songs_from_blacklisted_artists]
    all_blacklisted_ids = set(blacklisted_song_ids + blacklisted_artist_song_ids)
    partySongs = currentParty.songs_from_users.filter(**convert_dict_filter_to_orm_filter(PARTY_FILTER)).exclude(spotify_id__in=all_blacklisted_ids)
    clubSongs = currentParty.songs_from_users.filter(**convert_dict_filter_to_orm_filter(CLUB_FILTER)).exclude(spotify_id__in=all_blacklisted_ids)
    
    if request.method == 'POST':
        batchSize = int(request.POST['batchSize'])
        recommendatonSize = int(request.POST['recommendationSize'])
        playlistLength = int(request.POST['playlistLength'])
        if request.POST['filter'] == "party":
            party = True
        else:
            party = False
        
        # Value checks
        if batchSize < 1:
            batchSize = 1
        if batchSize > 5:
            batchSize = 5
        if recommendatonSize < 1:
            recommendatonSize = 1
        if recommendatonSize > 100:
            recommendatonSize = 100
            
        # Create new Playlist
        playlist = Playlist()
        playlist.name = f"Party {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        playlist.save()
        while playlist.songs.count() < playlistLength:
            if party:
                seed_songs = random.sample(list(partySongs), batchSize)
                filter = PARTY_FILTER
            else:
                seed_songs = random.sample(list(clubSongs), batchSize)
                filter = CLUB_FILTER
            results = my_sp.recommendations(seed_tracks=[song.spotify_id for song in seed_songs], limit=recommendatonSize, **filter)
            for item in results['tracks']: # TODO: Process multiple songs at once, max 50
                # Check if song is already in database
                if Song.objects.filter(spotify_id=item['id']).exists():
                    song = Song.objects.get(spotify_id=item['id'])
                    playlist.songs.add(song)
                    continue
                song = Song()
                song.title = item['name']
                song.spotify_id = item['id']
                song.popularity = item['popularity']
                song.duration_ms = item['duration_ms']
                song.cover = item['album']['images'][0]['url']
                audio_features = my_sp.audio_features(song.spotify_id)[0]
                song.danceability = audio_features["danceability"]
                song.energy = audio_features["energy"]
                song.key = audio_features["key"]
                song.loudness = audio_features["loudness"]
                song.mode = audio_features["mode"]
                song.speechiness = audio_features["speechiness"]
                song.acousticness = audio_features["acousticness"]
                song.instrumentalness = audio_features["instrumentalness"]
                song.liveness = audio_features["liveness"]
                song.valence = audio_features["valence"]
                song.tempo = audio_features["tempo"]
                song.save()
                for artist in item['artists']:
                    if not Artist.objects.filter(spotify_id=artist['id']).exists():
                        a = Artist()
                        a.name = artist['name']
                        a.spotify_id = artist['id']
                        a.save()
                    song.artists.add(Artist.objects.get(spotify_id=artist['id']))
                song.save()
                # Check if any artist is blacklisted
                if song.artists.filter(spotify_id__in=blacklist_artists_ids).exists():
                    playlist.songs_filtered_by_blacklist.add(song)
                    continue
                # Check if song is blacklisted
                if Blacklist.objects.filter(spotify_id=song.spotify_id, type="title").exists():
                    playlist.songs_filtered_by_blacklist.add(song)
                    continue
                # Check if song is already in playlist
                if playlist.songs.filter(spotify_id=song.spotify_id).exists():
                    continue
                playlist.songs.add(song)
        playlist.save()
        currentParty.playlists.add(playlist)
        currentParty.save()
    
    context = {
        "processedSongs": len(processedSongs),
        "processedSongsPct": len(processedSongs) / len(allSongs) * 100 if len(allSongs) > 0 else 0,
        "useableSongsParty": len(partySongs),
        "useableSongsPartyPct": len(partySongs) / len(processedSongs) * 100 if len(processedSongs) > 0 else 0,
        "useableSongsClub": len(clubSongs),
        "useableSongsClubPct": len(clubSongs) / len(processedSongs) * 100 if len(processedSongs) > 0 else 0,
        "blacklistLength": len(all_blacklisted_ids),
    }
    
    return render(request, 'home/newPlaylist.html', context)

def addToBlacklist(request: HttpRequest):
    if request.method == 'POST':
        # Check which preset is selected
        if request.POST['preset'] == "deutschrap":
            single_artists = pd.read_html("https://de.wikipedia.org/wiki/Liste_von_Hip-Hop-Musikern_Deutschlands")[0].iloc[:,1].tolist()
            groups = pd.read_html("https://de.wikipedia.org/wiki/Liste_von_Hip-Hop-Musikern_Deutschlands")[1].iloc[:,1].tolist()
            for rapper in list(set(single_artists + groups)):
                result = my_sp.search(q='artist:' + rapper, type='artist')
                try:
                    artist_id = result['artists']['items'][0]['id']
                    artist_name = result['artists']['items'][0]['name']
                    if not Blacklist.objects.filter(spotify_id=artist_id, type="artist").exists():
                        Blacklist.objects.create(spotify_id=artist_id, type="artist", name=artist_name)
                except IndexError:
                    print(f"Artist {rapper} not found")

        # Not preset selected, check if url or id is given
        elif request.POST["url_or_id"] and request.POST["type"]:
            url_or_id = request.POST["url_or_id"]
            type = request.POST["type"]
            if type == "artist":
                try:
                    result = my_sp.artist(url_or_id)
                    artist_id = result['id']
                    if not Blacklist.objects.filter(spotify_id=artist_id, type="artist").exists():
                        Blacklist.objects.create(spotify_id=artist_id, type="artist", name=result['name'])
                except IndexError:
                    print(f"Artist {url_or_id} not found")
                    pass
            elif type == "title":
                try:
                    result = my_sp.track(url_or_id)
                    track_id = result['id']
                    if not Blacklist.objects.filter(spotify_id=track_id, type="title").exists():
                        Blacklist.objects.create(spotify_id=track_id, type="title", name=result['name'])
                except IndexError:
                    print(f"Title {url_or_id} not found")
                    pass 
            elif type == "playlist_artist":
                try:
                    result = my_sp.playlist(url_or_id)
                    for item in result['tracks']['items']:
                        for artist in item['track']['artists']:
                            artist_id = artist['id']
                            if not Blacklist.objects.filter(spotify_id=artist_id, type="artist").exists():
                                Blacklist.objects.create(spotify_id=artist_id, type="artist", name=artist['name'])
                except Exception as e:
                    print(f"Error with {url_or_id}: {e}")
                    pass
            elif type == "playlist_title":
                try:
                    result = my_sp.playlist(url_or_id)
                    for item in result['tracks']['items']:
                        track_id = item['track']['id']
                        if not Blacklist.objects.filter(spotify_id=track_id, type="title").exists():
                            Blacklist.objects.create(spotify_id=track_id, type="title", name=item['track']['name'])
                except Exception as e:
                    print(f"Error with {url_or_id}: {e}")
                    pass
                
    blacklist_songs = Blacklist.objects.filter(type="title").count()
    blacklist_artists = Blacklist.objects.filter(type="artist").count()
    
    context = {
        'blacklist_songs': blacklist_songs,
        'blacklist_artists': blacklist_artists,
    }
    
    return render(request, 'home/addToBlacklist.html', context)

def addPlaylistToSpotify(request: HttpRequest, playlist_id: int):
    playlist = Playlist.objects.get(id=playlist_id)
    created_playlist = my_sp.user_playlist_create(my_id, playlist.name, public=True, collaborative=False, description=playlist.description)
    my_sp.user_playlist_add_tracks(my_id, created_playlist["id"], [song.spotify_id for song in playlist.songs.all()])
    playlist.spotify_id = created_playlist["id"]
    playlist.save()
    return redirect('home')

def pages(request: HttpRequest):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
