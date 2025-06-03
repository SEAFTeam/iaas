# базовый класс извлекателя данных из инфраструктуры
import os
from pprint import pprint
import logging
import json

class Extractor:
    # конструктор
    def __init__(self, kube):
        # объект для доступа к данным
        self.kube = kube
        self.name = ''
        # инициализация журнала
        self.logger = logging.getLogger(__name__)
        #self.items = {}

    # непосредственно извлечение
    def extract(self, serializer, parent = None):
        items = self.load()

        if len(items) == 0:
            return

        if (os.environ.get('debug.dump') is not None) :
            debugClasses = os.environ.get('debug.dump').split(',')
            if(any(self.name == item for item in debugClasses)) :
                print(f'ENTITIES: {self.name}')
                pprint(items)

        # формирование идентификаторов, нейтральных с т.з. движков отображения
        # for item in items:
        #    if hasattr(item, 'metadata') and hasattr(item.metadata, 'uid'):
        #        item.safeID = f'G{item.metadata.uid.replace("-", "")}'

        # формирование контекста
        context = {}
        context['entity'] = self.entity()
        context['items']  = items
        context['parent'] = parent

        # тут где-то должен быть родительский объект
        serializer.serialize(self, context)
        self.children(serializer, items)

    # загрузка данных экстрактора - базовая заглушка
    def load(self):
        pass

    # если что-то нужно сделать перед сериализацией каждого элемента
    def before(self, item):
        pass

    # получение названия сущности компонента
    def entity(self):
        return os.environ.get(f'root.{self.name}')

    # извлечение дочерних объектов
    def children(self, serializer, items):
        pass