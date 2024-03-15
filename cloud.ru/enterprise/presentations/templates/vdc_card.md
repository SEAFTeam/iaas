# Virtual Datacenter (VDC)
***  
**Наименование**: {{name}}

| Наименование | Организация  | DC/IaaS    |
|--------------|--------------|-----|
| {{name}}     | [{{org_name}}]({{org_link}}) | {{&dc_name}} |

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
