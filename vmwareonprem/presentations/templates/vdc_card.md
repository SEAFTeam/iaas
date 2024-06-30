# Virtual Datacenter (VDC)
***  
**Наименование**: {{title}}

| Наименование | DC/IaaS       |
|--------------|---------------|
| {{title}}    | {{&dc_title}} |

{{#vdcg}}
# VDC Groups
![Реестр](@entity/{{entity}}/vdcgroups?id={{id}})
{{/vdcg}}

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