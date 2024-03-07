# Virtual Datacenter (VDC)
***  
**Наименование**: {{name}}

| Наименование | Зона                     | Организация  |
|--------------|--------------------------|--------------|
| {{name}}     | {{computeproviderscope}} | {{org_name}} |

{{#description}}
## Описание
{{.}}
{{/description}}

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
