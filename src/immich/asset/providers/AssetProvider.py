from abc import ABC, abstractmethod



class AssetProvider(ABC):

    @abstractmethod
    def get_content_length(self, asset):
        pass

    @abstractmethod
    def get_content_type(self, asset):
        pass

    @abstractmethod
    def get_creation_date(self, asset):
        pass

    @abstractmethod
    def get_display_info(self, asset):
        pass

    @abstractmethod
    def get_etag(self, asset):
        pass

    @abstractmethod
    def support_etag(self, asset):
        pass

    @abstractmethod
    def get_last_modified(self, asset):
        pass

    @abstractmethod
    def get_content(self, asset):
        pass