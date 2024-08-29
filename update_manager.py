import requests
import logging
from packaging import version
from dataclasses import dataclass
from typing import Optional

GITHUB_API_URL = "https://api.github.com/repos/SnowyColdd/YouTubeDownloader/releases/latest"

@dataclass
class UpdateInfo:
    version: str
    download_url: str
    release_notes: str

class UpdateManager:
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.logger = logging.getLogger(__name__)

    def check_for_updates(self) -> Optional[UpdateInfo]:
        try:
            response = requests.get(GITHUB_API_URL, timeout=10)
            response.raise_for_status()
            latest_release = response.json()

            if 'tag_name' not in latest_release or 'assets' not in latest_release or not latest_release['assets']:
                self.logger.warning("Nieprawidłowa odpowiedź API GitHub")
                return None

            latest_version = latest_release['tag_name']
            download_url = latest_release['assets'][0]['browser_download_url']
            release_notes = latest_release['body']

            if version.parse(latest_version) > version.parse(self.current_version):
                return UpdateInfo(latest_version, download_url, release_notes)
            return None
        except requests.RequestException as e:
            self.logger.error(f"Błąd podczas sprawdzania aktualizacji: {e}")
            return None

    def download_update(self, update_info: UpdateInfo) -> Optional[str]:
        try:
            update_file = f"YouTubeDownloader_{update_info.version}.exe"
            response = requests.get(update_info.download_url, timeout=30)
            response.raise_for_status()

            with open(update_file, 'wb') as f:
                f.write(response.content)

            self.logger.info(f"Aktualizacja pobrana: {update_file}")
            return update_file
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania aktualizacji: {e}")
            return None