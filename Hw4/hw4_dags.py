from datetime import datetime, timedelta
from textwrap import dedent
import time

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization


####################################################
# DEFINE PYTHON FUNCTIONS
####################################################

count = 0

def sleeping_function():
    time.sleep(2)

def count_function():
    global count
    count += 1
    print('count_increase output: {}'.format(count))
    time.sleep(2)

def current_time_function():
    print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
   

say_hi = "echo hello world"
sleep = "sleep 3"
pwd = "pwd"

############################################
# DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################

default_args = {
    'owner': 'yizhang',
    'depends_on_past': False,
    'email': ['yz4130@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=30),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

with DAG(
    'hw4_dags',
    default_args=default_args,
    description='EECS6893 Homework 4 DAG',
    schedule_interval=timedelta(minutes=30),
    start_date=datetime(2022, 11, 29),
    catchup=False,
    tags=['example'],
) as dag:

##########################################
# DEFINE AIRFLOW OPERATORS
##########################################

    # t* examples of tasks created by instantiating operators

    t1 = BashOperator(
        task_id='t1',
        bash_command=pwd
    )

    t2 = BashOperator(
        task_id='t2',
        bash_command=say_hi
    )

    t3 = BashOperator(
        task_id='t3',
        bash_command=sleep
    )

    t4 = PythonOperator(
        task_id='t4',
        python_callable=count_function
    )
    
    t5 = BashOperator(
        task_id='t5',
        bash_command=sleep
    )


    t6 = BashOperator(
        task_id='t6',
        bash_command=say_hi
    )
    
    t7 = PythonOperator(
        task_id='t7',
        python_callable=current_time_function
    )
    
    t8 = PythonOperator(
        task_id='t8',
        python_callable=sleeping_function
    )
    
    t9 = BashOperator(
        task_id='t9',
        bash_command=say_hi
    )
    
    t10 = BashOperator(
        task_id='t10',
        bash_command=pwd
    )
    
    t11 = PythonOperator(
        task_id='t11',
        python_callable=current_time_function
    )
            
    t12 = PythonOperator(
        task_id='t12',
        python_callable=sleeping_function
    )
      
    t13 = BashOperator(
        task_id='t13',
        bash_command=sleep
    )
        
    t14 = BashOperator(
        task_id='t14',
        bash_command=sleep
    )
       
    t15 = PythonOperator(
        task_id='t15',
        python_callable=count_function
    )
    
    t16 = PythonOperator(
        task_id='t16',
        python_callable=count_function
    )
            
    t17 = BashOperator(
        task_id='t17',
        bash_command=say_hi
    )
    
    t18 = BashOperator(
        task_id='t18',
        bash_command=pwd
    )
            
    t19 = PythonOperator(
        task_id='t19',
        python_callable=sleeping_function
    )    
    
##########################################
# DEFINE TASKS HIERARCHY
##########################################

    # task dependencies 
 
    t1 >> [t5, t2, t3, t4]
    t5 >> [t8, t9]
    t2 >> t6
    t3 >> [t12, t7]
    t8 >> [t10, t15]
    t9 >> [t11, t12]
    t7 >> [t14, t18, t13]
    [t10, t11, t12] >> t14
    t15 >> t18
    t14 >> [t16, t17]
    [t17, t15, t13] >> t18
    [t16, t18] >> t19
        
    
    
    

