# vApp
***  
**Наименование**: {{name}}

| Наименование | VDC                          | Организация                  |
|--------------|------------------------------|------------------------------|
| {{name}}     | [{{vdc_name}}]({{vdc_link}}) | [{{org_name}}]({{org_link}}) |


{{#description}}
## Описание
{{.}}
{{/description}}

{{#networkexists}}
## Сети
{{/networkexists}}
{{#networks}}
**Наименование**: [{{name}}]({{vappnet_link}})

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


