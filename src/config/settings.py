from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    file_exts: set = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".srt"}
    pi_ip: str
    pi_movies: str
    pi_tv: str
    pi_user: str
    skip_files: set = set()
    watch_dir: str = os.path.expanduser("~/Transfers")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
