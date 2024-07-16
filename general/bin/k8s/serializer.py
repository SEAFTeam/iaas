# класс и модуль сериализатор объектов reverse engineering
import os
import chevron

# синтаксис mustache не предполагает итерацию по атрибутам объектов
# поэтому пришлось написать свою функцию, которая превращает атрибуты объектов в массив
def iterator(text, render):
    #pprint(text)
    #pprint("->" + render(text) + "<-")
    parts = render(text).split("@kv")
    output = ""
    prefix = parts[0]
    data   = eval(parts[1])
    #pprint(data.keys())
    for key in data.keys():
        output = output + f'{prefix}{key}: {data[key]}\n'
    return output

# класс с логикой сериализации
class Serializer:
    # конструктор
    def __init__(self):
        # инициализация переменной путём к каталогу, в который будет производиться запись
        self.target = os.environ.get('targetFolder')
        # если каталог не задан, то тут нам больше делать нечего
        if self.target is None:
            raise Exception("targetFolder environment variable not found")

        # маркер проведённой инициализации компонентов
        self.inits = {}

    # инициализация файла вывода, связанного с компонентом
    def init(self, component):
        # полный путь и имя файла для инициализации YAML структуры
        fileName = self.output(component)
        # инициализация YAML файла
        with open(fileName, mode="wt", encoding="utf-8") as file:
            print(f'{component.entity()}:', file=file)

    # функция формирования файла для записи сущностей типа компонента
    def output(self, component):
        # формирование имени файла
        fileName = f'{self.target}/{component.name}.yaml'
        return fileName

    # запись извлечённого объекта в файл типа компонента
    # структура контекста:
    # {
    #    entity: класс сериализуемой сущности
    #    items: массив выгруженных сущностей
    #    parent: родительская сущность
    #    {
    #       entity: класс родительской сущности
    #       item: родительская сушность
    #    }
    # }
    def serialize(self, component, context):
        # проверка, был ли инициализирован компонент
        if component.name not in self.inits:
            self.inits[component.name] = True
            self.init(component)

        # полный путь и имя YAML файла для сериализации
        output = self.output(component)
        # путь и имя файла шаблона, они должны располагаться в каталоге template относительно текущего каталога
        template = f'templates/{component.name}.mustache'

        context["iterator"] = iterator
        # читаем шаблон и рендерим итоговые данные
        with open(template, 'r') as f:
            data = chevron.render(f, context)

        # запись сформированной выгрузки в конец файла
        with open(output, 'a') as out:
            out.write(data)


