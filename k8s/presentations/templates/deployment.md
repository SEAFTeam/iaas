# Deployment [{{name}}]
*** 

| атрибут         | значение           |
|----------------------|--------------------|
| Стратегия обновления | {{updateStrategy}} |
| Количество реплик    | {{replicas}}       |

## контейнеры
{{#containers}}
| {{name}} |  |
|----|----|
| образ | {{image}} |
| обновление | {{imagePullPolicy}} |
| порты |  | 
{{#ports}}
| | {{name}}:{{protocol}}:{{port}} |
{{/ports}}
{{/containers}}

