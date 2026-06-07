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

    # pair each play as (track_name, artist_name)
    plays = [
        (i["track"]["name"], i["track"]["artists"][0]["name"])
        for i in items
    ]

    if not plays:
        return None

    # most played track (with its correct artist)
    track_counts = Counter(name for name, _ in plays)
    top_track_name = track_counts.most_common(1)[0][0]
    top_artist = next(artist for name, artist in plays if name == top_track_name)

    # 5 most recently played unique tracks
    seen = set()
    recent_tracks = []
    for name, _ in plays:
        if name not in seen:
            seen.add(name)
            recent_tracks.append(name)
        if len(recent_tracks) == 5:
            break

    return {
        "top_track":     top_track_name,
        "top_artist":    top_artist,
        "recent_tracks": recent_tracks,
        "total_played":  len(items),
    }
