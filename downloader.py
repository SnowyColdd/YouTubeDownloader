import os
import subprocess
import time
import requests
import zipfile
import io
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from utils import get_download_folder, progress_hook

def download_ffmpeg():
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_zip_path = "ffmpeg.zip"
    ffmpeg_folder = "ffmpeg"

    if not os.path.exists(ffmpeg_folder):
        os.makedirs(ffmpeg_folder)
        print("Pobieranie ffmpeg...")
        response = requests.get(ffmpeg_url)
        with open(ffmpeg_zip_path, 'wb') as file:
            file.write(response.content)

        with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if filename:  # nie puste
                    source = zip_ref.open(member)
                    target = open(os.path.join(ffmpeg_folder, filename), "wb")
                    with source, target:
                        target.write(source.read())

        os.remove(ffmpeg_zip_path)
        print("ffmpeg pobrano i rozpakowano.")

    ffmpeg_executable = os.path.join(ffmpeg_folder, "ffmpeg.exe")
    if not os.path.exists(ffmpeg_executable):
        raise FileNotFoundError(f"Nie znaleziono ffmpeg w {ffmpeg_executable}")
    else:
        print(f"ffmpeg znaleziono w {ffmpeg_executable}")

class Downloader:
    def __init__(self, gui):
        self.stop_download = False
        self.paused = False
        self.gui = gui
        download_ffmpeg()  # Dodaj to wywołanie

    def download_subtitles(self, url, subtitle_language):
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [subtitle_language] if subtitle_language else ['en'],
            'skip_download': True,
            'outtmpl': os.path.join(get_download_folder(), '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegSubtitlesConvertor',
                'format': 'srt',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def resume_download(self, url, partial_file):
        ydl_opts = {
            'outtmpl': partial_file,
            'progress_hooks': [self.progress_hook_wrapper],
            'ffmpeg_location': os.path.join("ffmpeg", "ffmpeg.exe"),  # Dodaj tę linię
            'continuedl': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_video(self, url, selected_resolution_text, download_subtitles, output_format, subtitle_language=None):
        self.stop_download = False
        download_folder = get_download_folder()
        ffmpeg_path = os.path.join("ffmpeg", "ffmpeg.exe")
        ydl_opts = {
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook_wrapper],
            'ffmpeg_location': ffmpeg_path,  # Dodaj tę linię
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            },
        }

        if selected_resolution_text == "Tylko audio":
            ydl_opts['format'] = "bestaudio/best"
            
            # Obsługa różnych formatów wyjściowych dla audio
            if output_format == "mp3":
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': output_format,
                }]
                ydl_opts['outtmpl'] = os.path.join(download_folder, f'%(title)s.{output_format}')
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

        # Obsługa pobierania/generowania napisów
        ydl_opts['postprocessors'] = [] 

        if download_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = [subtitle_language] if subtitle_language else ['en']
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegSubtitlesConvertor',
                'format': 'srt',
            })

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if download_subtitles:
                    subtitles = info.get('subtitles', {})
                    auto_subtitles = info.get('automatic_captions', {})
                    
                    if subtitle_language in subtitles:
                        ydl_opts['writesubtitles'] = True
                        ydl_opts['writeautomaticsub'] = False
                    elif subtitle_language in auto_subtitles:
                        ydl_opts['writesubtitles'] = False
                        ydl_opts['writeautomaticsub'] = True
                    else:
                        self.gui.show_message(
                            "Informacja",
                            f"Napisy w języku {subtitle_language} nie są dostępne. Pobieranie bez napisów."
                        )
                        ydl_opts['writesubtitles'] = False
                        ydl_opts['writeautomaticsub'] = False

                ydl.download([url])
                filename = ydl.prepare_filename(info)
                base, ext = os.path.splitext(filename)

                # Konwersja do wybranego formatu, jeśli jest inny niż pierwotny
                if selected_resolution_text != "Tylko audio" and output_format and ext != f'.{output_format}':
                    new_filename = f"{base}.{output_format}"
                    subprocess.run([ffmpeg_path, "-i", filename, new_filename])
                    os.remove(filename)  # Usunięcie oryginalnego pliku
                    filename = new_filename

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

    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False

    def convert_format(self, input_file, output_format):
        ffmpeg_path = os.path.join("ffmpeg", "ffmpeg.exe")
        output_file = os.path.splitext(input_file)[0] + "." + output_format
        total_duration = self.get_video_duration(input_file)
        
        command = [ffmpeg_path, "-i", input_file, "-progress", "pipe:1", "-nostats", output_file]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        start_time = time.time()
        for line in iter(process.stdout.readline, ''):
            if 'out_time_ms' in line:
                time_ms = int(line.split('=')[1])
                progress = (time_ms / 1000000) / total_duration
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / progress if progress > 0 else 0
                remaining_time = estimated_total_time - elapsed_time
                
                self.gui.root.after_idle(self.update_conversion_progress, progress * 100, remaining_time, line)
        
        process.wait()
        return output_file

    def get_video_duration(self, input_file):
        ffmpeg_path = os.path.join("ffmpeg", "ffprobe.exe")
        result = subprocess.run([ffmpeg_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)

    def update_conversion_progress(self, progress, remaining_time, details):
        self.gui.conversion_label.config(text=f"Konwersja: {progress:.2f}%")
        self.gui.conversion_progress['value'] = progress
        self.gui.conversion_time_label.config(text=f"Pozostały czas: {time.strftime('%M:%S', time.gmtime(remaining_time))}")
        self.gui.conversion_details_label.config(text=details)
        self.gui.root.update_idletasks()
