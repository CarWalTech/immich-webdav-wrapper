
import requests
from typing import TYPE_CHECKING
from wsgidav.dc.base_dc import BaseDomainController

from src.config import AppConfig
from src.immich.domain.ImmichDomainUser import ImmichDomainUser
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainProvider import ImmichDomainProvider

class ImmichDomainController(BaseDomainController):
    def __init__(self, wsgidav_app, config):
        super().__init__(wsgidav_app, config)
        self.provider: ImmichDomainProvider = config["provider_mapping"]["/"]
        self.config: AppConfig = config["immich_settings"]
        self.immich_url = self.config.immich_url.rstrip("/")
        self.users: dict[str, ImmichDomainUser] = {}
        self.refresh_rate_hours = self.config.refresh_rate_hours
        self.excluded_file_types = self.config.excluded_file_types

        self.provider.set_domain_controller(self)

    def _update_user(self, access_token: str, user_id: str):
        if not user_id in self.users:
            self.users[user_id] = ImmichDomainUser(self, access_token, user_id)
        else:
            self.users[user_id].update_access_token(access_token)
        
        return self.users[user_id]
    
    def basic_auth_user(self, realm, username, password, environ):
        """Return True if Immich accepts the credentials."""
        url = f"{self.immich_url}/api/auth/login"
        payload = {"email": username, "password": password}

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 201:
                data = resp.json()
                #_logger.info("Authenticated: \r\n" + str(data))
                user = self._update_user(data["accessToken"], data["userId"])
                environ["immich_access_token"] = user.immich_access_token
                environ["immich_user_id"] = user.immich_user_id
                return True
            return False
        except Exception as e:
            _logger.error(f"Immich auth error: {e}")
            #raise e
            return False
    
    def get_domain_realm(self, path_info, environ):
        return self._calc_realm_from_path_provider(path_info, environ)

    def supports_http_digest_auth(self):
        return True

    def require_authentication(self, realm, environ):
        return True