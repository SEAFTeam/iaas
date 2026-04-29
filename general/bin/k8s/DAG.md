Для того, чтобы интегрировать DAG в существующую инсталляцию AF, небходимо сделать следующие шаги.

* Скопировать DAG в AF в папку dags
* Скопировать содержимое данного каталога в папку dags/k8s
* Сформировать в папке dags/k8s файл .env из sample, удалив оттуда targetFolder и configFile
* Конфиг k8s необходимо разместить так же в папке dags/k8s с именем kube.config
* Добавить в AF в confis/variables.json секцию:
 
 "k8s": {
  "configFile": "/opt/airflow/dags/k8s/kube.config"
  }
 
Файлы будут формироваться в каталоге, указанном в git.output_dir файла variables.json в AF
