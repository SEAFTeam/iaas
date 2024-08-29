# Deployment [{{title}}]
*** 

| атрибут              | значение            |
|----------------------|---------------------|
| стратегия обновления | {{update_strategy}} |
| количество реплик    | {{replicas}}        |

## контейнеры
{{#containers}}
| {{name}} |  |
|----|----|
| образ | {{image}} |
| обновление | {{image_pull_policy}} |
| порты |  | 
{{#ports}}
| | {{name}}:{{protocol}}:{{port}} |
{{/ports}}
{{/containers}}

