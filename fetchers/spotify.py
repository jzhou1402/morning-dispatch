import os
from collections import Counter

def fetch():
    client_id     = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri  = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
    if not client_id or not client_secret:
        return None

    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-read-recently-played",
        cache_path=".spotify_token_cache",
    ))

    recent = sp.current_user_recently_played(limit=20)
    items  = recent.get("items", [])

    tracks  = [i["track"]["name"]             for i in items]
    artists = [i["track"]["artists"][0]["name"] for i in items]

    top_track_name = Counter(tracks).most_common(1)[0][0] if tracks else ""
    top_idx        = tracks.index(top_track_name)         if tracks else 0

    return {
        "top_track":     top_track_name,
        "top_artist":    artists[top_idx] if artists else "",
        "recent_tracks": list(dict.fromkeys(tracks))[:5],
        "total_played":  len(items),
    }
