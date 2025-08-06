# SpotifyPlaylistDownloader

This is a Python-based tool that automatically downloads all the songs from a given Spotify playlist as MP3 files by:<br>
✅ Fetching songs from Spotify API<br>
✅ Searching YouTube for each song<br>
✅ Downloading the best matching audio using yt-dlp<br>
✅ Converting and saving audio as .mp3 using ffmpeg<br>
✅ Logging download status in a CSV file<br>
<br>

## 🧠 What It Does
- Accepts a Spotify playlist URL from the user
- Uses Spotify API to fetch all track names and artists
- Uses `YouTube Data API` to search for matching videos
- Uses `yt-dlp` to download and convert audio from `webm` to `MP3`
- Logs all download results (success/failure + error messages)
- Supports playlists with any number of tracks
<br>

## 🚀 Usage

### 1. 🔧 Install Dependencies
```bash
pip install -r packages.txt
```

### 2. Ensure your .env file contains the following:
```ini
SPOTIFY_CLIENT_ID       = xxx
SPOTIFY_CLIENT_SECRET   = xxx
YOUTUBE_API_KEY         = xxx
```
<br>

## 📝 Notes
- Only the first matching YouTube video's audio is downloaded for each song
- Works best for playlists with popular tracks
- YouTube rate limits may apply on large playlists
<br>