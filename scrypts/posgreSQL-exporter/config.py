""" pg_secret содержит данные для подключения к postgreSQL АГГ2"""
pg_secret = {'host': '10.127.32.86',
             'user': 'postgres',
             'password': 'Xae4aep9',
             'db_name': 'vts',
             'port': '5432'
             }

"""pg_srcret_estp содержит данные для подколючения к posgreSQL  estp"""
pg_secret_estp = {'host': '10.127.32.90',
                  'user': 'odoo',
                  'password': 'odoo',
                  'db_name': 'estp',
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
