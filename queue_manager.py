import threading

class QueueManager:
    def __init__(self, downloader, gui):
        self.download_queue = []
        self.downloader = downloader
        self.gui = gui
        self.current_download_thread = None
        self.paused = False

    def start_download(self, url, resolution, download_subtitles, output_format, subtitle_language=None):
        self.download_queue.append((url, resolution, download_subtitles, output_format, subtitle_language))
        if len(self.download_queue) == 1:
            self.process_queue()
            self.gui.stop_button.place(x=300, y=150)
        else:
            self.gui.show_message("Informacja", "Link dodany do kolejki pobierań.")

    def process_queue(self):
        if self.download_queue:
            url, resolution, download_subtitles, output_format, subtitle_language = self.download_queue[0]
            self.current_download_thread = threading.Thread(
                target=self.download_video, 
                args=(url, resolution, download_subtitles, output_format, subtitle_language)
            )
            self.current_download_thread.start()
        else:
            self.gui.show_message("Informacja", "Wszystkie pobierania zakończone.")
            self.gui.stop_button.place_forget()

    def download_video(self, url, resolution, download_subtitles, output_format, subtitle_language):
        self.gui.progress_label.config(text="Rozpoczynanie pobierania...")
        self.gui.progress_bar['value'] = 0
        result = self.downloader.download_video(url, resolution, download_subtitles, output_format, subtitle_language)
        if result.startswith("Dla tego filmu nie są dostępne napisy"):
            self.gui.show_message("Informacja", result)
            result = self.downloader.download_video(url, resolution, False, output_format, None)
        
        if result != "Pobieranie zakończone!":
            self.gui.show_message("Błąd", result)
        
        self.download_queue.pop(0)
        self.gui.root.after(1000, self.process_queue)

    def stop_download(self):
        if self.current_download_thread and self.current_download_thread.is_alive():
            self.downloader.stop()
            self.gui.stop_button.place_forget()
            self.gui.progress_label.config(text="Pobieranie zatrzymane.")
    
    def pause_download(self):
        self.paused = True
        self.downloader.pause()

    def resume_download(self): 
        self.paused = False
        self.downloader.resume()

   
    def move_up(self, index):
        if index > 0:
            self.download_queue[index], self.download_queue[index - 1] = self.download_queue[index - 1], self.download_queue[index]

    def move_down(self, index):
        if index < len(self.download_queue) - 1:
            self.download_queue[index], self.download_queue[index + 1] = self.download_queue[index + 1], self.download_queue[index]
            