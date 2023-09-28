# Generated by Django 4.2.3 on 2023-09-28 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_song_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('spotify_id', models.TextField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='song',
            name='artist',
        ),
        migrations.AddField(
            model_name='playlist',
            name='songs_filtered_by_blacklist',
            field=models.ManyToManyField(related_name='songs_filtered_by_blacklist', to='home.song'),
        ),
        migrations.AddField(
            model_name='song',
            name='artists',
            field=models.ManyToManyField(to='home.artist'),
        ),
    ]
