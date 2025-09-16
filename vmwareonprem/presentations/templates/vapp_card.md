# vApp
***  
**Наименование**: {{title}}

| Наименование | VDC                          | Организация    | Датацентр     |
|--------------|------------------------------|----------------|---------------|
| {{title}}     | [{{vdc_title}}]({{vdc_link}}) | {{org_title}}  | {{&dc_title}} |


{{#description}}
## Описание
{{.}}
{{/description}}

{{#networkexists}}
## Сети
{{/networkexists}}
{{#networks}}
**Наименование**: [{{title}}]({{vappnet_link}})

**DNS:** 
{{#dns}}
- {{.}}
{{/dns}}

{{#ipscopes}}
**Gateway**: {{gateway}}

**Fence Mode**: {{fencemode}}

**Диапазоны адресов:**

{{#ipranges}}
- {{startaddress}} - {{endaddress}}
{{/ipranges}}
{{/ipscopes}}
***
{{/networks}}

## Виртуальные машины в vApp
![Реестр](@entity/{{entity}}/vm_list?id={{id}})

## Схема vApp
![Схема](@entity/{{entity}}/schema?id={{id}})


