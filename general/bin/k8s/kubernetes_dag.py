import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from kub import kuber, functions
import json
from os import listdir
from os.path import isfile, join


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def kubernetes_dag():

    def get_config(section="kubernetes"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    @task
    def clusters():
        config = get_config()
        path = config["output"]
        clusters = kuber.get_clusters(config)
        return functions.save(clusters, path, "clusters")

    git = get_config("git")
    k8s = get_config("k8s")

    push = BashOperator(
        task_id="push",
        bash_command="{} {} ".format(
            git.get("push_script"), git.get("output_dir"))
    )

    run = BashOperator(
        task_id = 'run_k8s_extract',
        bash_command = "python run.py",
        cwd = '/opt/airflow/dags/k8s',
        env = {
            "configFile" : k8s.get("configFile"),
            "targetFolder" : git.get("output_dir")
        }
    )

    run >> push

kubernetes_dag()
