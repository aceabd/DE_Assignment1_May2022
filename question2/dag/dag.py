from datetime import timedelta
from airflow.utils.dates import days_ago

from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging

import pandas as pd
import json


LOGGER = logging.getLogger("airflow.task")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': [],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
with DAG(
        'data_transformation',
        default_args=default_args,
        description='data engineering assignment #2',
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['ETL'],
) as dag:
    def generate_id(**kwargs):
        import uuid
        id = uuid.uuid4()
        LOGGER.info('id: ' + str(id))
        ti = kwargs['ti']
        ti.xcom_push(key='file_id', value=str(id))

    generateId = PythonOperator(
        task_id='generate_id',
        python_callable=generate_id,
        provide_context=True,
        dag=dag,
    )

    exportFileCsv = BashOperator(
        task_id='export_table_csv',
        bash_command='psql postgresql://postgres:postgres@de_postgres:5432 -c "\copy tweets to \'/home/airflow/data/{{ti.xcom_pull(key="file_id", task_ids=["generate_id"])[0]}}.csv\' csv header ;"',
        dag=dag
    )

    def convert_to_json(**kwargs):
        ti = kwargs['ti']
        id = ti.xcom_pull(key='file_id', task_ids=['generate_id'])[0]
        df = pd.read_csv('/home/airflow/data/' + str(id) + '.csv')
        df.reset_index(inplace=True)
        dict = df.to_dict("records")
        LOGGER.info(str(dict))
        with open('/home/airflow/data/' + str(id) + '.json', 'w') as file:
            json.dump(dict, file)
        LOGGER.info('conversion to json done')

    convertFileJson = PythonOperator(
        task_id='convert_csv_to_json',
        python_callable=convert_to_json,
        provide_context=True,
        dag=dag,
    )

    installPyMongo = BashOperator(
        task_id='install_pymongo',
        bash_command='pip install pymongo',
    )

    def import_json(**kwargs):
        ti = kwargs['ti']
        id = ti.xcom_pull(key='file_id', task_ids=['generate_id'])[0]

        from pymongo import MongoClient

        client = MongoClient("mongodb://mongoadmin:mongo@de_mongo:27017")

        db = client["Assignment_2"]

        Collection = db["tweets"]

        # Loading or Opening the json file
        with open('/home/airflow/data/' + str(id) + '.json') as file:
            file_data = json.load(file)
            Collection.insert_many(file_data)

    importJsonToMongo = PythonOperator(
        task_id='import_json_to_mongo',
        python_callable=import_json,
        provide_context=True,
        dag=dag
    )

    generateId >> exportFileCsv
    exportFileCsv >> convertFileJson
    convertFileJson >> installPyMongo
    installPyMongo >> importJsonToMongo
