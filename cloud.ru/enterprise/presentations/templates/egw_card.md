# Edge Gateway
***  
**Наименование**: {{name}}

| Наименование | Type     | VDC                          | VDC Group                              | Организация                  |  DC/IaaS    |
|--------------|----------|------------------------------|----------------------------------------|------------------------------|-----|
| {{name}}     | {{type}} | [{{vdc_name}}]({{vdc_link}}) | [{{vdcgroup_name}}]({{vdcgroup_link}}) | [{{org_name}}]({{org_link}}) | {{&dc_name}}   |

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
![Схема](@entity/{{entity}}/schema?id={{id}})


