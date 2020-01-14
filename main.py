import spotipy
import spotipy.util as util
from credentials import USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from bs4 import BeautifulSoup
import requests

def get_prog_songs():
    base_url = "http://www.progarchives.com/top-prog-albums.asp?s"
    subgenre = "subgenres=43" + "&"
    album_types = "albumtypes=1" + "&"
    years = "years=" + "&"
    countries = "countries=" + "&"
    minratings = "minratings=" + "&"
    maxratings = "maxratings=" + "&"
    minavgratings = "minavgratings=0" + "&"
    max_results = "maxresults=250" + "&"
    #TODO: create request url out of above

if __name__ == "__main__":

    SCOPE = "playlist-modify-public"
    CACHE = ".spotipyoauthcache"

    token = util.prompt_for_user_token(USERNAME, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)
        playlist = sp.user_playlist(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX")
        print(playlist)




