# DAG - directed acyclic graph
# ETL workflow for MooVitamix data ingestion

# Tasks:
# 1) Extract data from FastAPI (extract)
# 2) Transform data with pandas (transform)
# 3) Create and store transformed data in PostgreSQL tables (load)

# Operators: PythonOperator, PostgresOperator
# Hooks: PostgreSQL connection via psycopg2
# Dependencies

from datetime import datetime, timedelta
from airflow import DAG
#from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import PythonOperator

#from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator


import requests
import pandas as pd
import psycopg2

# API base URL for data extraction
base_url = "http://host.docker.internal:8000/"

# Functions for ETL tasks

# 1) Extract data from FastAPI
def extract_data():
    # Fetch data from FastAPI endpoints
    tracks = requests.get(f"{base_url}/tracks").json()
    users = requests.get(f"{base_url}/users").json()
    listen_history = requests.get(f"{base_url}/listen_history").json()
    
    # Return the data to be used in transformation
    return {
        'tracks': tracks['items'],
        'users': users['items'],
        'listen_history': listen_history['items']
    }

# 2) Transform data into DataFrames
def transform_data(ti):
    # Retrieve extracted data from XCom
    data = ti.xcom_pull(task_ids='extract_data')
    
    # Transform data into DataFrames
    df_tracks = pd.DataFrame(data['tracks'])
    df_users = pd.DataFrame(data['users'])
    df_listen_history = pd.DataFrame(data['listen_history'])
    
    # Return transformed data as dictionary
    return {
        'tracks': df_tracks.to_dict('records'),
        'users': df_users.to_dict('records'),
        'listen_history': df_listen_history.to_dict('records')
    }

# 3) Load data into PostgreSQL
def load_data(ti):
    # Retrieve transformed data from XCom
    data = ti.xcom_pull(task_ids='transform_data')
    
    # Database connection setup
    conn = psycopg2.connect(
        dbname="playlist",
        user="airflow",
        password="airflow",
        host="172.18.0.3"
    )
    cur = conn.cursor()
    
    # Insert data into PostgreSQL tables
    for table, records in data.items():
        for record in records:
            columns = ', '.join(record.keys())
            values = ', '.join(['%s'] * len(record))
            insert_query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            cur.execute(insert_query, list(record.values()))
    
    conn.commit()
    cur.close()
    conn.close()

# DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize the DAG
dag = DAG(
    dag_id='moovitamix_etl',
    default_args=default_args,
    description='ETL for MooVitamix data ingestion',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Operators
# Extract data from API
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

# Transform data with pandas
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

create_tables_task = PostgresOperator(
    task_id='create_tables',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY,
        name VARCHAR(255),
        artist VARCHAR(255),
        songwriters VARCHAR(255),
        duration VARCHAR(10),
        genres VARCHAR(255),
        album VARCHAR(255),
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        email VARCHAR(255),
        gender VARCHAR(50),
        favorite_genres VARCHAR(255),
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS listen_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        items INTEGER[],
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    dag=dag,
)

# Load data into PostgreSQL
load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

# Dependencies
extract_task >> transform_task >> create_tables_task >> load_task
