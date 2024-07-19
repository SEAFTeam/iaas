from kubernetes import client
# базовый класс
from extractor  import Extractor
# извлекатель деплойментов
from deployment import DeploymentExtractor
from service import ServiceExtractor
from pvc import PersistentVolumeClaimExtractor

class NamespaceExtractor(Extractor):
    # конструктор
    def __init__(self, kube):
        super().__init__(kube)
        self.name = 'namespace'


    def load(self):
        # загрузка списка нод кластера
        api = client.CoreV1Api(self.kube)
        namespaces = api.list_namespace()
        return namespaces.items

    # загрузко объектов, дочерних по отношению к namespace
    def children(self, serializer, items):
        for namespace in items:
            # извлечение деплойментов
            deployments = DeploymentExtractor(self.kube, namespace)
            parent = {}
            parent['item'] = namespace
            parent['entity'] = self.entity()
            deployments.extract(serializer, parent)

            # извлечение сервисов
            services = ServiceExtractor(self.kube, namespace)
            parent = {}
            parent['item'] = namespace
            parent['entity'] = self.entity()
            services.extract(serializer, parent)

            # извлечение PVs
            pvs = PersistentVolumeClaimExtractor(self.kube, namespace)
            parent = {}
            parent['item'] = namespace
            parent['entity'] = self.entity()
            pvs.extract(serializer, parent)
