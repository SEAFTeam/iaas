#import sys
#from pprint import pprint
from kubernetes import client
# базовый класс
from extractor import Extractor

class NetworkPolicyExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'network_policy'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        api = client.NetworkingV1Api(self.kube)
        npcies = api.list_network_policy_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        return npcies.items
