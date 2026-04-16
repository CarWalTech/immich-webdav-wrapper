from typing import TYPE_CHECKING

from wsgidav.dav_provider import DAVCollection
from wsgidav.util import join_uri

from src.immich.asset.ImmichAsset import ImmichAsset
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainUser import ImmichDomainUser

class ImmichAssetCollection(DAVCollection):
    """Represents specific Immich assets, exposing a flat structure."""

    def __init__(self, path, environ, user_data: "ImmichDomainUser"):
        super().__init__(path, environ)
        self._user_data: "ImmichDomainUser" = user_data

    def files(self, refresh=False):
        if not self._user_data: return {}
        return self._user_data.get_assets_by_route(self.path, refresh)            

    def get_member_names(self):
        return sorted(self.files(True).keys())

    def get_member(self, name):
        asset = self.files().get(name)
        if not asset:
            return None
        return ImmichAsset(join_uri(self.path, name), self.environ, asset, self._user_data)