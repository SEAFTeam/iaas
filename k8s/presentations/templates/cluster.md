# Кластер Kubernetes
***  
**Наименование**: {{cluster_id}}

| атрибут    | значение           |
|------------|--------------------|
| Cluster ID | **{{cluster_id}}** |
| FQDN | **{{fqdn}}**       |
| нод        | **{{node_count}}** |
## Схемы

[внешние сервисы кластера](/entities/{{ kube_config.cluster.entity }}/ports?id={{id}})

## Namespaces
![Получаем ns кластера](@entity/{{ kube_config.cluster.entity }}/namespaces?id={{cluster_id}})

## Ноды кластера
![Получаем ноды кластера](@entity/{{ kube_config.cluster.entity }}/nodes?id={{cluster_id}})
