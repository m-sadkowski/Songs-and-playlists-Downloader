# Songs and Playlists Downloader

## Overview

This application allows users to download songs and playlists from Spotify and YouTube. The graphical user interface (GUI) is built with PyQt5, and the program supports downloading songs from Spotify playlists and individual YouTube videos, converting them to MP3 format.

## Features

- **Service Selection:** Choose between Spotify and YouTube for downloading.
- **Playlist Handling:** Fetch and download all tracks from a Spotify playlist.
- **YouTube Integration:** Download and convert YouTube videos to MP3.
- **Threading:** Asynchronous downloading using threads to keep the UI responsive.
- **User-Friendly GUI:** Built with PyQt5 for a simple and intuitive interface.

## Prerequisites

- Python 3.x
- PyQt5
- spotipy
- youtubesearchpython
- yt-dlp

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/m-sadkowski/Songs-and-playlists-Downloader.git
   cd Songs-and-playlists-Downloader
   ```

2. **Install Required Packages:**

   You can install the required packages using `pip`. Make sure you are in the project directory and run:

   ```bash
   pip install PyQt5 spotipy youtubesearchpython yt-dlp
   ```

## Usage

1. **Run the Application:**

   Execute the script using Python:

   ```bash
   python main.py
   ```

2. **Interface Overview:**

   - **Service Selection:** Choose between 'Spotify' and 'YouTube'.
   - **URL Input:** Enter the URL of the playlist (for Spotify) or video (for YouTube).
   - **Spotify Credentials:** Provide Spotify Client ID and Secret if downloading from Spotify.
   - **Download Button:** Click to start the download process.
   - **Progress Label:** Displays the status of the download.

3. **Download Process:**

   - **Spotify:**
     - If the URL is a playlist, the application will download each track from the playlist.
     - Requires Spotify Client ID and Secret for authentication.
     - Tracks are searched on YouTube and then downloaded.
   - **YouTube:**
     - Downloads the video directly and converts it to MP3 format.

## Code Details

### Main Components

- **`DownloadThread`**: A QThread subclass that handles downloading in the background.
- **`App`**: The main PyQt5 application window with GUI elements for user interaction.
- **`download_spotify`**: Downloads songs from Spotify playlists.
- **`download_youtube`**: Downloads and converts YouTube videos to MP3.

### Functions

- **`get_spotify_playlist_tracks`**: Retrieves track names and artists from a Spotify playlist.
- **`search_youtube`**: Searches for YouTube videos matching a query.
- **`download_youtube_video`**: Downloads a YouTube video and converts it to MP3.
- **`download_spotify_playlist`**: Downloads all tracks from a Spotify playlist.
- **`on_finished`**: Updates the UI when a download completes.

## Example Output

When a download is completed, a message box will show the status:

```
Finished
Downloaded to downloads/TrackName.mp3
```

## Notes

- Ensure you have valid Spotify credentials if downloading from Spotify.
- The 'downloads' directory will be created if it doesn't exist.
- The application might require access to network resources for downloading and converting files.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to contribute by submitting issues or pull requests to improve the functionality or fix bugs.

## Contact

For any questions or support, please contact [msadkowski000@gmail.com](mailto:msadkowski000@gmail.com).
