import sys
from urllib.parse import urlparse

this = sys.modules[__name__]

#entity name
this.entity = "cluster"
#k8s API object
this.kube = {}

# init iterator with context
def init(kube):
    this.kube = kube

def next(name):
    cluster = {}
    cluster['kubernetes_id'] = name
    cluster['cluster_fqdn'] = urlparse(this.kube.configuration.host).hostname
    return cluster
