# Virtual Datacenter Group (VDC Group)
***  
**Наименование**: {{title}}

| Наименование | Организация  | DC/IaaS      |
|--------------|--------------|--------------|
| {{title}}     | [{{org_title}}]({{org_link}}) | {{&dc_title}} |

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
