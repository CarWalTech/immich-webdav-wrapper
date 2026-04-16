from typing import TYPE_CHECKING

from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN
from wsgidav.dav_provider import DAVNonCollection


from src.immich.asset.providers.AssetProvider import AssetProvider
from src.immich.asset.providers.RemoteAssetProvider import RemoteAssetProvider
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainUser import ImmichDomainUser


class ImmichAsset(DAVNonCollection):
    """Represents an individual photo or video file mapped from the Immich local filesystem."""

    def __init__(self, path, environ, asset, user_data: "ImmichDomainUser"):
        super().__init__(path, environ)
        self.asset = asset
        self._user_data = user_data
        self._asset_provider: AssetProvider = RemoteAssetProvider(path, user_data)
        
    def handle_delete(self):
        #TODO: Implement API Calls to Move Image to the Trash
        return super().handle_delete()

    def delete(self):
        #TODO: Implement API Calls to Move Image to the Trash
        raise DAVError(HTTP_FORBIDDEN)
    
    def handle_copy(self, dest_path, *, depth_infinity):
        #TODO: Implement API Calls to Move Image or add Image to other Albums
        return super().handle_copy(dest_path, depth_infinity=depth_infinity)

    def copy_move_single(self, dest_path, *, is_move):
        #TODO: Implement API Calls to Move Image or add Image to other Albums
        raise DAVError(HTTP_FORBIDDEN)
    
    def handle_move(self, dest_path):
        #TODO: Implement API Calls to Move Image or add Image to other Albums
        return super().handle_move(dest_path)

    def move_recursive(self, dest_path):
        #TODO: Implement API Calls to Move Image or add Image to other Albums
        return super().move_recursive(dest_path)

    def support_recursive_move(self, dest_path):
        #TODO: Implement API Calls to Move Image or add Image to other Albums
        return super().support_recursive_move(dest_path)
    


    #region File Info
    
    def get_content_length(self):
        return self._asset_provider.get_content_length(self.asset)

    def get_content_type(self):
        return self._asset_provider.get_content_type(self.asset)

    def get_creation_date(self):
        return self._asset_provider.get_creation_date(self.asset)

    def get_display_name(self):
        return self.name

    def get_display_info(self):
        return self._asset_provider.get_display_info(self.asset)

    def get_etag(self):
        return self._asset_provider.get_etag(self.asset)

    def support_etag(self):
        return self._asset_provider.support_etag(self.asset)

    def get_last_modified(self):
        return self._asset_provider.get_last_modified(self.asset)

    def get_content(self):
        return self._asset_provider.get_content(self.asset)
    
    #endregion