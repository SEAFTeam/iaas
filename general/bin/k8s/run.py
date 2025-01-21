# загрузка параметров из файла с переменными среды
from dotenv import load_dotenv
# для вывода операционной и служебной информации
from pprint import pprint
# для записи объектов в файлы YAML
from serializer import Serializer
# корневой экстрактор для кластеров
from cluster import ClusterExtractor
# журналирование
import logging
import os

# загрузка переменых окружения из файла .env
load_dotenv()

# настройка параметров журналирования
# согласно методологии 12 factors, журналировать надо в stdout, поэтому никаких файлов

logging.basicConfig(
    format='%(asctime)s|%(levelname)s|%(module)s|%(message)s', 
    datefmt='%Y-%m-%d %I:%M:%S', 
    level=os.environ.get('debug.level', 'WARNING').upper())
logger = logging.getLogger(__name__)
logger.info('starting k8s extraction procedure')

try:
    # инициализация сериализатора
    serializer = Serializer()

    # инициализация экстрактора кластеров
    clusters = ClusterExtractor()
    clusters.extract(serializer)
except Exception as error:
    logger.error(error)

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


