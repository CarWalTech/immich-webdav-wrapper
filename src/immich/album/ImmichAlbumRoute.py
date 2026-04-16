import uuid



class ImmichAlbumRoute:

    PATH_SEPERATOR = " / "

    def __init__(self, raw_name: str, album_id: str | None = None, is_virtual: bool = False):
        self.raw_name = raw_name
        self.is_virtual = is_virtual
        self.album_id = album_id if not is_virtual else "virtual: " + str(uuid.uuid4())
        self.album_children: ImmichAlbumRouteList = ImmichAlbumRouteList()
        self.album_parent_id = None
        self.uri = self.get_folder_path()


    def get_folder_segments(self):
         return self.get_folder_path().split("/")
    
    def get_folder_prefix(self):
        return f"{self.get_folder_path()}/"
    
    def get_folder_path(self):
        return "/".join(self.raw_name.split(ImmichAlbumRoute.PATH_SEPERATOR))
    
    def get_folder_name(self):
        return self.get_folder_path().split("/")[-1]
         
    def add_child(self, child: "ImmichAlbumRoute"):
        if not self.album_children.contains_album_id(child):
             self.album_children.append(child)
             child.album_parent_id = self.album_id

    def is_child_of(self, parent: "ImmichAlbumRoute"):
        parent_prefix = parent.get_folder_prefix()
        if not self.raw_name.startswith(parent_prefix): return False

        actual_name = self.raw_name.lstrip(parent_prefix)
        if ImmichAlbumRoute.PATH_SEPERATOR in actual_name: return False

        return actual_name
    
class ImmichAlbumRouteList(list[ImmichAlbumRoute]):
        
    def get_by_folder_name(self, folder_name: str):
        results = [x for x in self if x.get_folder_name() == folder_name]
        if len(results) >= 1: return results[0]
        else: return None

    def contains_album_id(self, item: ImmichAlbumRoute):
        return item.album_id in [x.album_id for x in self]
    
    def contains_folder_name(self, folder_name: str):
        return folder_name in [x.get_folder_name() for x in self]