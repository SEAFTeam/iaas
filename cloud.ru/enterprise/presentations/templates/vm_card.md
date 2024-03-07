# Сервер
***  
**Наименование**: {{name}}

| Наименование | IP адреса                         | Subnet     | VDC     | DC/IaaS |
|--------------|-----------------------------------|------------|---------|---------|
| {{name}}     | {{#addresses}}{{.}}{{/addresses}} | {{subnet}} | {{vdc}} | {{dc}}  |

{{#description}}
## Описание
{{.}}
{{/description}}

{{#backup}}
## Backup Policies
![Получаем данные о резервном копировании](@entity/seaf.ta.reverse.cloud_ru.advanced.backup_policies/server_backup?id={{id}})
{{/backup}}

{{#firewall}}
## Firewall Rules

{{#sg}}
**{{name}}**
![Получаем данные об ACL](@entity/seaf.ta.reverse.cloud_ru.advanced.security_groups/table_view?id={{sg_id}})

{{/sg}}
{{/firewall}}
