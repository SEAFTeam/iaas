# Network
***  
**Наименование**: {{name}}

| Наименование | Connected                        | Type     | VDC                          | Организация                  |
|--------------|----------------------------------|----------|------------------------------|------------------------------|
| {{name}}     | {{connected}} | {{type}} | [{{vdc_name}}]({{vdc_link}}) | [{{org_name}}]({{org_link}}) |


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


