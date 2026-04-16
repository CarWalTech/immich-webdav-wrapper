


import re

import requests
import threading
import time
from typing import TYPE_CHECKING

from src.immich.album.ImmichAlbumRoute import ImmichAlbumRoute, ImmichAlbumRouteList
from src.utils.SafeNameMixin import SafeNameMixin
from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from src.immich.domain.ImmichDomainController import ImmichDomainController

ASSET_SIZE_CACHE = {}

class ImmichDomainUser:

    def __init__(self, controller: "ImmichDomainController", access_token: str, user_id: str):
        super().__init__()
        self._count_get_resource_inst = 0

        self.immich_url = controller.immich_url.rstrip("/")
        self.immich_access_token = access_token
        self.immich_user_id = user_id

        self.immich_asset_cache: dict[str, any] = dict()
        self.immich_album_cache: dict[str, any] = dict()

        self.immich_album_tree: ImmichAlbumRouteList = ImmichAlbumRouteList()

        self.refresh_rate_seconds = controller.refresh_rate_hours * 3600
        self.excluded_file_types = controller.excluded_file_types

        self.refresh_thread = threading.Thread(target=self._auto_refresh, daemon=True)
        self.stop_event = threading.Event()

        self.refresh_albums()    
        self.refresh_thread.start()

    def _get_cookies(self):
        return {
            "immich_access_token": self.immich_access_token,
            "immich_auth_type": "password",
            "immich_is_authenticated": "true"
        }

    def _auto_refresh(self):
        while not self.stop_event.wait(self.refresh_rate_seconds):
            _logger.info("Refreshing assets...")
            self.refresh_albums()

    def _post_with_retries(self, url, data={}, max_retries=3):
        cookies = self._get_cookies()

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, cookies=cookies, json=data, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                _logger.error(f"Error posting {url} (attempt {attempt}/{max_retries}): {e}")
                time.sleep(2)

        return None

    def _fetch_with_retries(self, url, data={}, max_retries=3):
        cookies = self._get_cookies()

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, cookies=cookies, json=data, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                _logger.error(f"Error fetching {url} (attempt {attempt}/{max_retries}): {e}")
                time.sleep(2)

        return None

    def _pathify_albums(self, albums: list[dict[str, any]]):
        def normalize(p: str) -> str:
            p = p.strip()
            p = re.sub(r"\s*/\s*", "/", p)
            p = re.sub(r"/+", "/", p)
            return p.rstrip("/")

        # Step 1: Build normalized → raw and normalized → id maps
        norm_to_raw = {}
        norm_to_id = {}

        for album in albums:
            raw = album["albumName"]
            norm = normalize(raw)
            norm_to_raw[norm] = raw
            norm_to_id[norm] = album["id"]

        # Step 2: Add missing intermediate folders
        all_norm_paths = set(norm_to_raw.keys())

        for norm in list(all_norm_paths):
            parts = norm.split("/")
            for i in range(1, len(parts)):
                parent_norm = "/".join(parts[:i])
                if parent_norm not in all_norm_paths:
                    all_norm_paths.add(parent_norm)
                    norm_to_raw[parent_norm] = parent_norm
                    norm_to_id[parent_norm] = None  # virtual

        # Step 3: Create nodes
        nodes: dict[str, ImmichAlbumRoute] = {}
        for norm in all_norm_paths:
            raw = norm_to_raw[norm]
            album_id = norm_to_id[norm]
            nodes[norm] = ImmichAlbumRoute(raw, album_id, is_virtual=(album_id is None))

        # Step 4: Link parents and children
        for norm, node in nodes.items():
            parts = norm.split("/")
            if len(parts) == 1:
                continue  # root-level

            parent_norm = "/".join(parts[:-1])
            parent_node = nodes[parent_norm]
            parent_node.add_child(node)

        # Keep only root nodes (nodes with no parent)
        root_nodes = ImmichAlbumRouteList([node for norm, node in nodes.items() if node.album_parent_id == None])
        return root_nodes

    def _uniquify_assets(self, assets):
        processed = {}
        used_all = set()

        for asset in assets:
            original = asset.get("originalFileName")
            if not original:
                continue

            ext = original.split(".")[-1].lower()
            if ext in self.excluded_file_types:
                continue

            asset_id = asset.get("id", "unknown")
            safe_all = SafeNameMixin.unique_safe_name(original, "Untitled Asset", used_all, asset_id)
            processed[safe_all] = asset

        return processed

    def _get_albums(self):
        url = f"{self.immich_url}/api/albums"
        albums = self._fetch_with_retries(url)
        if albums: return albums
        return []

    def _get_album_data(self, album_id, used_album_names, new_album_map):
        url = f"{self.immich_url}/api/albums/{album_id}"
        album_data = self._fetch_with_retries(url)

        if album_data:
            album_data = dict(album_data)
            album_name = album_data.get("albumName")
            asset_count = len(album_data.get("assets", []))
            

            album_data["processed_assets"] = self._uniquify_assets(
                album_data.get("assets", [])
            )

            safe_album_name = SafeNameMixin.unique_safe_name(
                album_data.get("albumName"),
                fallback="Untitled Album",
                existing_names=used_album_names,
                unique_suffix=album_data.get("id", "unknown"),
            )

            # Ensure string
            safe_album_name = str(safe_album_name)

            # NEW: normalize whitespace around slashes
            safe_album_name = "/".join(part.strip() for part in safe_album_name.split("/"))

            new_album_map[safe_album_name] = album_data

            _logger.info(f"Loaded Album {album_name} with {asset_count} assets from the API.")

    def _get_unsorted_assets(self):

        def request_items(page=0) -> list:
            url = f"{self.immich_url}/api/search/metadata"
            json = { "isNotInAlbum": True }
            if page != 0: json["page"] = page
                
            search_results: dict = self._post_with_retries(url, json)

            if search_results == None:
                return []
            
            asset_search_results: dict = search_results.get("assets", {})
            found_assets = asset_search_results.get("items", [])
            next_page = asset_search_results.get("nextPage", None)


            if next_page != None:
                other_assets = request_items(page+1)
                found_assets = found_assets + other_assets

            return found_assets

        items = request_items()
        _logger.info(f"Loaded {len(items)} unsorted assets from the API.")
        return self._uniquify_assets(items)
    
    def _get_album_assets(self, path: ImmichAlbumRoute):
        def request_items(page=0) -> list:
            url = f"{self.immich_url}/api/albums/{path.album_id}"
            search_results: dict = self._fetch_with_retries(url)
            if search_results == None:
                return []
            
            found_assets: dict = search_results.get("assets", {})
            return found_assets

        items = request_items()
        _logger.info(f"Loaded {len(items)} assets in album [{path.raw_name}] from the API.")
        return self._uniquify_assets(items)



    #region Public Methods

    def fetch_asset_size(self, asset_id):
        if not asset_id:
            return None

        if asset_id in ASSET_SIZE_CACHE:
            return ASSET_SIZE_CACHE[asset_id]

        url = f"{self.immich_url}/api/assets/{asset_id}/original"
        cookies = self._get_cookies()
        head = requests.head(url, cookies=cookies)
        size = int(head.headers.get("Content-Length", 0))

        ASSET_SIZE_CACHE[asset_id] = size
        return size
    
    def fetch_asset(self, asset_id):        
        url = f"{self.immich_url}/api/assets/{asset_id}/original"
        cookies = self._get_cookies()
        response = requests.get(url, cookies=cookies, stream=True)
        response.raise_for_status()
        return response.raw

    def get_albums_by_route(self, route: "ImmichAlbumRoute | None", refresh: bool = False) -> ImmichAlbumRouteList:
        path = "/albums/"
        if route: path += route.uri

        if path in self.immich_album_cache and not refresh:    
            return ImmichAlbumRouteList(self.immich_album_cache[path])
        
        if route == None:
            results = self.immich_album_tree
        elif route.album_children:
            results = route.album_children
        else:
            results = ImmichAlbumRouteList()
        
        
        self.immich_album_cache[path] = results
        return results

    def get_assets_by_route(self, route: "ImmichAlbumRoute | str | None", refresh: bool = False) -> dict:
        path: str

        if route and isinstance(route, ImmichAlbumRoute): path = f"/albums/{route.uri}"
        elif route and isinstance(route, str): path = f"{route}"
        else: path = "/"
    
        if path in self.immich_asset_cache and not refresh:
            return self.immich_asset_cache[path]
        
        results = {}

        if path == "/unsorted":
            results = self._get_unsorted_assets()

        elif path.startswith("/albums") and route and isinstance(route, ImmichAlbumRoute):
            results = self._get_album_assets(route)

        self.immich_asset_cache[path] = results
        return results

    def refresh_albums(self):
        albums: list[dict[str, any]] = self._get_albums()
        self.immich_album_tree = self._pathify_albums(albums)

    def update_access_token(self, access_token: str):
        self.immich_access_token = access_token

    def stop_refresh(self):
        self.stop_event.set()
        if self.refresh_thread.is_alive():
            self.refresh_thread.join()
    #endregion