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
        self.logger.info(f'attempt to load nodes from {self.kube.configuration.host}')
        nodes   = api.list_node()
        #print(nodes.__class__)
        #print(dir(nodes.items))

        self.logger.info(f'loaded {len(nodes.items)}')
        return nodes.items

