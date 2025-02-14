from kubernetes import client
# базовый класс
from extractor import Extractor
from pprint import pprint
import json
from types import SimpleNamespace

class VirtualServiceExtractor(Extractor):
    # конструктор
    def __init__(self, kube, namespace):
        super().__init__(kube)
        self.name = 'vservice'
        self.parent = namespace.metadata.name

    def load(self):
        # загрузка списка нод кластера
        group = 'networking.istio.io'
        version = 'v1'
        plural = 'virtualservices'
        api = client.CustomObjectsApi(self.kube)
        res = api.list_namespaced_custom_object(group, version, self.parent, plural, pretty = 'true')
        # тут я не разобрался до конца - возвращается не обычный объект, а dictionary, и всё разваливается
        # поэтому сначала в строку, потом в объект
        tmp = json.dumps(res)
        vservices = json.loads(tmp, object_hook=lambda d: SimpleNamespace(**d))
        return vservices.items

