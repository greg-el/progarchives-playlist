import spotipy
import spotipy.util as util
from credentials import USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from bs4 import BeautifulSoup
import requests
import re
import random
import json

class Album:
    def __init__(self, artist, album_name, url):
        self.artist = artist
        self.album_name = album_name
        self.url = url

    def __str__(self):
        return f"{self.artist} - {self.album_name} // {self.url}"


def get_prog_songs():
    output = []
    with open("playlist-urls", "r") as f:
        urls = f.readlines()

    url_choice = random.choice(urls)

    url = url_choice.split(",")[1]
    print(url_choice.split(",")[0])
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


if __name__ == "__main__":
    album_list = get_prog_songs()
    random.shuffle(album_list)
    SCOPE = "playlist-modify-public"
    CACHE = ".spotipyoauthcache"
    token = util.prompt_for_user_token(USERNAME, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    if token:
        sp = spotipy.Spotify(auth=token)
        playlist = sp.user_playlist(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX")

        print(f"album: {album_list[1].album_name}  artist:{album_list[1].artist}")
        try:
            test = sp.search(q="album:" + album_list[1].album_name, type="album", limit=1)
        except IndexError:
            print("Album not on Spotify")
            exit(1)

        result = test['albums']['items'][0]
        result_artist_name = result['artists'][0]['name']
        if result_artist_name == album_list[1].artist:
            result_uri = result['uri']
            spotify_album = sp.album_tracks(result_uri)
            for item in spotify_album['items']:
                print(item)







