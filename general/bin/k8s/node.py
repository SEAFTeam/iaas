import sys
from pprint import pprint
from kubernetes import client

this = sys.modules[__name__]

#entity name
this.entity = "node"
#k8s API object
this.kube = {}

# init iterator with context
def init(kube):
    this.kube = kube

def next():
    api = client.CoreV1Api(this.kube)
    # получаем список нод кластера
    nodes = api.list_node()
    #pprint(nodes)
    return nodes

