# загрузка параметров из файла с переменными среды
from dotenv import load_dotenv
# API k8s для Python
from kubernetes import client, config
# для вывода операционной и служебной информации
from pprint import pprint
import serializer, cluster, node, namespace

# загрузка переменых окружения из файла .env
load_dotenv()

# формирование контекста импорта
components = [
    cluster,
    node,
    namespace
]

serializer.init(components)
#загрузка контекстов конфигурации kubectl
contexts, current = config.list_kube_config_contexts()
#перебираем по контексту
for context in contexts:
    ctxName = context['name']
    print(f'using context [%s]' % (ctxName))
    kube = config.new_client_from_config(None, ctxName)
    cluster.init(kube)
    # загрузка кластера
    item = cluster.next(ctxName)
    serializer.serialize(item, cluster, None, None)
    # для кажого кластера грузим ноды
    node.init(kube)
    serializer.serialize(node.next(), node, item, cluster)
    namespace.init(kube)
    serializer.serialize(namespace.next(), namespace, item, cluster)


