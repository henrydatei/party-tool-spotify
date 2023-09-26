# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from django.db.models import Q

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from polyglot.detect import Detector

from .models import Party, Song, Blacklist, Playlist, User

SPOTIPY_CLIENT_ID = '***REMOVED***'
SPOTIPY_CLIENT_SECRET = '***REMOVED***'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback'
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope="user-library-read")
my_sp = spotipy.Spotify(auth_manager=sp_oauth)

def check_language_of_song(trackID):
    r = requests.get(f"https://spotify-lyric-api.herokuapp.com/?trackid={trackID}")
    if r.status_code != 200:
        return "none"
    text = ""
    for line in r.json()["lines"]:
        text += line["words"] + "\n"
    return Detector(text).language.code

def index(request: HttpRequest):
    party = Party.objects.filter(active=True).first()
    context = {'party': party}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def joinParty(request: HttpRequest):
    party = Party.objects.filter(active=True).first()
    if not party:
        return redirect('home')
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
        for item in results['items']:
            # Check if song is already in database
            if Song.objects.filter(spotify_id=item['track']['id']).exists():
                song = Song.objects.get(spotify_id=item['track']['id'])
                party.songs_from_users.add(song)
                continue
            song = Song()
            song.artist = ", ".join([artist['name'] for artist in item['track']['artists']])
            song.title = item['track']['name']
            song.spotify_id = item['track']['id']
            song.popularity = item['track']['popularity']
            song.duration_ms = item['track']['duration_ms']
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
    not_processed_songs = Song.objects.filter(Q(danceability__isnull=True) | Q(energy__isnull=True) | Q(key__isnull=True) | Q(loudness__isnull=True) | Q(mode__isnull=True) | Q(speechiness__isnull=True) | Q(acousticness__isnull=True) | Q(instrumentalness__isnull=True) | Q(liveness__isnull=True) | Q(valence__isnull=True) | Q(tempo__isnull=True) | Q(language__isnull=True)).all()
    for song in not_processed_songs:
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
        song.language = check_language_of_song(song.spotify_id)
        song.save()
    return redirect('home')

def newPlaylist(request: HttpRequest):
    return render(request, 'home/newPlaylist.html')

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
