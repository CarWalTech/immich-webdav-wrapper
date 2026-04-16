import hashlib
from wsgidav import util
from src.immich.asset.providers.AssetProvider import AssetProvider
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()
from dateutil.parser import isoparse
import os

class LocalAssetProvider(AssetProvider):

    def __init__(self, assetPath: str):
        super().__init__()
        self.path = assetPath
    
    def get_content_length(self, asset):
        try:
            return os.path.getsize(asset.get("originalPath"))
        except (FileNotFoundError, TypeError):
            _logger.error("Check originalPath")
            return None
        
    def get_content_type(self, asset):
        return asset.get("originalMimeType")
    
    def get_creation_date(self, asset):
        val = asset.get("fileCreatedAt")
        if not val:
            return None
        try:
            return int(isoparse(val).timestamp())
        except Exception:
            return None

    def get_display_info(self, asset):
        return {
            "type": "File",
            "etag": self.get_etag(asset),
            "size": self.get_content_length(asset),
        }

    def get_etag(self, asset):
        return (
            f"{hashlib.md5(self.path.encode()).hexdigest()}-"
            f"{util.to_str(self.get_last_modified(asset))}-"
            f"{self.get_content_length(asset)}"
        )

    def support_etag(self, asset):
        return True

    def get_last_modified(self, asset):
        val = asset.get("fileModifiedAt")
        if not val:
            return None
        try:
            return int(isoparse(val).timestamp())
        except Exception:
            return None

    def get_content(self, asset):
        path = asset.get("originalPath")
        if not path:
            raise FileNotFoundError("Missing originalPath")
        return open(path, "rb")