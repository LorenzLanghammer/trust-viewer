
from abc import ABC, abstractmethod



class GdsInterface(ABC):
    @abstractmethod
    def connect(self):
        pass
    def disconnect(self):
        pass
    def getApplications(self):
        pass
    def getCertificateGroups(self):
        pass
    def readTrustList(self, trustlist_id: int):
        pass


class open62541GDS(GdsInterface):
    def __init__(self, client):
        self.client = client

    def connect(self):
        pass
    def disconnect(self):
        pass
    def getApplications(self):
        pass
    def getCertificateGroups(self):
        pass
    def readTrustList(self, trustlist_id: int):
        pass
