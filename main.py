import tkinter as tk
from downloader import Downloader
from gui import YouTubeDownloaderGUI
from queue_manager import QueueManager
from update_manager import UpdateManager

def start_download_callback(url, resolution, download_subtitles, output_format, subtitle_language=None):
    queue_manager.start_download(url, resolution, download_subtitles, output_format, subtitle_language)

def stop_download_callback():
    queue_manager.stop_download()
    gui.stop_button.pack_forget()

def check_for_updates_callback():
    update_info = update_manager.check_for_updates()
    if update_info:
        gui.show_update_dialog(update_info)
    else:
        gui.show_message("Aktualizacje", "Brak dostępnych aktualizacji.")

def download_update_callback(update_info):
    return update_manager.download_update(update_info)

if __name__ == "__main__":
    root = tk.Tk()
    
    current_version = "2.3"
    update_manager = UpdateManager(current_version)
    gui = YouTubeDownloaderGUI(root, start_download_callback, stop_download_callback, check_for_updates_callback, download_update_callback)
    downloader = Downloader(gui)
    queue_manager = QueueManager(downloader, gui)

    gui.check_for_updates()

    root.mainloop()