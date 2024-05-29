import os
import chevron

# инициализация загрузчиков и форматов
def init(components):

    # проверка необходимых для запуска переменных
    targetFolder = os.environ.get('targetFolder')
    if targetFolder is None:
        raise Exception("targetFolder environment variable not found")

    # настройка параметров для каждого компонента
    for component in components:
        entity = component.entity
        rootEntity = getRootEntiry(component)

        fileName = f'{targetFolder}/{entity}.yaml'

        with open(fileName, mode="wt", encoding="utf-8") as file:
            print(f'{rootEntity}:', file=file)

def getRootEntiry(component):
    entity = component.entity
    rootEntity = os.environ.get(f'root.{entity}')
    if rootEntity is None:
        raise Exception(f'root entity for [{entity}] not found in environment variables - [root.{entity}] expected')

    return rootEntity

def serialize(items, component, parent, parentComponent):
    entity = component.entity
    rootEntity = getRootEntiry(component)
    parentEntity = {}

    if(parentComponent is not None):
        parentEntity = getRootEntiry(parentComponent)

    targetFolder = os.environ.get('targetFolder')
    fileName = f'{targetFolder}/{entity}.yaml'
    templateFile = f'templates/{entity}.mustache'
    context = {}
    context['items'] = items
    context['entity'] = rootEntity
    context['parent'] = parent
    context['parentEntity'] = parentEntity
    with open(templateFile, 'r') as f:
        item = chevron.render(f, context)

    with open(fileName, 'a') as out:
        out.write(item)
