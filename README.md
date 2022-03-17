# SpotiNet

A statistical network analysis project of musical artist collaboration networks using Spotify's API. In this project, the following analyses were carried out:
 - Comparison of network statistics between electronic and rap musicians are carried out
 - Degree and strength distributions are compared and analyzed
 - Presence of power law is tested statistically following methods described by Clause et al. (2009)
 - Identified influential artists in each genre by Betweeness Centrality using Dijkstra's algorithm

## Collab Net module

The collab net module carries out snowball sampling of a user defined size from a source musician. The module relies on Spotify's API to sample. You must put your Spotify API developer keys in a separate file named `spotify_secret` before importing the module for use. The secret file should contain the following.

```
keys = {"SPOTIFY_CLIENT_ID":"your_client_id", 
        "SPOTIPY_CLIENT_SECRET":"your_secret_key",
        "SPOTIPY_REDIRECT_URI": "https://example.com"}
```
