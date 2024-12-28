#import sys
#from pprint import pprint
from kubernetes import client
# базовый класс
from extractor import Extractor

class PersistentVolumeExtractor(Extractor):
    # конструктор
    def __init__(self, kube):
        super().__init__(kube)
        self.name = 'pv'

    def load(self):
        # загрузка списка нод кластера
        api = client.CoreV1Api(self.kube)
        pvs = api.list_persistent_volume()
        return pvs.items

