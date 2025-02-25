from kubernetes import client
# базовый класс
from extractor import Extractor
from pprint import pprint
import json
from types import SimpleNamespace

class DestinationRuleExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'drule'
        self.parent = namespace.metadata.name

    def load(self):
        group = 'networking.istio.io'
        version = 'v1'
        plural = 'destinationrules'
        api = client.CustomObjectsApi(self.kube)
        res = api.list_namespaced_custom_object(group, version, self.parent, plural, pretty = 'true')
        return res.items()


