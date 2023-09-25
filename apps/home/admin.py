# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Song, Blacklist, Playlist, User, Party

# Register your models here.
admin.site.register(Song)
admin.site.register(Blacklist)
admin.site.register(Playlist)
admin.site.register(User)
admin.site.register(Party)