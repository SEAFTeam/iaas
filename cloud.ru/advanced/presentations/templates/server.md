# Сервер
***  
**Наименование**: {{name}}

| Наименование | Статус     | IP адреса                                       | Описание | Subnet     | VPC     | DC/IaaS |
|--------------|------------|-------------------------------------------------|----------|------------|---------|---------|
| {{name}}     | {{status}} | {{#ip_addresses}}{{address}}  {{/ip_addresses}} |  {{description}}        | {{subnet}} | {{vpc}} | {{dc}}  |

{{#system_title}}
## Система
**Наименование**: [{{system_title}}]({{system_link}})   
**Идентификатор**: {{system_id}}   
**Описание**: {{system_description}}    
{{/system_title}}

## Backup Policies
![Получаем данные о резервном копировании](@entity/seaf.ta.reverse.cloud_ru.advanced.backup_policies/server_backup?id={{id}}&domain={{domain}})

## Firewall Rules
![Получаем данные об ACL](@entity/seaf.ta.reverse.cloud_ru.advanced.security_groups/list_for_servers?id={{id}}&domain={{domain}})


