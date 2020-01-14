import spotipy
import spotipy.util as util
from spotipy import oauth2
from credentials import USERNAME, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

if __name__ == "__main__":

    SCOPE = "playlist-modify-public"
    CACHE = ".spotipyoauthcache"

    token = util.prompt_for_user_token(USERNAME, SCOPE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

    if token:
        sp = spotipy.Spotify(auth=token)
        playlist = sp.user_playlist(user=USERNAME, playlist_id="4NDOGu4SwODtZIgkG205yX")
        print(playlist)




