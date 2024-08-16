import os
import time
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from utils import get_download_folder, progress_hook

class Downloader:
    def __init__(self, gui):
        self.stop_download = False
        self.gui = gui
    
    def download_video(self, url, selected_resolution_text):
        self.stop_download = False
        download_folder = get_download_folder()
        ydl_opts = {
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook_wrapper],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            },
        }

        if selected_resolution_text == "Tylko audio":
            ydl_opts['format'] = "bestaudio/best"
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            resolution_map = {
                "4K": "2160",
                "1440p": "1440",
                "1080p": "1080",
                "720p": "720",
                "480p": "480",
                "360p": "360"
            }
            selected_res = resolution_map.get(selected_resolution_text, "best")
            ydl_opts['format'] = f'bestvideo[height<={selected_res}]+bestaudio/best[height<={selected_res}]'
        
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except DownloadError as e:
                error_message = str(e)
                if "Requested format is not available" in error_message:
                    return f"Wybrany format nie jest dostępny. Spróbuj innej rozdzielczości."
                else:
                    return f"Wystąpił błąd podczas pobierania: {error_message}"
            except Exception as e:
                return f"Nieoczekiwany błąd: {str(e)}"

        return "Pobieranie zakończone!"
    
    def progress_hook_wrapper(self, d):
        return progress_hook(d, self.stop_download, self.gui.progress_label, self.gui.size_label, self.gui.progress_bar, self.gui.speed_label, self.gui.eta_label)

    def stop(self):
        self.stop_download = True