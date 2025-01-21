# загрузка параметров из файла с переменными среды
from dotenv import load_dotenv
# k8s API configuration
from kubernetes import config
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
    # загрузка конфигурации
    logger.info("loading k8s config")
    # config.load_kube_config("C:\\Users\\priva\\.kube\\config-local")
    # инициализация сериализатора
    serializer = Serializer()
    # инициализация экстрактора кластеров
    clusters = ClusterExtractor(os.environ.get('configFile', None))
    clusters.extract(serializer)
except Exception as error:
    logger.error(error)
