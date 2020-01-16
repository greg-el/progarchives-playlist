import spotipy
import spotipy.util as util
from credentials import USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from bs4 import BeautifulSoup
import requests
import re
import random

class Album:
    def __init__(self, artist, album_name, url):
        self.artist = artist
        self.album_name = album_name
        self.url = url

    def __str__(self):
        return f"{self.artist} - {self.album_name} // {self.url}"


def get_prog_songs(url):
    output = []
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    album_table = soup.find_all("table")[1]
    albums = album_table.find_all("tr")
    for album in albums:
        delimited_album_html = album.find_all("td")[3].contents
        album_url = album.find_all("a", href=True)[0]["href"]
        album_name = delimited_album_html[0].text
        artist_name = delimited_album_html[2].text
        output.append(Album(artist_name, album_name, album_url))

    return output


def get_album_songs_from_url(album_url):
    output = []
    album_html = requests.get(f"http://www.progarchives.com/{album_url}")
    album_soup = BeautifulSoup(album_html.text, "html.parser")
    test = album_soup.find_all("td")[1].contents[7].contents
    song_regex = re.compile(r"^\d{1,2}. (.*) ")
    for song in test:
        song_bytes_string = song.encode("utf-8")
        song_string = song_bytes_string.decode("utf-8")
        song_regex_match = song_regex.match(song_string)
        if song_regex_match and song_string[0].isdigit():
            output.append(song_regex_match.group(1))

    return output


def get_songs_from_albums(spotify):
    output_songs = []
    artists_added = []
    if token:
        for album in album_list:
            test = spotify.search(q=f"artist:{album.artist} album:{album.album_name}", type="album", limit=20)
            result = test['albums']['items']
            for item in result:
                try:
                    result_artist_name = item['artists'][0]['name']
                    if result_artist_name == album.artist and album.artist not in artists_added:
                        artists_added.append(album.artist)
                        result_uri = item['uri']
                        spotify_album = spotify.album_tracks(result_uri)
                        album_songs = spotify_album['items']
                        choice = random.choice(album_songs)
                        print(album_songs)
                        output_songs.append(choice['id'])
                        if len(output_songs) > 30:
                            return output_songs
                        break
                except TypeError:
                    print("Run out of songs")
                    return output_songs


def clear_playlist(spotify):
    playlist_track_ids = []
    playlist = spotify.user_playlist(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX")
    playlist_tracks = playlist['tracks']['items']
    for track in playlist_tracks:
        playlist_track_ids.append(track['track']['id'])
    spotify.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX", tracks=playlist_track_ids)


if __name__ == "__main__":
    SCOPE = "playlist-modify-public"
    CACHE = ".spotipyoauthcache"
    token = util.prompt_for_user_token(USERNAME, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)
    list_of_artists = []
    output_artists = []
    html = requests.get("http://www.progarchives.com/subgenre.asp?style=12")
    soup = BeautifulSoup(html.text, "html.parser")
    table_0 = soup.find_all("td", {"class": "cls_tdDisco0"})
    table_1 = soup.find_all("td", {"class": "cls_tdDisco1"})
    for item in table_0:
        list_of_artists.append(item)

    for item in table_1:
        list_of_artists.append(item)

    for i in range(0, len(list_of_artists), 2):
        output_artists.append((list_of_artists[i], list_of_artists[i].find_all("a", href=True)[0]["href"]))

    artist_prog_archives_url = output_artists[36][1]
    artist_page_html = requests.get(f"http://www.progarchives.com/{artist_prog_archives_url}")
    artist_page_soup = BeautifulSoup(artist_page_html.text, "html.parser")
    table = artist_page_soup.find_all("div", {"id": "main"})
    print(table[0].find_all("div", {"style": "background-color:#fff;margin:25px 0px 0px 0px;"}))
    #TODO: fix this





    #with open("playlist-urls", "r") as f:
    #    urls = f.readlines()

    #url_choice = random.choice(urls)
    #url = url_choice.split(",")[1]
    #playlist_description = url_choice.split(",")[0]
    #album_list = get_prog_songs(url)
    #random.shuffle(album_list)

    #playlist_id = "4NDOGu4SwODtZIgkG205yX"
    #output_songs = get_songs_from_albums(sp)
    #clear_playlist(sp)
    #sp.user_playlist_change_details(user=USERNAME, playlist_id=playlist_id, public=True, description=f"Weekly Prog // Currently: {playlist_description}")
    #sp.user_playlist_add_tracks(USERNAME, playlist_id, output_songs)










