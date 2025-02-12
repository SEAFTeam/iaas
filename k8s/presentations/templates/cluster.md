# Кластер Kubernetes
***  
**Наименование**: {{id}}

| атрибут    | значение           |
|------------|--------------------|
| Cluster ID | **{{cluster_id}}** |
| FQDN | **{{fqdn}}**       |
| нод        | **{{node_count}}** | 

ABC: 

## Ноды кластера
![Получаем ноды кластера](@entity/{{ kube_config.cluster.entity }}/nodes?id={{cluster_id}})

## Namespaces
![Получаем ns кластера](@entity/{{ kube_config.cluster.entity }}/namespaces?id={{cluster_id}})




