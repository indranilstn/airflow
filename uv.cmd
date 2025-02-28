uv pip compile requirements.in --constraint airflow-constraints-3.12.txt -o requirements.txt
uv pip install * --constraint airflow-constraints-3.12.txt --cache-dir .cache

sudo service rabbitmq-server restart
