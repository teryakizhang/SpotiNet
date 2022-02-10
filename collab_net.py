import json
import pickle as p
from collections import Counter
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from spotify_secret import keys

SPOTIFY_CLIENT_ID = keys["SPOTIFY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = keys['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = keys['SPOTIPY_REDIRECT_URI']


auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                        client_secret=SPOTIPY_CLIENT_SECRET,
                                        requests_timeout=120)


class collabNet:

    def __init__(self, start_id, limit=50, 
                save_attr=True, attr_filename='artist_attr.json', 
                save_collabs=True, collabs_filename='collabs.csv'):
        sp = spotipy.Spotify(auth_manager=auth_manager)
        self.limit = limit
        self.seen = list()
        self.unseen = list()
        self.unseen.append(start_id)
        self.albums = list()
        self.seen_name = list()
        self.seen_artists_uri = set()
        self.seen_tracks = set()
        self.collabs = list()
        self.artist_attr = dict()
        self.weighted_edge_list = list()

        i = 1
        for uri in self.unseen:
            if uri in self.seen:
                continue

            try:
                results = sp.artist_albums(uri, album_type=['album', 'single'])
            except:
                self.unseen.remove(uri)
                continue

            artist_name = sp.artist(uri)['name']
            print(f"{i}. currently on: {artist_name}")
            self.seen_name.append(artist_name)
            i += 1

            simp_albums = results['items']
            while results['next']:
                results = sp.next(results)
                # print(results[items])
                simp_albums.extend(results['items'])

            album_uris = []
            for album in simp_albums:
                album_uris.append(album['uri'].replace("spotify:album:", ''))

            n = 5
            album_uri_chunks = [album_uris[i:i + n]
                                for i in range(0, len(album_uris), n)]

            for chunk in album_uri_chunks:
                self.albums.extend(sp.albums(chunk)['albums'])

            tracks = list()
            for album in self.albums:
                if album == None:
                    continue
                else:
                    tracks.extend(album['tracks']['items'])

            for track in tracks:
                artists = track['artists']
                track_name = track['name']
                if track_name in self.seen_tracks:
                    continue

                track_artists = [art['name'] for art in artists]
                track_collabs = list(combinations(track_artists, 2))
                self.collabs.extend(track_collabs)
                self.seen_tracks.add(track_name)

                for art in artists:
                    collab_uri = art['uri'].replace("spotify:artist:", '')
                    self.seen_artists_uri.add(collab_uri)

                    if (collab_uri == uri or
                        collab_uri in self.seen):
                        continue
                    else:

                        self.unseen.append(collab_uri)

            self.seen.append(uri)
            self.unseen.remove(uri)
            if len(self.unseen) < 1 or len(self.seen) >= self.limit:
                break
            else:
                continue

        
        print("Getting artists attributes...")
        n = 50
        collab_artist_uris = list(self.seen_artists_uri)
        artist_uri_chunks = [collab_artist_uris[i:i + n]
                                 for i in range(0, len(collab_artist_uris), n)]
       
        collab_artists = list()
        for artist_uri_chunk in artist_uri_chunks:
            track_artists = sp.artists(artist_uri_chunk)['artists']
            collab_artists.extend(track_artists)

        artist_attr_temp = {art['name']: {'followers': art['followers']['total'],
                                            'popularity': art['popularity'],
                                            'genres': art['genres']} for art in collab_artists}
        self.artist_attr.update(artist_attr_temp)
        self.make_edge_list()
        print('Done!')

        if save_attr == True:
            self.save_attr_json(attr_filename)
        if save_collabs == True:
            self.save_collab_csv(collabs_filename)
            

    def make_edge_list(self):
        collab_counts = Counter(self.collabs)

        for count in collab_counts:
            self.weighted_edge_list.append(count + (collab_counts[count], ))


    def save_attr_json(self, filename='artist_attr.json'):
        with open(filename, 'w') as f:
            json.dump(self.artist_attr, f)
        print('Artist attribute saved as JSON')


    def save_collab_csv(self, filename='collabs.csv'):
        column_names = ['artist', 'collab', 'weight']

        data = self.weighted_edge_list

        collab_df = pd.DataFrame(data, columns=column_names)
        collab_df.to_csv(filename)

        print("Collaborations saved to CSV")



# drake = "3TVXtAsR1Inumwj472S9r4"
# # deadmau5 = "2CIMQHirSU0MQqyYHq0eOx"

# collab_net = collabNet(drake, limit=2)

# print('done')
