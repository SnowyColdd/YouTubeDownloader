import threading

class QueueManager:
    def __init__(self, downloader, gui):
        self.download_queue = []
        self.downloader = downloader
        self.gui = gui

    def start_download(self, url, resolution):
        self.download_queue.append((url, resolution))
        if len(self.download_queue) == 1:
            self.process_queue()
            self.gui.stop_button.place(x=300, y=150)
        else:
            self.gui.show_message("Informacja", "Link dodany do kolejki pobierań.")

    def process_queue(self):
        if self.download_queue:
            url, resolution = self.download_queue[0]
            download_thread = threading.Thread(target=self.download_video, args=(url, resolution))
            download_thread.start()
        else:
            self.gui.show_message("Informacja", "Wszystkie pobierania zakończone.")

    def download_video(self, url, resolution):
        result = self.downloader.download_video(url, resolution)
        if result:
            self.gui.show_message("Błąd", result)
        self.download_queue.pop(0)
        self.gui.root.after(1000, self.process_queue)

    def stop_download(self):
        self.downloader.stop()
        self.gui.stop_button.place_forget()
        self.gui.progress_label.config(text="Pobieranie zatrzymane.")
