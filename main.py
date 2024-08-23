import tkinter as tk
from downloader import Downloader
from gui import YouTubeDownloaderGUI
from queue_manager import QueueManager

def start_download_callback(url, resolution, download_subtitles, output_format, subtitle_language=None):
    queue_manager.start_download(url, resolution, download_subtitles, output_format, subtitle_language)

def stop_download_callback():
    queue_manager.stop_download()
    gui.stop_button.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    
    gui = YouTubeDownloaderGUI(root, start_download_callback, stop_download_callback)
    downloader = Downloader(gui)
    queue_manager = QueueManager(downloader, gui)
    root.mainloop()