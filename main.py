import os
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import yt_dlp
import threading


def get_spotify_playlist_tracks(playlist_url, client_id, client_secret):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    results = sp.playlist_items(playlist_id)
    track_and_artist_names = [(item['track']['name'], item['track']['artists'][0]['name']) for item in results['items']]
    return track_and_artist_names


def get_spotify_track(track_url, client_id, client_secret):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    track_id = track_url.split('/')[-1].split('?')[0]
    result = sp.track(track_id)
    track_name = result['name']
    artist_name = result['artists'][0]['name']
    return track_name, artist_name


def search_youtube(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if result['result']:
        return result['result'][0]['link']
    return None


def print_spinner(message, delay=0.1):
    spinner = ['|', '/', '-', '\\']
    while not stop_spinner_event.is_set():
        for symbol in spinner:
            sys.stdout.write(f'\r{message} {symbol}')
            sys.stdout.flush()
            time.sleep(delay)


def download_youtube_video(video_url, output_path='.', progress_hook=None):
    global stop_spinner_event
    stop_spinner_event = threading.Event()

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            sys.stdout.write(f'\rDownloading... {percent:.2f}%')
            sys.stdout.flush()
        elif d['status'] == 'finished':
            stop_spinner_event.set()
            print('\nDownload completed.')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [progress_hook]
    }

    spinner_thread = threading.Thread(target=print_spinner, args=("Downloading...",))
    spinner_thread.start()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        file_name = ydl.prepare_filename(info_dict)
        base, ext = os.path.splitext(file_name)
        new_file = base + '.mp3'
        os.rename(file_name, new_file)
        spinner_thread.join()  # Ensure spinner thread finishes before returning
        return new_file


def download_spotify_playlist(playlist_url, client_id, client_secret):
    track_and_artist_names = get_spotify_playlist_tracks(playlist_url, client_id, client_secret)
    total_tracks = len(track_and_artist_names)
    downloaded_tracks = 0

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    for track_name, artist_name in track_and_artist_names:
        print(f"\nDownloading: {downloaded_tracks + 1}/{total_tracks} - {track_name} by {artist_name}")
        video_url = search_youtube(f"{track_name} {artist_name}")
        if video_url:
            download_youtube_video(video_url, 'downloads')
        else:
            print(f"Could not find: {track_name} by {artist_name} on YouTube")
        downloaded_tracks += 1
        print(f"Progress: {downloaded_tracks}/{total_tracks} tracks downloaded.")

    print('\nAll tracks downloaded.')


def download_spotify_track(track_url, client_id, client_secret):
    track_name, artist_name = get_spotify_track(track_url, client_id, client_secret)
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    print(f"\nDownloading: {track_name} by {artist_name}")
    video_url = search_youtube(f"{track_name} {artist_name}")
    if video_url:
        download_youtube_video(video_url, 'downloads')
    else:
        print(f"Could not find: {track_name} by {artist_name} on YouTube")
    print('\nDownload completed.')


def download_youtube_playlist(playlist_url):
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            sys.stdout.write(f'\rDownloading... {percent:.2f}%')
            sys.stdout.flush()
        elif d['status'] == 'finished':
            print('\nDownload completed.')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'quiet': True,
        'yesplaylist': True,
        'progress_hooks': [progress_hook]
    }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])


def download_youtube_video_single(video_url):
    download_youtube_video(video_url, 'downloads')


def main():
    print("Playlist Downloader")
    print("Select service:")
    print("1. Spotify")
    print("2. YouTube")

    service_choice = input("Enter choice (1 or 2): ").strip()

    if service_choice == '1':
        client_id = input("Enter Spotify Client ID: ").strip()
        client_secret = input("Enter Spotify Client Secret: ").strip()
        if not client_id or not client_secret:
            print("Error: Please provide both Client ID and Client Secret.")
            return

        print("Enter Spotify link (playlist or track):")
        link = input("URL: ").strip()
        if not link:
            print("Error: URL cannot be empty.")
            return

        if "playlist" in link:
            download_spotify_playlist(link, client_id, client_secret)
        elif "track" in link:
            download_spotify_track(link, client_id, client_secret)
        else:
            print("Error: Invalid Spotify URL.")

    elif service_choice == '2':
        print("Enter YouTube link (playlist or video):")
        link = input("URL: ").strip()
        if not link:
            print("Error: URL cannot be empty.")
            return

        if "playlist" in link:
            download_youtube_playlist(link)
        elif "youtube.com" in link or "youtu.be" in link:
            download_youtube_video_single(link)
        else:
            print("Error: Invalid YouTube URL.")

    else:
        print("Error: Invalid choice.")


if __name__ == "__main__":
    # Redirect stderr to suppress yt_dlp warnings
    sys.stderr = open(os.devnull, 'w')
    main()
    # Restore stderr
    sys.stderr = sys.__stderr__
