# Сервер
***  
**Наименование**: {{name}}

| Наименование | IP адреса                         | vApp Networks | vApp                      | VDC                     | DC/IaaS      |
|--------------|-----------------------------------|---------------|---------------------------|-------------------------|--------------|
| {{name}}     | {{#addresses}}{{.}}{{/addresses}} | {{subnet}}    | [{{vapp}}]({{vapp_link}}) | [{{vdc}}]({{vdc_link}}) | {{&dc_name}} |

{{#description}}
## Описание
{{.}}
{{/description}}

