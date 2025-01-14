# Virtual Datacenter (VDC)
***  
**Наименование**: {{title}}

| Наименование | DC/IaaS       |
|--------------|---------------|
| {{title}}    | {{&dc_title}} |

{{#description}}
## Описание
{{.}}
{{/description}}

{{#hosts}}
## Хосты
![Реестр](@entity/{{entity}}/hosts?id={{id}})
{{/hosts}}

{{#networks}}
## Сети
![Реестр](@entity/{{entity}}/networks?id={{id}})
{{/networks}}

{{#vapps}}
## vApps
![Реестр](@entity/{{entity}}/vapps?id={{id}})
{{/vapps}}

## Схема

![Схема](@entity/{{entity}}/schema?id={{id}})
