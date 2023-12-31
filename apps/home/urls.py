# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('joinParty/', views.joinParty, name='joinParty'),
    path('callback', views.callback, name='callback'),
    path('newParty/', views.newParty, name='newParty'),
    path('newPlaylist/', views.newPlaylist, name='newPlaylist'),
    path('processSongs/', views.processSongs, name='processSongs'),
    path('addToBlacklist/', views.addToBlacklist, name='addToBlacklist'),
    path('addPlaylistToSpotify/<int:playlist_id>', views.addPlaylistToSpotify, name='addPlaylistToSpotify'),
    path('addPlaylist/', views.addPlaylist, name='addPlaylist'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
