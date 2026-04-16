from typing import TYPE_CHECKING

from wsgidav.util import join_uri


from src.utils.AppLoggerMixin import AppLoggerMixin
_logger = AppLoggerMixin.get_logger()

if TYPE_CHECKING:
    from immich.domain.ImmichDomainUser import ImmichDomainUser
    from src.immich.album.ImmichAlbumRoute import ImmichAlbumRoute, ImmichAlbumRouteList

class ImmichAlbumUtils:
    @staticmethod
    def GetAlbums(route: "ImmichAlbumRoute | None", user_data: "ImmichDomainUser", refresh: bool = False):
        from src.immich.album.ImmichAlbumRoute import ImmichAlbumRouteList
        if not user_data: return ImmichAlbumRouteList()
        results = user_data.get_albums_by_route(route, refresh)   
        return results

    @staticmethod
    def Create(name: str, path: str, albums: "ImmichAlbumRouteList", environ, user_data: "ImmichDomainUser"):
        if not albums.contains_folder_name(name): return None
        album_data: "ImmichAlbumRoute" = albums.get_by_folder_name(name)

        if album_data.is_virtual == False:
            #_logger.info(f"""populating album: Name: {name} Path: {path} Folder Path: {folder_path}""")
            from src.immich.album.ImmichAlbum import ImmichAlbum
            return ImmichAlbum(
                join_uri(path, name),
                environ,
                data=album_data,
                user_data=user_data
            )
        else:
            #_logger.info(f"""populating virtual album: Name: {name} Path: {path} Folder Path: {folder_path}""")
            from src.immich.album.ImmichAlbum import ImmichAlbumPath
            return ImmichAlbumPath(
                join_uri(path, name),
                environ,
                data=album_data,
                user_data=user_data
            )

    @staticmethod
    def ListMembers(known_albums: "ImmichAlbumRouteList"):
        print([x.raw_name for x in known_albums])
        top_levels = set()

        for albums in known_albums:
            full_name = albums.get_folder_name()
            if not isinstance(full_name, str):
                continue
            top_levels.add(full_name)
        return sorted(top_levels)

