import hashlib
from typing import TYPE_CHECKING

from wsgidav import util

from src.immich.asset.providers.AssetProvider import AssetProvider
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainUser import ImmichDomainUser



class RemoteAssetProvider(AssetProvider):

    def __init__(self, asset_path: str, user_data: "ImmichDomainUser"):
        super().__init__()
        self.path = asset_path
        self._user_data = user_data

    def get_content_length(self, asset):
        asset_id = asset.get("id")
        if not asset_id:
            return None
        return self._user_data.fetch_asset_size(asset_id)

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
        asset_id = asset.get("id")
        return self._user_data.fetch_asset(asset_id)
