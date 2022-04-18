import random
from collections import OrderedDict
from datetime import datetime
from time import strftime, gmtime
import os
import googlemaps
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# API Key should be secret
GMAPS_KEY = os.environ['PLACES_API']
gmaps = googlemaps.Client(key=GMAPS_KEY)



def main2():
    # Client Credentials should be secret
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],
                                                        client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],
                                                        # Same as in Spotify Dashboard
                                                        redirect_uri='http://localhost:9090',
                                                        scope='playlist-modify-public'))

    # Get origin and destination until Google Maps picks the correct one
    while True:
        origin = input("Please enter the start of your trip: ")
        destination = input("Please enter the destination of your trip: ")
        d = directions(origin, destination)
        origin_resolved, destination_resolved = resolve_origin_and_destination(d)
        if input(f"Did you mean from {origin_resolved} to {destination_resolved}? (y/n): ") == 'n':
            print("Please be more specific.")
        else:
            break

    # Create empty playlist in Spotify
    playlist_name = "Road2Music - " + origin + " to " + destination
    spotify.user_playlist_create(user=spotify.me()['id'], name=playlist_name)
    print(f"Creating playlist with the name {playlist_name} in your Spotify account.")
    # Get playlist id from previously created empty playlist by searching for the name within user's playlists
    playlist_id = search_playlist_id(spotify, playlist_name)

    # Calculate time in each state
    state_time = time_in_states_along_route(d)

    for i in range(0, len(state_time)):
        if i == 0:
            print(
                f"Your trip will go through {list(state_time.keys())[0]} for {strftime('%H:%M:%S', gmtime(list(state_time.values())[0]))}.")
        elif i == len(state_time) - 1:
            print(
                f"And finally through {list(state_time.keys())[i]} for {strftime('%H:%M:%S', gmtime(list(state_time.values())[i]))}.")
        else:
            print(
                f"Then through {list(state_time.keys())[i]} for {strftime('%H:%M:%S', gmtime(list(state_time.values())[i]))}.")

    # Add songs to empty playlist based on states
    add_songs(spotify, playlist_id, state_time)







def directions(origin, destination):
    now = datetime.now()
    directions_result = gmaps.directions(origin,
                                         destination,
                                         mode="driving",
                                         departure_time=now)
    return directions_result


def resolve_origin_and_destination(directions):
    origin = directions[0]['legs'][0]['start_address']
    # Pick end address from last leg since a route may have multiple legs
    destination = directions[0]['legs'][len(directions[0]['legs']) - 1]['end_address']
    return origin, destination


def time_in_states_along_route(directions):
    states = OrderedDict()
    legs = directions[0]['legs']

    duration_in_current_state_seconds = 0
    current_state = ""
    for leg in legs:
        steps = leg['steps']
        for step in steps:
            # Get name of state by coordinates
            start_state = gmaps.reverse_geocode(step['start_location'], result_type='administrative_area_level_1')
            end_state = gmaps.reverse_geocode(step['end_location'], result_type='administrative_area_level_1')
            # Save sum of duration of all steps when the state changes plus half the duration of the step that
            # crosses the state's border
            if start_state != end_state:
                states[start_state[0]['address_components'][0]['long_name']] = duration_in_current_state_seconds + \
                                                                               step['duration']['value'] / 2
                current_state = end_state[0]['address_components'][0]['long_name']
                duration_in_current_state_seconds = step['duration']['value'] / 2
            else:
                duration_in_current_state_seconds += step['duration']['value']
    # After the last state, there is no state change anymore, so save it explicitly
    states[current_state] = duration_in_current_state_seconds

    return states


def add_songs(spotify, playlist, time_in_states):
    song_counter = 0
    for state, time in time_in_states.items():
        songs = get_songs_by_state(state)
        time_left = time
        if len(songs) == 0:
            print(f"Skipping {state} since there are no songs in the database.")
        while time_left > 0 and len(songs) > 0:
            # Random pick and delete from song list, so no song is picked twice
            uri = random.choice(songs)
            songs.remove(uri)

            song = spotify.track(track_id=uri)
            spotify.playlist_add_items(playlist_id=playlist, items=[uri])

            song_counter += 1
            # Reduce time left in state by song length
            time_left -= song['duration_ms'] / 1000
    print(f"{song_counter} songs have been added to the playlist. Enjoy your trip!")


def search_playlist_id(spotify, name):
    playlists = spotify.current_user_playlists()
    for playlist in playlists["items"]:
        if playlist["name"] == name:
            return playlist["id"]


def get_songs_by_state(state):
    data = pd.read_excel('songs.xlsx')
    df = pd.DataFrame(data)
    # Drop NAs since column lengths differ
    songs = df[state].dropna()
    if songs.empty:
        return []
    return songs.values.tolist()


if __name__ == '__main__':
    main2()
