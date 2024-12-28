from kubernetes import client
# базовый класс
from extractor import Extractor

class ServiceExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'service'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        api = client.CoreV1Api(self.kube)
        services = api.list_service_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        #pprint(deployments.items)
        return services.items

