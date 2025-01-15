### Скрипты выгрузки данных из Облака VMware

Подключите необходимые библиотеки:
* requests
* os
* json
* yaml
* lxml
* re
* math
* configparser
* sys

Заполните конфигурационный файл:
```console
[connection]
access_token = [your access token if exists, do not fill both refresh and access]
refresh_token = [your refresh token, do not fill both refresh and access]
host = [vcd dns name]
tenant = [tenant name]

[params]
domain = [company domain (prefix)]
root = sber
exportpath = [export folder path]
DC = [DataCenter id from TA]   
```
Запустите выгрузку и подключите выгруженные файлы с помощью **imports:**