# класс извлечения данных по кластеру
import sys
from urllib.parse import urlparse
# API k8s для Python
from kubernetes import client, config
# импорт базового класса
from extractor import Extractor
from node import NodeExtractor
from namespace import NamespaceExtractor
from pv import PersistentVolumeExtractor

class ClusterExtractor(Extractor):
    # конструктор
    def __init__(self):
        super().__init__(None)
        self.name = 'cluster'

    def load(self):
        # загрузка контекстов конфигурации kubectl
        contexts, current = config.list_kube_config_contexts()

        for context in contexts:
            ctxName = context['name']
            kube = config.new_client_from_config(None, ctxName)
            context['cluster_fqdn'] = urlparse(kube.configuration.host).hostname

        return contexts

    def children(self, serializer, items):
        for context in items:
            ctxName = context['name']
            kube = config.new_client_from_config(None, ctxName)
            #api = client.CoreV1Api(kube)

            # выгрузка нод
            nodes = NodeExtractor(kube)
            parent = {}
            parent['item'] = context
            parent['entity'] = self.entity()
            nodes.extract(serializer, parent)

            # выгрузка namespaces
            namespaces = NamespaceExtractor(kube)
            parent = {}
            parent['item'] = context
            parent['entity'] = self.entity()
            namespaces.extract(serializer, parent)

            # выгрузка namespaces
            pvs = PersistentVolumeExtractor(kube)
            parent = {}
            parent['item'] = context
            parent['entity'] = self.entity()
            pvs.extract(serializer, parent)
            # выгрузка namespace

            #for namespace in namespaces.items:
            #    deployments = DeploymentExtractor(client.AppsV1Api(kube), namespace)
            #    parent = {}
            #    parent['item'] = namespace
            #    parent['entity'] = namespaces.entity()
            #    deployments.extract(serializer, parent)

#this = sys.modules[__name__]

#entity name
#this.entity = "cluster"
#k8s API object
#this.kube = {}

# init iterator with context
#def init(kube):
#    this.kube = kube

#def next(name):
#    cluster = {}
#    cluster['kubernetes_id'] = name
#    cluster['cluster_fqdn'] = urlparse(this.kube.configuration.host).hostname
#    return cluster
