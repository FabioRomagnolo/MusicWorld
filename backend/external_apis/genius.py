import os
import re

import lyricsgenius

from requests.exceptions import HTTPError, ConnectionError, Timeout


def simplify_research(query):
    query = query.lower()
    # Removing phrases inside brackets []
    query = re.sub(r"\[[^\[\]]*\]", "", query)
    # Removing 'Remastered year' pattern
    query = re.sub(r'((remastered|remaster) [0-9]+)+', "", query)
    query = re.sub(r'([0-9]+ (remastered|remaster))+', "", query)
    # Removing 'Remixed year' pattern
    query = re.sub(r'((remix|remixed) [0-9]+)+', "", query)
    query = re.sub(r'([0-9]+ (remix|remixed))+', "", query)

    # Removing useless words
    to_replace = ['single version', 'remastered', 'remaster', 'remix', 'remixed',
                  'version', 'deluxe', 'extended', '-', 'edition', ';', ':']
    for word in to_replace:
        query = query.replace(word, '')
    # Removing empty brackets
    query = query.replace("()", "")
    query = query.replace("[]", "")
    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def simplify_more_research(query):
    # ATTENTION! The use of this simplification of research is suggested only as last chance
    query = simplify_research(query)
    # Removing phrases inside brackets ()
    query = re.sub(r"\([^()]*\)", "", query)
    # Removing final spaces
    query = "".join(query.rstrip())
    return query


def verify_result(query, result):
    query, result = query.lower(), result.lower()
    if result.find('New Music Friday') != -1:
        return False
    for word in re.findall(r'\w+', query):
        if word in re.findall(r'\w+', result):
            return True
    return False


class Genius(object):
    def __init__(self):
        # ATTENTION! In order to do authentication with token by public Genius API,
        #            'GENIUS_TOKEN' env variable must be setted.
        token = os.environ['GENIUS_TOKEN']
        self.genius = lyricsgenius.Genius(token, response_format='html')
        # Turning on status messages
        self.genius.verbose = True
        # Removing section headers (e.g. [Chorus]) from lyrics when searching
        # self.genius.remove_section_headers = True
        # Skipping hits thought to be non-songs (e.g. track lists)
        self.genius.skip_non_songs = True
        # Excluding songs with these words in their title
        # self.genius.excluded_terms = ["(Remix)", "(Live)"]

    def get_artist(self, artist_name):
        print(f"Getting from Genius annotations about ARTIST: {artist_name} ...")
        try:
            searched_artist = self.genius.search_artist(
                artist_name=artist_name, max_songs=1, sort='popularity',
                per_page=1, get_full_info=False, allow_name_change=True)
            if not searched_artist or verify_result(artist_name, searched_artist.name) is False:
                artist_name = simplify_more_research(artist_name)
                searched_artist = self.genius.search_artist(
                    artist_name=artist_name, max_songs=1, sort='popularity',
                    per_page=1, get_full_info=False, allow_name_change=True)
                if not searched_artist or verify_result(artist_name, searched_artist.name) is False:
                    return None
            artist = self.genius.artist(artist_id=searched_artist.id)

            # Get Genius URL
            url = artist['artist']['url']
            # Get description
            try:
                description = artist['artist']['description']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get Akas
            try:
                alternate_names = artist['artist']['alternate_names']
            except (KeyError, ValueError, AttributeError):
                alternate_names = None

            return {'url': url,
                    'annotations': {'description': description, 'alternate_names': alternate_names}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_album(self, artist_name, album_name):
        # Album research semplification
        album_name = simplify_research(album_name)

        print(f"Getting from Genius annotations about ALBUM {album_name} by ARTIST {artist_name} ...")
        try:
            searched_album = self.genius.search_album(
                artist=artist_name, name=album_name, get_full_info=False)
            if not searched_album or verify_result(album_name, searched_album.name) is False:
                album_name = simplify_more_research(album_name)
                searched_album = self.genius.search_album(
                    artist=artist_name, name=album_name, get_full_info=False)
                if not searched_album or verify_result(album_name, searched_album.name) is False:
                    return None
            album = self.genius.album(album_id=searched_album.id)

            # Get Genius URL
            url = album['album']['url']
            # Get description
            try:
                description = album['album']['description_annotation']['annotations'][0]['body']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get producers, writers and labels names and links
            producers = []
            writers = []
            labels = []
            try:
                for sp in album['album']['song_performances']:
                    if sp['label'] == 'Producers':
                        for p in sp['artists']:
                            producers.append({'name': p['name'], 'url': p['url']})
                    if sp['label'] == 'Writers':
                        for w in sp['artists']:
                            writers.append({'name': w['name'], 'url': w['url']})
                    if sp['label'] == 'Label':
                        for l in sp['artists']:
                            labels.append({'name': l['name'], 'url': l['url']})
            except (KeyError, ValueError, AttributeError):
                writers = None
                producers = None
                labels = None

            return {'url': url,
                    'annotations': {'description': description, 'producers': producers, 'writers': writers, 'labels': labels}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None

    def get_track(self, artist_name, track_name):
        # Track research semplification
        track_name = simplify_research(track_name)

        print(f"Getting from Genius lyrics and annotations about TRACK {track_name} by ARTIST {artist_name} ...")
        try:
            searched_track = self.genius.search_song(
                artist=artist_name, title=track_name, get_full_info=False)
            if not searched_track or verify_result(track_name, searched_track.title) is False:
                track_name = simplify_more_research(track_name)
                searched_track = self.genius.search_song(
                    artist=artist_name, title=track_name, get_full_info=False)
                if not searched_track or verify_result(track_name, searched_track.title) is False:
                    return None
            track = self.genius.song(searched_track.id)

            # Get Genius URL
            url = track['song']['url']
            # Get lyrics
            lyrics = self.genius.lyrics(track['song']['id'])
            if lyrics:
                # Cleaning lyrics
                lyrics = re.sub(r"\d+EmbedShare URLCopyEmbedCopy", "", lyrics)
            # Get description
            try:
                description = track['song']['description_annotation']['annotations'][0]['body']['html']
            except (KeyError, ValueError, AttributeError):
                description = None
            # Get producers names and links
            producers = []
            try:
                for p in track['song']['producer_artists']:
                    producers.append({'name': p['name'], 'url': p['url']})
            except (KeyError, ValueError, AttributeError):
                producers = None
            # Get writers names and links
            writers = []
            try:
                for w in track['song']['writer_artists']:
                    writers.append({'name': w['name'], 'url': w['url']})
            except (KeyError, ValueError, AttributeError):
                writers = None
            # Get labels
            labels = []
            try:
                for cp in track['song']['custom_performances']:
                    if cp['label'] == 'Label':
                        for l in cp['artists']:
                            labels.append({'name': l['name'], 'url': l['url']})
            except (KeyError, ValueError, AttributeError):
                labels = None

            return {'url': url, 'lyrics': lyrics,
                    'annotations': {'description': description, 'producers': producers, 'writers': writers, 'labels': labels}}

        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            return None
