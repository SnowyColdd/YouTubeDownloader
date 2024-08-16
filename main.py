import tkinter as tk
from downloader import Downloader
from gui import YouTubeDownloaderGUI
from queue_manager import QueueManager

def start_download_callback(url, resolution):
    queue_manager.start_download(url, resolution)

def stop_download_callback():
    queue_manager.stop_download()

if __name__ == "__main__":
    root = tk.Tk()
    
    gui = YouTubeDownloaderGUI(root, start_download_callback, stop_download_callback)
    downloader = Downloader(gui)
    queue_manager = QueueManager(downloader, gui)
    root.mainloop()