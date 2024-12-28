from kubernetes import client
# базовый класс
from extractor import Extractor

class DeploymentExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'deployment'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        api = client.AppsV1Api(self.kube)
        deployments = api.list_deployment_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        #pprint(deployments.items)
        return deployments.items

