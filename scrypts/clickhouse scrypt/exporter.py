import psycopg2
from psycopg2.extras import RealDictCursor
from config import *
import datetime
import csv
import clickhouse_connect
from clickhouse_connect.driver.tools import insert_file
from uuid import uuid4
import os


def data_partition():
    return input("название партиции sh_dwh.bnso_data_t(yyyymmdd). введите дату партиции в формате 'yyyymmdd: ")


agg_conn = psycopg2.connect(
    host=agg_secret['host'],
    user=agg_secret['user'],
    password=agg_secret['password'],
    database=agg_secret['db_name'],
    port=agg_secret['port']
)

client = clickhouse_connect.get_client(host=kh_secret['host'],
                                       username=kh_secret['user'],
                                       password=kh_secret['password'],
                                       database=kh_secret['db_name'],
                                       port=kh_secret['port'],
                                       query_limit=0)


def datetime_handler(x):
    if isinstance(x, datetime.date):
        return x.strftime("%Y-%m-%dT%H:%M:%S%z")


count = 0
count_table = 1
summa = 0

with agg_conn.cursor(name=f"my_name_{uuid4()}", cursor_factory=RealDictCursor) as cursor:
    cursor.itersize = 500000
    cursor.execute(f"""SELECT bnso_code, nph_request_id, navigate_date, provider_id,
            asu_ods_user, owner_id, status_id, speed, lon, lat, y_msk, x_msk,
            nsat, pdop, odh_id, yard_id, odh_owner_id, yard_owner_id, oktmo_code,
            garage_id, trash_id, ssp_id, loadplace_id, gov_number, car_owner_id, car_type_id,
            car_group_id, region_id, car_id, car_company_id, con_area, district,
            wst, motor_depot_id, altitude, polygon_id FROM sh_dwh.bnso_data_t{data_partition()}""")

    for i in cursor:
        packet = {
            'client': int(i['bnso_code']),
            'nph_request_id': i['nph_request_id'],
            'navigation_date': i['navigate_date'],
            'provider_id': i['provider_id'],
            'asu_ods_user': i['asu_ods_user'],
            'owner_id': i['owner_id'] or 0,
            'status_id': i['status_id'],
            'speed': i['speed'],
            'longitude': i['lon'],
            'latitude': i['lat'],
            'y_msk': i['y_msk'],
            'x_msk': i['x_msk'],
            'nsat': i['nsat'],
            'pdop': i['pdop'],
            'odh_id': i['odh_id'] or 0,
            'yard_id': i['yard_id'] or 0,
            'odh_owner_id': i['odh_owner_id'] or 0,
            'yard_owner_id': i['yard_owner_id'] or 0,
            'oktmo_code': i['oktmo_code'] or 0,
            'garage_id': i['garage_id'] or 0,
            'trash_id': i['trash_id'] or 0,
            'ssp_id': i['ssp_id'] or 0,
            'loadplace_id': i['loadplace_id'] or 0,
            'gov_number': i['gov_number'] or ' ',
            'car_owner_id': i['car_owner_id'] or 0,
            'car_type_id': i['car_type_id'] or 0,
            'car_group_id': i['car_group_id'] or 0,
            'region_id': i['region_id'] or 0,
            'car_id': i['car_id'] or 0,
            'car_company_id': i['car_company_id'] or 0,
            'con_area_id': i['con_area'] or 0,
            'district_id': i['district'] or 0,
            'wst_id': i['wst'] or 0,
            'motor_depot_id': i['motor_depot_id'] or 0,
            'altitude': int(i['altitude']),
            'polygon_id': i['polygon_id'] or 0,
            'ip_address': '10.127.33.33',
            'port': 0,
            'imei': ' ',
            'receive_ts': 0,
            'navigation_ts': 0,
            'dut.port': [],
            'dut.sensor_id': [],
            'dut.raw_value': [],
            'dut.value': [],
            'kbm.type_id': [],
            'kbm.port': [],
            'kbm.sensor_id': [],
            'kbm.raw_value': [],
            'kbm.value': []
        }

        with open(f'data/data{count_table}.csv', 'a', newline='') as f:
            csv_writer = csv.writer(f)
            if count == 0:
                header = packet.keys()
                csv_writer.writerow(header)
            count += 1
            summa += 1
            csv_writer.writerow(packet.values())
            if count == 500000:
                insert_file(client, 'telemetry', f'data/data{count_table}.csv', settings=
                {'input_format_allow_errors_ratio': .2,
                 'input_format_allow_errors_num': 5})
                os.remove(f'data/data{count_table}.csv')
                print(f'пачка № {count_table} загружена и удалена')
                count = 0
                count_table += 1


insert_file(client, 'telemetry', f'data/data{count_table}.csv', settings=
{'input_format_allow_errors_ratio': .2,
 'input_format_allow_errors_num': 5})
print(count_table)
print('последняя пачка')
os.remove(f'data/data{count_table}.csv')
client.close()
print(f'всего строк= {summa - (count_table - 1)}')
