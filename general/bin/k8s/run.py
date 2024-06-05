# загрузка параметров из файла с переменными среды
from dotenv import load_dotenv
# для вывода операционной и служебной информации
from pprint import pprint
from serializer import Serializer
from cluster import ClusterExtractor

# загрузка переменых окружения из файла .env
load_dotenv()

# инициализация сериализатора
serializer = Serializer()

# инициализация экстрактора кластеров
clusters = ClusterExtractor()
clusters.extract(serializer)

#перебираем по контексту
# for context in contexts:
#    ctxName = context['name']
#    print(f'using context [%s]' % (ctxName))
#    kube = config.new_client_from_config(None, ctxName)
#    cluster.init(kube)
    # загрузка кластера
#    item = cluster.next(ctxName)
#    serializer.serialize(item, cluster, None, None)
    # для кажого кластера грузим ноды
#    node.init(kube)
#    serializer.serialize(node.next(), node, item, cluster)
#    namespace.init(kube)
#    serializer.serialize(namespace.next(), namespace, item, cluster)


