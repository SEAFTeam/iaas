import sys
from pprint import pprint
from kubernetes import client

this = sys.modules[__name__]

#entity name
this.entity = "namespace"
#k8s API object
this.kube = {}

# init iterator with context
def init(kube):
    this.kube = kube
    this.api = client.CoreV1Api(this.kube)
    this.namespaces = this.api.list_namespace().items
    #pprint(this.namespaces)

def next():
    # получаем список нод кластера
    #pprint(nodes)
    return this.namespaces

