# Network
***  
**Наименование**: {{title}}

| Наименование | Type     | VDC                          | DC/IaaS |
|--------------|----------|------------------------------|-----|
| {{title}}     | {{type}} | [{{vdc_title}}]({{vdc_link}}) | {{&dc_title}} |


{{#description}}
## Описание
{{.}}
{{/description}}

{{#ipscopes}}
**Диапазоны адресов:**

{{#ipranges}}
- {{startaddress}} - {{endaddress}}
{{/ipranges}}
{{/ipscopes}}

## Схема сети
{{#vdc}}
![Схема](@entity/{{entity}}/schema?id={{id}})
{{/vdc}}
