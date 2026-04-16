from typing import TYPE_CHECKING

from wsgidav.dav_provider import DAVCollection
from src.immich.asset.ImmichAssetCollection import ImmichAssetCollection
from src.immich.album.ImmichAlbumCollection import ImmichAlbumCollection

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainUser import ImmichDomainUser

class ImmichRootCollection(DAVCollection):
    """Resolves top-level requests ('/')"""

    def __init__(self, environ, user_data: "ImmichDomainUser"):
        super().__init__("/", environ)
        self.user_data: "ImmichDomainUser" = user_data
            
    def get_member_names(self):
        return ["albums", "unsorted"]

    def get_member(self, name):
        if name == "albums":
            return ImmichAlbumCollection("/albums", self.environ, self.user_data)
        elif name == "unsorted":
            return ImmichAssetCollection("/unsorted", self.environ, self.user_data)
        else:
            return None