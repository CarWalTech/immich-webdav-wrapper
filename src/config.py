import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    immich_url: str | None
    album_ids: list[str]
    refresh_rate_hours: int | None
    port: int | None
    excluded_file_types: list[str]
    flatten_structure: bool

    @staticmethod
    def load():

        def parse_album_ids(env: str | None):
            return [id.strip() for id in env.split(",") if id.strip()] if env else []

        def parse_file_types(env: str):
            return [ x.strip().lower() for x in env.split(",") if x.strip()]
        
        return AppConfig(
            os.getenv("IMMICH_URL"),
            parse_album_ids(os.getenv("ALBUM_IDS")),
            int(os.getenv("REFRESH_RATE_HOURS", 1)),
            int(os.getenv("WEBDAV_PORT", 1700)),
            parse_file_types(os.getenv("EXCLUDED_FILE_TYPES", "")),
            os.getenv("FLATTEN_ASSET_STRUCTURE", "false").lower() == "true"
        )