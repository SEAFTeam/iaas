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
        self.logger.info(f'attempt to load deployments from {self.kube.configuration.host} namespace {self.parent}')
        deployments = api.list_deployment_for_all_namespaces(field_selector=f'metadata.namespace={self.parent}')
        self.logger.info(f'loaded {len(deployments.items)}')
        return deployments.items

