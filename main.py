import spotipy
import spotipy.util as util
from credentials import USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from bs4 import BeautifulSoup
import requests
import random
import psycopg2
from psycopg2 import sql


class Album:
    def __init__(self, artist, album_name, url):
        self.artist = artist
        self.album_name = album_name
        self.url = url

    def __str__(self):
        return f"{self.artist} - {self.album_name} // {self.url}"


def database_exists():
    conn = psycopg2.connect(dbname="postgres", user="postgres")
    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT datname FROM pg_catalog.pg_database WHERE datname='data')")
    test = cur.fetchone()
    cur.close()
    conn.close()
    return test[0]


def create_database():
    conn = psycopg2.connect(dbname="postgres", user="postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("data")))
    cur.close()
    conn.close()


def create_table():
    conn = psycopg2.connect(dbname="data", user="postgres")
    cur = conn.cursor()
    cur.execute("CREATE TABLE artists (id serial PRIMARY KEY, name varchar, artist_id varchar, genre varchar);")
    conn.commit()
    cur.close()
    conn.close()


def add_artist_to_db(artist, artist_id, genre):
    conn = psycopg2.connect(dbname="data", user="postgres")
    cur = conn.cursor()
    cur.execute("INSERT INTO artists (name, artist_id, genre) VALUES (%s, %s, %s)", (artist, artist_id, genre))
    conn.commit()
    cur.close()
    conn.close()


def get_artist_id_from_name(artist):
    conn = psycopg2.connect(dbname="data", user="postgres")
    cur = conn.cursor()
    output = cur.execute("SELECT artist_id FROM artists WHERE artist = (%s)", (artist, ))
    conn.commit()
    cur.close()
    conn.close()
    return output


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


def get_genre_from_database(genre):
    conn = psycopg2.connect(dbname="data", user="postgres")
    cur = conn.cursor()
    cur.execute('SELECT artist_id FROM artists WHERE genre=%s;', (genre, ))
    output_data = cur.fetchall()
    output = [x[0] for x in output_data]
    conn.commit()
    cur.close()
    conn.close()
    return output

def get_songs_from_albums(spotify, albums):
    output_songs = []
    for album in albums:
        result = spotify.album_tracks(album)
        output_songs.append(result['items'][0]['id'])

    return output_songs


def get_artist_id_from_name(artist, spotify):
    data = spotify.search(q=f"artist: {artist}", type="artist")
    search_result = data['artists']['items']
    genre_filter = {"art rock",
                    "canterbury scene",
                    "zeuhl",
                    "black metal",
                    'technical brutal death metal',
                    'technical death metal'}

    partial_filter = ["prog", "avant-garde"]
    for item in search_result:
        if [x for x in item['genres'] if [y for y in partial_filter if y in x]] or not set(genre_filter).isdisjoint(
                set(item['genres'])):
            return item['id']
    return False


def get_lists_of_artists_from_genre_page(genre):
    list_of_artists = []
    output_artists = []
    html = requests.get(f"http://www.progarchives.com/subgenre.asp?style={genre}")
    soup = BeautifulSoup(html.text, "html.parser")
    table_0 = soup.find_all("td", {"class": "cls_tdDisco0"})
    table_1 = soup.find_all("td", {"class": "cls_tdDisco1"})
    for item in table_0:
        list_of_artists.append(item)

    for item in table_1:
        list_of_artists.append(item)

    for i in range(0, len(list_of_artists), 2):
        output_artists.append(list_of_artists[i].text)

    return output_artists


def clear_playlist(spotify):
    playlist_track_ids = []
    playlist = spotify.user_playlist(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX")
    playlist_tracks = playlist['tracks']['items']
    for track in playlist_tracks:
        playlist_track_ids.append(track['track']['id'])
    spotify.user_playlist_remove_all_occurrences_of_tracks(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX",
                                                           tracks=playlist_track_ids)


def add_list_of_songs_to_playlist(spotify, songs, genre):
    playlist_id = "4NDOGu4SwODtZIgkG205yX"
    clear_playlist(spotify)
    spotify.user_playlist_change_details(user=USERNAME, playlist_id=playlist_id, public=True,
                                         description=f"Weekly Prog // Currently: {genre}")
    spotify.user_playlist_add_tracks(USERNAME, playlist_id, songs)


def get_artist_albums(spotify, artist_id):
    results = spotify.artist_albums(artist_id, album_type="album")
    albums = results['items']
    output = [x['id'] for x in albums]
    return output


def populate_database():
    if not database_exists():
        create_database()
        create_table()

    with open("genres", "r") as f:
        genres = f.readlines()

    formatted_genres = []
    for i in range(len(genres) - 1):
        item = genres[i].split(",")
        formatted_genres.append((item[0], item[1].strip()))

    for genre in formatted_genres:
        genre_id = genre[0]
        genre_name = genre[1]
        print(genre_name)
        artists = get_lists_of_artists_from_genre_page(genre_id)
        for artist in artists:
            artist_id = get_artist_id_from_name(artist, sp)
            if artist_id:
                add_artist_to_db(artist, artist_id, genre_name)


def make_random_genre_playlist(spotify):
    playlist_songs = []
    if not database_exists():
        create_database()
        create_table()

    with open("genres", "r") as f:
        genres = f.readlines()

    formatted_genres = []
    for i in range(len(genres) - 1):
        item = genres[i].split(",")
        formatted_genres.append((item[0], item[1].strip()))


    genre = random.choice(formatted_genres)
    genre_id = genre[0]
    genre_name = genre[1].strip()
    artist_list = get_genre_from_database(genre_name)
    random.shuffle(artist_list)
    for artist in artist_list:
        albums = get_artist_albums(spotify, artist)
        random.shuffle(albums)
        album_songs = get_songs_from_albums(spotify, albums)
        if len(album_songs) == 0:
            continue
        random.shuffle(album_songs)
        playlist_songs.append(album_songs[0])
        if len(playlist_songs) == 30:
            return playlist_songs, genre_name



if __name__ == "__main__":
    SCOPE = "playlist-modify-public"
    CACHE = ".spotipyoauthcache"
    token = util.prompt_for_user_token(USERNAME, SCOPE,
                                       client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)

    songs, genre = make_random_genre_playlist(sp)
    add_list_of_songs_to_playlist(sp, songs, genre)
