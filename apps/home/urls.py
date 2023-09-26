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
    path('callback/', views.callback, name='callback'),
    path('newParty/', views.newParty, name='newParty'),
    path('newPlaylist/', views.newPlaylist, name='newPlaylist'),
    path('processSongs/', views.processSongs, name='processSongs'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
