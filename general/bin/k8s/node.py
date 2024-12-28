#import sys
#from pprint import pprint
from kubernetes import client
# базовый класс
from extractor import Extractor
# from pprint import pprint


class NodeExtractor(Extractor):
    # конструктор
    def __init__(self, kube):
        super().__init__(kube)
        self.name = 'node'

    def load(self):
        # загрузка списка нод кластера
        api     = client.CoreV1Api(self.kube)
        nodes   = api.list_node()
        return nodes.items

