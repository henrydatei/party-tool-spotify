# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Song(models.Model):
    artist = models.TextField()
    title = models.TextField()
    spotify_id = models.TextField(primary_key=True)
    danceability = models.FloatField(null=True, default=None)
    energy = models.FloatField(default=None, null=True)
    key = models.IntegerField(default=None, null=True)
    loudness = models.FloatField(default=None, null=True)
    mode = models.IntegerField(default=None, null=True)
    speechiness = models.FloatField(default=None, null=True)
    acousticness = models.FloatField(default=None, null=True)
    instrumentalness = models.FloatField(default=None, null=True)
    liveness = models.FloatField(default=None, null=True)
    valence = models.FloatField(default=None, null=True)
    tempo = models.FloatField(default=None, null=True)
    duration_ms = models.IntegerField()
    popularity = models.IntegerField()
    language = models.TextField(default=None, null=True)
    processed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        fields_to_check = [
            self.danceability, self.energy, self.key, self.loudness, self.mode,
            self.speechiness, self.acousticness, self.instrumentalness, 
            self.liveness, self.valence, self.tempo, self.language
        ]

        self.processed = all(field is not None for field in fields_to_check)

        super(Song, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
class Blacklist(models.Model):
    spotify_id = models.TextField(primary_key=True)
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
    spotify_id = models.TextField(primary_key=True)
    name = models.TextField()
    access_token = models.TextField(default="")
    
    def __str__(self):
        return f"{self.name} - {self.spotify_id}"    
    
class Party(models.Model):
    id = models.AutoField(primary_key=True)
    playlists = models.ManyToManyField(Playlist)
    users = models.ManyToManyField(User)
    date = models.DateField()
    active = models.BooleanField(default=True)
    songs_from_users = models.ManyToManyField(Song)
    description = models.TextField(default="")
    
    def __str__(self):
        return f"Party {self.id} am {self.date}"