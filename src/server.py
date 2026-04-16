


from cheroot import wsgi
from dotenv import load_dotenv
from wsgidav.wsgidav_app import WsgiDAVApp

from src.config import AppConfig
from src.immich.domain.ImmichDomainProvider import ImmichDomainProvider
from src.immich.domain.ImmichDomainController import ImmichDomainController
from src.utils.AppLoggerMixin import AppLoggerMixin

load_dotenv()
_logger = AppLoggerMixin.get_logger()

class ImmichWebDAVServer:
    @staticmethod
    def start():

        environ = AppConfig.load()

        if not environ.immich_url:
            raise ValueError("IMMICH_URL must be set.")

        provider = ImmichDomainProvider()

        config = {
            "host": "0.0.0.0",
            "port": environ.port,
            "provider_mapping": {"/": provider},
            "immich_settings": environ,
            "http_authenticator": {
                "accept_basic": True,
                "accept_digest": False,
                "default_to_digest": False,
                "domain_controller": ImmichDomainController,
            },
            "directory_browser": True,
            "verbose": 2,
        }

        _logger.info(f"Preparing...")
        app = WsgiDAVApp(config)
        server = wsgi.Server(
            bind_addr=(config["host"], environ.port),
            wsgi_app=app,
        )

        try:
            _logger.info(f"Starting WebDAV server on port {environ.port}...")
            server.start()

        except KeyboardInterrupt:
            _logger.info("Stopping...")

        finally:
            provider.stop_refresh()
            server.stop()
            