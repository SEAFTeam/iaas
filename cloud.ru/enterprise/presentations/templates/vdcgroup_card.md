# Virtual Datacenter Group (VDC Group)
***  
**Наименование**: {{name}}

| Наименование | Организация  | DC/IaaS      |
|--------------|--------------|--------------|
| {{name}}     | [{{org_name}}]({{org_link}}) | {{&dc_name}} |

{{#description}}
## Описание
{{.}}
{{/description}}

{{#networks}}
## Сети
![Реестр](@entity/{{entity}}/networks?id={{id}})
{{/networks}}

{{#vdcs}}
## VDCs
![Реестр](@entity/{{entity}}/vdcs?id={{id}})
{{/vdcs}}

## Схема

![Схема](@entity/{{entity}}/schema?id={{id}})
