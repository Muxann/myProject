import psycopg2
from psycopg2.extras import RealDictCursor
import pika
import datetime
import json
from config import *


def data_partition():
    return input("название партиции sh_dwh.bnso_data_t(yyyymmdd). введите дату партиции в формате 'yyyymmdd: ")


def datetime_handler(x):
    if isinstance(x, datetime.date):
        return x.strftime("%Y-%m-%dT%H:%M:%S%z")


if __name__ == "__main__":
    try:
        connection = psycopg2.connect(
            host=agg_secret['host'],
            user=agg_secret['user'],
            password=agg_secret['password'],
            database=agg_secret['db_name'],
            port=agg_secret['port']
        )
        print("[INFO] Connect to exist database PostgresSQL")

        credentials = pika.PlainCredentials(rabbit_secret['username'],
                                            rabbit_secret['password'])

        parameters = pika.ConnectionParameters(rabbit_secret['host'],
                                               rabbit_secret['port'],
                                               rabbit_secret['virtualHost'],
                                               credentials)

        connect_rabit = pika.BlockingConnection(parameters)
        channel = connect_rabit.channel()

        channel.exchange_declare(exchange=rabbit_secret['exchange'], exchange_type=rabbit_secret['exchange_type'])
        channel.queue_declare(queue=rabbit_secret['queue'], durable=True)
        channel.queue_bind(exchange=rabbit_secret['exchange'], queue=rabbit_secret['queue'])
        # ----------------------------------------------------------------------
        print("[INFO] Connect to exist RabbitMQ")
        # запрос в бд postgresSQL
        query = f"SELECT * FROM sh_dwh.bnso_data_t{data_partition()}"

        print("[INFO] Connection to PostgresSQL database established:")

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            print("[INFO] Getting a query from Postgresql:")

            for row in cursor:
                row['bnso_code'] = int(row['bnso_code'])
                row['lon'] = float(row['lon'])
                row['lat'] = float(row['lat'])
                row['speed'] = int(row['speed'])
                row['car_owner_id'] = int(row['car_owner_id'] or 0)
                row['altitude'] = int(row['altitude'])
                channel.basic_publish(exchange=rabbit_secret['exchange'],
                                      routing_key=rabbit_secret['queue'],
                                      body=json.dumps(row, default=datetime_handler),
                                      properties=pika.BasicProperties(delivery_mode=2, )
                                      )
        connect_rabit.close()
        print("[INFO] RabbitMQ connection closed")

    except Exception as _ex:
        print("[INFO] Error while working ", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgresSQL connection closed")
