# Network
***  
**Наименование**: {{name}}

| Наименование | Connected                        | Type     | VDC                          | VDC Group                              | Организация                  | DC/IaaS |
|--------------|----------------------------------|----------|------------------------------|----------------------------------------|------------------------------|-----|
| {{name}}     | {{connected}} | {{type}} | [{{vdc_name}}]({{vdc_link}}) | [{{vdcgroup_name}}]({{vdcgroup_link}}) | [{{org_name}}]({{org_link}}) | {{&dc_name}} |


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
![Схема](@entity/{{entity}}/schema?id={{id}})


