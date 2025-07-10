import requests, os, csv, base64, yt_dlp, imageio_ffmpeg
from dotenv import load_dotenv

"""
fetch token using spotify api
use token to get list of songs from playlist using spotify api
search song names on youtube and get youtube id using youtube api
download audio of this youtube id using yt-dlp api
"""

def config():
    load_dotenv()
    return [
        os.getenv("SPOTIFY_CLIENT_ID"),
        os.getenv("SPOTIFY_CLIENT_SECRET"),
        os.getenv("YOUTUBE_API_KEY"),
    ]

def get_token(spotify_client_id, spotify_client_secret):
    auth_str = f"{spotify_client_id}:{spotify_client_secret}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    res = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    try: res_json = res.json()
    except Exception as e:
        print(e)
        return
    if res.status_code != 200:
        print("couldnt get token:", res.status_code, res_json)
        return
    # print(res_json["access_token"])
    return res_json["access_token"]

def extract_playlist_id(playlist_url):
    return playlist_url.replace("https://open.spotify.com/playlist/", "")

def get_songs_from_playlist(playlist_id, token):
    songs = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    while url:
        res = requests.get(url=url, headers=headers)
        try:
            res_json = res.json()
        except Exception as e:
            return [False, e]
        if res.status_code != 200:
            return [False, f"couldn't get songs: {res.status_code} {res_json}"]
        for item in res_json["items"]:
            if item["track"]:
                songs.append({
                    "name": item["track"]["name"],
                    "id": item["track"]["id"],
                    "artist": item["track"]["artists"][0]["name"]
                })
        url = res_json.get("next")
        # print songs
    return [True, songs]

def get_playlist_name(playlist_id, token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    res = requests.get(url=url, headers=headers)
    try: res_json = res.json()
    except Exception as e: return [False, e]
    if res.status_code != 200:
        error_msg = f"couldnt get playlist name: {res.status_code} {res_json}"
        return [False, error_msg]
    playlist_name = res_json["name"]
    # print(playlist_name)
    return [True, playlist_name]

def get_yt_video_id(song_name, yt_api_key):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": song_name,
        "type": "video",
        "maxResults": 1,
        "key": yt_api_key,
    }
    res = requests.get(url=url, params=params)
    try: res_json = res.json()
    except Exception as e:
        error_msg = f"couldnt parse json: {res.status_code} {res_json}"
        return [False, error_msg]
    if res.status_code != 200:
        error_msg = f"couldnt get song ids: {res.status_code} {res_json}"
        return [False, error_msg]
    
    # getting video id from response
    items = res_json.get("items", [])
    if not items:
        return [False, "no search results"]
    video_id = items[0].get("id", {}).get("videoId")
    if not video_id:
        return [False, f"no videoId in item: {items[0]}"]
    
    # print(video_id)
    return [True, video_id]

def download_yt_audio(url, output_dir, ffmpeg_path):
    os.makedirs(output_dir, exist_ok=True)
    yt_dlp_opts = {
        'ffmpeg_location': ffmpeg_path,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': False,
        'noplaylist': True
    }
    try:
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([url])
            return [True, ""]
    except Exception as e:
        return [False, e]

if __name__ == "__main__":
    spotify_client_id, spotify_client_secret, yt_api_key = config()
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    token = get_token(spotify_client_id, spotify_client_secret) # spotify api token
    spotify_playlist_id = extract_playlist_id(input("Enter playlist url: "))
    playlist_name_ok, playlist_name = get_playlist_name(spotify_playlist_id, token)
    output_dir = f"{playlist_name} (downloaded)"

    # performing checks
    if not playlist_name_ok:
        print("couldnt fetch playlist name")
    if token is None:
        print("couldnt fetch token")
    songs_success, songs = get_songs_from_playlist(spotify_playlist_id, token)
    if not songs_success:
        print("failed to fetch playlist data from spotify api")
        exit()

    with open("logs.csv", "w", newline="", encoding="utf-8") as file:
        # (encoding for special characters in song names)
        writer = csv.writer(file)
        writer.writerow(["sr. no.", "song_name", "song_id", "download_success", "error_msg"])

        print(f"Downloading {len(songs)} songs from playlist: {playlist_name}")
        for idx, song in enumerate(songs, start=1):
            # downloading songs and updating logs here
            song_name = song["name"]
            song_id = song["id"]
            song_artist = song["artist"]
            print(f"[{idx}/{len(songs)}] Downloading: {song_name} by {song_artist}")
            yt_id_success, yt_id = get_yt_video_id(f"{song_name} {song_artist}", yt_api_key)
            if not yt_id_success:
                writer.writerow([idx, song_name, song_id, yt_id_success, yt_id])
                continue
            url = f"https://www.youtube.com/watch?v={yt_id}"
            download_success, download_msg = download_yt_audio(url, output_dir, ffmpeg_path)
            writer.writerow([idx, song_name, song_id, download_success, download_msg])
