from kubernetes import client
# базовый класс
from extractor import Extractor

class StatefulSetExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'stateful_set'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        api = client.AppsV1Api(self.kube)
        sets = api.list_stateful_set_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        #pprint(deployments.items)
        return sets.items

