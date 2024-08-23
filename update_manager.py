import requests
import subprocess
import sys
import os

GITHUB_API_URL = "https://api.github.com/repos/SnowyColdd/YouTubeDownloader/releases/latest"

def check_for_updates(current_version):
    """Sprawdza dostępność aktualizacji."""
    try:
        response = requests.get(GITHUB_API_URL)
        latest_release = response.json()
        if 'tag_name' not in latest_release:
            print("Brak informacji o wersji w odpowiedzi API")
            return None, None
        latest_version = latest_release['tag_name']
        if latest_version > current_version:
            if 'assets' in latest_release and latest_release['assets']:
                return latest_version, latest_release['assets'][0]['browser_download_url']
            else:
                print("Brak pliku do pobrania w najnowszym wydaniu")
                return None, None
        return None, None
    except Exception as e:
        print(f"Błąd podczas sprawdzania aktualizacji: {e}")
        return None, None

def download_and_install_update(download_url):
    """Pobiera i instaluje aktualizację."""
    try:
        update_file = "YouTubeDownloader.exe"
        response = requests.get(download_url)
        with open(update_file, 'wb') as f:
            f.write(response.content)
        subprocess.run([update_file], check=True)
        os.remove(update_file)
        print("Aktualizacja zainstalowana. Uruchom program ponownie.")
        sys.exit(0)
    except Exception as e:
        print(f"Błąd podczas instalacji aktualizacji: {e}")
