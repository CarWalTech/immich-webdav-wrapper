from typing import TYPE_CHECKING

from wsgidav.dav_provider import DAVCollection

from src.immich.album.ImmichAlbumUtils import ImmichAlbumUtils

if TYPE_CHECKING:
    from immich.domain.ImmichDomainUser import ImmichDomainUser

class ImmichAlbumCollection(DAVCollection):
    """Resolves available Immich albums."""

    def __init__(self, path, environ, user_data: "ImmichDomainUser"):
        super().__init__(path, environ)
        self._user_data: "ImmichDomainUser" = user_data

    def get_member_names(self):
        return ImmichAlbumUtils.ListMembers(ImmichAlbumUtils.GetAlbums(None, self._user_data, True))

    def get_member(self, name):
        root_albums = ImmichAlbumUtils.GetAlbums(None, self._user_data)
        return ImmichAlbumUtils.Create(name, self.path, root_albums, self.environ, self._user_data)