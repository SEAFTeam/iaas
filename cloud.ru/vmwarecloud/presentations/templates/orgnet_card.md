# Network
***  
**Наименование**: {{title}}

| Наименование | Connected                        | Type     | VDC                          | VDC Group                              | Организация                  | DC/IaaS |
|--------------|----------------------------------|----------|------------------------------|----------------------------------------|------------------------------|-----|
| {{title}}     | {{connected}} | {{type}} | [{{vdc_title}}]({{vdc_link}}) | [{{vdcgroup_title}}]({{vdcgroup_link}}) | [{{org_title}}]({{org_link}}) | {{&dc_title}} |


{{#description}}
## Описание
{{.}}
{{/description}}


## Параметры сети

**Gateway**: {{gateway}}

**Fence Mode**: {{fencemode}}

**DNS:** 
{{#dns}}
- {{.}}
{{/dns}}

{{#ipscopes}}
**Диапазоны адресов:**

{{#ipranges}}
- {{startaddress}} - {{endaddress}}
{{/ipranges}}
{{/ipscopes}}
***

## Схема сети
{{^vdcgroup}}
{{#vdc}}
![Схема](@entity/{{entity}}/schema?id={{id}})
{{/vdc}}
{{/vdcgroup}}

{{#vdcgroup}}
![Схема](@entity/{{entity}}/schema_vdcgroup?id={{id}})
{{/vdcgroup}}