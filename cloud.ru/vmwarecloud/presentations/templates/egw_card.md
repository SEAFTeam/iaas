# Edge Gateway
***  
**Наименование**: {{title}}

| Наименование | Type     | VDC                          | VDC Group                              | Организация                  |  DC/IaaS    |
|--------------|----------|------------------------------|----------------------------------------|------------------------------|-----|
| {{title}}     | {{type}} | [{{vdc_title}}]({{vdc_link}}) | [{{vdcgroup_title}}]({{vdcgroup_link}}) | [{{org_title}}]({{org_link}}) | {{&dc_title}}   |

{{#description}}
## Описание
{{.}}
{{/description}}

## Адреса
{{#addresses}}
- {{.}}
{{/addresses}}

## Адреса NAT
{{#nataddresses}}
- {{.}}
{{/nataddresses}}

## Параметры сетей
![Сети](@entity/{{entity}}/networks_list?id={{id}})

## DNAT
![Сети](@entity/{{egws_nat_entity}}/dnat_list?id={{id}})

## SNAT
![Сети](@entity/{{egws_nat_entity}}/snat_list?id={{id}})

## Firewall Rules
![FW](@entity/{{egws_fw_entity}}/egw_rules_list?id={{id}})
***

## Схема 
{{^vdcgroup}}
{{#vdc}}
![Схема](@entity/{{entity}}/schema?id={{id}})
{{/vdc}}
{{/vdcgroup}}
{{#vdcgroup}}
![Схема](@entity/{{entity}}/schema_vdcgroup?id={{id}})
{{/vdcgroup}}



