from kubernetes import client
# базовый класс
from extractor  import Extractor
# извлекатель деплойментов
from deployment import DeploymentExtractor
from service import ServiceExtractor
from pvc import PersistentVolumeClaimExtractor
from virtualservice import VirtualServiceExtractor
from destinationrule import DestinationRuleExtractor
# from network_policy import NetworkPolicyExtractor
# from statefulset import StatefulSetExtractor

class NamespaceExtractor(Extractor):
    # конструктор
    def __init__(self, kube):
        super().__init__(kube)
        self.name = 'namespace'


    def load(self):
        # загрузка списка нод кластера
        api = client.CoreV1Api(self.kube)
        self.logger.info(f'attempt to load namespaces from {self.kube.configuration.host}')
        namespaces = api.list_namespace()
        self.logger.info(f'loaded {len(namespaces.items)}')
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

            # извлечение SS
            # sets = StatefulSetExtractor(self.kube, namespace)
            # parent = {}
            # parent['item'] = namespace
            # parent['entity'] = self.entity()
            # sets.extract(serializer, parent)

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

            # извлечение Istio Virtural Service
            vservices = VirtualServiceExtractor(self.kube, namespace)
            parent = {}
            parent['item'] = namespace
            parent['entity'] = self.entity()
            vservices.extract(serializer, parent)

            # извлечение Istio Virtural Service
            drules = DestinationRuleExtractor(self.kube, namespace)
            parent = {}
            parent['item'] = namespace
            parent['entity'] = self.entity()
            drules.extract(serializer, parent)

            # извлечение NPs
            # nps = NetworkPolicyExtractor(self.kube, namespace)
            # parent = {}
            # parent['item'] = namespace
            # parent['entity'] = self.entity()
            # nps.extract(serializer, parent)
