# Сервер
***  
**Наименование**: {{name}}

| Наименование | Статус     | IP адреса                                       | Описание | Subnet     | VPC     | Датацентр |
|--------------|------------|-------------------------------------------------|----------|------------|---------|-----------|
| {{name}}     | {{status}} | {{#ip_addresses}}{{address}}  {{/ip_addresses}} |  {{description}}        | {{subnet}} | {{vpc}} | {{dc}}    |

{{#system_exists}}
## Система, система КБ или технический сервис
|Наименование| Тип |Идентификатор|Описание|
|------------|-----|-------------|--------|
{{/system_exists}}
{{#systems}}
|[{{title}}]({{link}})|{{link_type}}|{{id}}|{{description}}|
{{/systems}}

## Backup Policies
![Получаем данные о резервном копировании](@entity/seaf.ta.reverse.cloud_ru.advanced.backup_policies/server_backup?id={{id}}&domain={{domain}})

## Firewall Rules
![Получаем данные об ACL](@entity/seaf.ta.reverse.cloud_ru.advanced.security_groups/list_for_servers?id={{id}}&domain={{domain}})


