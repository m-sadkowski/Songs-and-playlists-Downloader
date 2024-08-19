import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import yt_dlp
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox, QComboBox, \
    QFormLayout, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import platform
import subprocess


class DownloadThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, download_func, *args, **kwargs):
        super().__init__()
        self.download_func = download_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.download_func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create widgets
        self.service_combo = QComboBox()
        self.service_combo.addItems(['Select Service', 'Spotify', 'YouTube'])

        self.url_input = QLineEdit()
        self.client_id_input = QLineEdit()
        self.client_secret_input = QLineEdit()
        self.download_button = QPushButton('Download')
        self.open_folder_button = QPushButton('Open Download Folder')
        self.progress_label = QLabel('')

        # Layout setup
        form_layout = QFormLayout()
        form_layout.addRow(QLabel('Service:'), self.service_combo)
        form_layout.addRow(QLabel('URL:'), self.url_input)
        form_layout.addRow(QLabel('Spotify Client ID:'), self.client_id_input)
        form_layout.addRow(QLabel('Spotify Client Secret:'), self.client_secret_input)

        # Adjust visibility of client id and secret
        self.client_id_input.setVisible(False)
        self.client_secret_input.setVisible(False)

        # Center the buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()

        # Combine all layouts
        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addLayout(button_layout)
        vbox.addWidget(self.progress_label)

        self.setLayout(vbox)

        # Connect signals
        self.download_button.clicked.connect(self.on_download_click)
        self.open_folder_button.clicked.connect(self.open_download_folder)
        self.service_combo.currentIndexChanged.connect(self.on_service_change)

        # Window settings
        self.setWindowTitle('Music Downloader')
        self.setGeometry(300, 300, 400, 250)

        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit, QComboBox, QPushButton {
                background-color: #4C4C4C;
                color: #FFFFFF;
                border: 1px solid #7F7F7F;
                padding: 5px;
            }
            QPushButton {
                background-color: #3A3A3A;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5C5C5C;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #009688;
            }
            """)

    def on_service_change(self):
        service = self.service_combo.currentText()
        if service == 'Spotify':
            self.client_id_input.setVisible(True)
            self.client_secret_input.setVisible(True)
        else:
            self.client_id_input.setVisible(False)
            self.client_secret_input.setVisible(False)

    def on_download_click(self):
        service = self.service_combo.currentText()
        url = self.url_input.text().strip()
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()

        if not url:
            QMessageBox.warning(self, 'Error', 'URL cannot be empty.')
            return

        if service == 'Spotify':
            if not client_id or not client_secret:
                QMessageBox.warning(self, 'Error', 'Please provide both Client ID and Client Secret.')
                return
            self.download_button.setEnabled(False)
            self.thread = DownloadThread(self.download_spotify, url, client_id, client_secret)
            self.thread.finished.connect(self.on_finished)
            self.progress_label.setText('Downloading...')
            self.thread.start()
        elif service == 'YouTube':
            self.download_button.setEnabled(False)
            self.thread = DownloadThread(self.download_youtube, url)
            self.thread.finished.connect(self.on_finished)
            self.progress_label.setText('Downloading...')
            self.thread.start()
        else:
            QMessageBox.warning(self, 'Error', 'Please select a valid service.')

    def download_spotify(self, url, client_id, client_secret):
        def get_spotify_track_info(track_url, client_id, client_secret):
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
            track_id = track_url.split('/')[-1].split('?')[0]
            result = sp.track(track_id)
            return result['name'], result['artists'][0]['name']

        def get_spotify_playlist_tracks(playlist_url, client_id, client_secret):
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            results = sp.playlist_items(playlist_id)
            track_and_artist_names = [(item['track']['name'], item['track']['artists'][0]['name']) for item in
                                      results['items']]
            return track_and_artist_names

        def search_youtube(query):
            videos_search = VideosSearch(query, limit=1)
            result = videos_search.result()
            if result['result']:
                return result['result'][0]['link']
            return None

        def download_youtube_video(video_url, output_path='.'):
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'noplaylist': True
            }

            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                file_name = ydl.prepare_filename(info_dict)
                base, ext = os.path.splitext(file_name)
                new_file = base + '.mp3'
                os.rename(file_name, new_file)
                return f"Downloaded to {new_file}"

        def download_spotify_track(track_url, client_id, client_secret):
            track_name, artist_name = get_spotify_track_info(track_url, client_id, client_secret)
            video_url = search_youtube(f"{track_name} {artist_name}")
            if video_url:
                return download_youtube_video(video_url, 'downloads')
            else:
                return f"Could not find: {track_name} by {artist_name} on YouTube"

        def download_spotify_playlist(playlist_url, client_id, client_secret):
            track_and_artist_names = get_spotify_playlist_tracks(playlist_url, client_id, client_secret)

            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            for track_name, artist_name in track_and_artist_names:
                video_url = search_youtube(f"{track_name} {artist_name}")
                if video_url:
                    download_youtube_video(video_url, 'downloads')
                else:
                    print(f"Could not find: {track_name} by {artist_name} on YouTube")

            return 'All tracks downloaded.'

        if 'track' in url:
            return download_spotify_track(url, client_id, client_secret)
        elif 'playlist' in url:
            return download_spotify_playlist(url, client_id, client_secret)
        else:
            return "Invalid Spotify URL"

    def download_youtube(self, url):
        def download_youtube_video(video_url, output_path='.'):
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'noplaylist': True
            }

            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                file_name = ydl.prepare_filename(info_dict)
                base, ext = os.path.splitext(file_name)
                new_file = base + '.mp3'
                os.rename(file_name, new_file)
                return f"Downloaded to {new_file}"

        return download_youtube_video(url, 'downloads')

    def open_download_folder(self):
        if platform.system() == 'Windows':
            subprocess.Popen(f'explorer {os.path.abspath("downloads")}')
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', os.path.abspath("downloads")])
        else:  # Linux
            subprocess.Popen(['xdg-open', os.path.abspath("downloads")])

    def on_finished(self, message):
        QMessageBox.information(self, 'Finished', message)
        self.progress_label.setText('Download complete.')
        self.download_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
