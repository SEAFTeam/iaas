from kubernetes import client
# базовый класс
from extractor import Extractor

class PersistentVolumeClaimExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'pvc'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        api = client.CoreV1Api(self.kube)
        pvcs = api.list_persistent_volume_claim_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        #pprint(deployments.items)
        return pvcs.items

