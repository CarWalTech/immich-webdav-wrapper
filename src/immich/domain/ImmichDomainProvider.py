from typing import TYPE_CHECKING

from wsgidav.dav_provider import DAVProvider
from src.immich.ImmichRootCollection import ImmichRootCollection
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainUser import ImmichDomainUser
    from src.immich.domain.ImmichDomainController import ImmichDomainController

class ImmichDomainProvider(DAVProvider):
    """
    Custom WebDAV provider that maps the Immich API to a virtual filesystem.
    """

    def __init__(self):
        super().__init__()
        self.__domain_controller: "ImmichDomainController" = None

    def _get_user_data(self, environ) -> "ImmichDomainUser | None": 
        if "immich_access_token" not in environ and "immich_user_id" not in environ: return None
        immich_access_token: str = environ["immich_access_token"]
        immich_user_id: str = environ["immich_user_id"]
        if immich_user_id not in self.__domain_controller.users: return None
        if self.__domain_controller.users[immich_user_id].immich_access_token != immich_access_token: return None
        return self.__domain_controller.users[immich_user_id]
        
    def set_domain_controller(self, controller: "ImmichDomainController"):
        self.__domain_controller = controller
        
    def stop_refresh(self):
        for user_id in self.__domain_controller.users:
            self.__domain_controller.users[user_id].stop_refresh()

    def get_resource_inst(self, path, environ):
        #_logger.info("get_resource_inst('%s')" % path)
        root = ImmichRootCollection(environ, self._get_user_data(environ))
        return root.resolve("", path)