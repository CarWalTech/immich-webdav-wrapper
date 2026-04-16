from typing import TYPE_CHECKING

from wsgidav.dav_provider import DAVCollection
from wsgidav.util import join_uri

from src.immich.album.ImmichAlbumUtils import ImmichAlbumUtils
from src.immich.album.ImmichAlbumRoute import ImmichAlbumRoute
from src.immich.asset.ImmichAsset import ImmichAsset
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from immich.domain.ImmichDomainUser import ImmichDomainUser

class ImmichAlbumPath(DAVCollection):
    """Represents a virtual folder created from album name path segments."""

    def __init__(self, path, environ, data: ImmichAlbumRoute, user_data: "ImmichDomainUser"):
        super().__init__(path, environ)
        self.album_data = data
        self._user_data = user_data

    def get_member_names(self):
        return ImmichAlbumUtils.ListMembers(ImmichAlbumUtils.GetAlbums(self.album_data, self._user_data, True))

    def get_member(self, name):
        root_albums = ImmichAlbumUtils.GetAlbums(self.album_data, self._user_data)
        return ImmichAlbumUtils.Create(name, self.path, root_albums, self.environ, self._user_data)
    
class ImmichAlbum(ImmichAlbumPath):
    """Represents a specific Immich album, exposing a flat structure."""

    def __init__(self, path, environ, data: ImmichAlbumRoute, user_data: "ImmichDomainUser"):
        super().__init__(path, environ, data, user_data)

    def files(self, refresh=False):
        if not self._user_data: return {}
        return self._user_data.get_assets_by_route(self.album_data, refresh)            

    def get_member_names(self):
        nested_albums = super().get_member_names()
        return nested_albums + sorted(self.files(True))

    def get_member(self, name):
        base_result = super().get_member(name)
        if base_result:
            return base_result
        
        asset = self.files().get(name)
        if not asset:
            return None
        return ImmichAsset(join_uri(self.path, name), self.environ, asset, self._user_data)