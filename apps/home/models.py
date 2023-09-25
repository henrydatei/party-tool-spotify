# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Song(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.TextField()
    title = models.TextField()
    spotify_id = models.TextField()
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.IntegerField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    duration_ms = models.IntegerField()
    popularity = models.IntegerField()
    language = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
class Blacklist(models.Model):
    id = models.AutoField(primary_key=True)
    spotify_id = models.TextField()
    type = models.TextField()
    
    def __str__(self):
        return f"{self.type} - {self.spotify_id}"
    
class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    spotify_id = models.TextField()
    name = models.TextField()
    description = models.TextField()
    songs = models.ManyToManyField(Song)
    
    def __str__(self):
        return f"{self.name} - {self.description}"
    
class User(models.Model):
    id = models.AutoField(primary_key=True)
    spotify_id = models.TextField()
    name = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.spotify_id}"    
    
class Party(models.Model):
    id = models.AutoField(primary_key=True)
    playlists = models.ManyToManyField(Playlist)
    users = models.ManyToManyField(User)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    songs_from_users = models.ManyToManyField(Song)
    
    def __str__(self):
        return f"Party {self.id} am {self.date}"