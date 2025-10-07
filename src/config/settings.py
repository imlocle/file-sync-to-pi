from pydantic_settings import BaseSettings, SettingsConfigDict
import os

from src.utils.constants import MOVIES_DIR, TV_SHOWS_DIR


class Settings(BaseSettings):
    watch_dir: str = os.path.expanduser("~/Transfers")
    pi_user: str
    pi_ip: str
    pi_movies: str = f"/mnt/external/{MOVIES_DIR}/"
    pi_tv: str = f"/mnt/external/{TV_SHOWS_DIR}/"
    file_exts: set = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".srt"}
    skip_files: set = set()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
