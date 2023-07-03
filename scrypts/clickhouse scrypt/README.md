# Работа с очередями RabbitMQ скрипт миграции из БД Posgresql в бд ClickHouse
Представлены несколько скриптов: скрипт для получения данных из БД Posgresql и отправки этих данных в RabbitMQ, а также скрипт для разбора очереди RabbitMQ и миграция полученных данных в бд ClickHouse.


### Файл конфигурации

Пример готового файла:
```py
""" pg_secret содержит данные для подключения к postgreSQL АГ2"""
agg_secret = {'host': 'localhot',
              'user': 'postgres',
              'password': 'postgres',
              'db_name': 'vts',
              'port': '5432'
              }

""" содержит данные подключения к rabbit_mq """
rabbit_secret = {'host': '127.0.0.1',
                 'username': 'mqadmin',
                 'password': 'mqadmin',
                 'port': '5672',
                 'exchange': 'workers',
                 'virtualHost': '/',
                 'exchange_type': 'direct',
                 'queue': 'workers_queue1'
                 }
                 
kh_secret = {'host': '127.0.0.1',
             'user': 'default',
             'password': '',
             'db_name': 'default',
             'port': '8123'
             }
```

