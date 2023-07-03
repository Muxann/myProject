#!/usr/bin/env python3
from datetime import datetime
from config import *
import psycopg2
from psycopg2.extras import RealDictCursor
import simplejson
import pika


def py_default(obj):
    epoch = datetime.utcfromtimestamp(0)
    return {"$date": int((obj - epoch).total_seconds() * 1000.0)}


def data_partition():
    return input("название партиции sh_dwh.bnso_data_t(yyyymmdd). введите дату партиции в формате 'yyyymmdd: ")


credentials = pika.PlainCredentials(rabbit_secret['username'],
                                    rabbit_secret['password'])
parameters = pika.ConnectionParameters(rabbit_secret['host'],
                                       rabbit_secret['port'],
                                       rabbit_secret['virtualHost'],
                                       credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='queue')

agg_conn = psycopg2.connect(
    host='10.127.32.86',
    user='postgres',
    password='Xae4aep9',
    database='vts',
    port=5432
)

estp_conn = psycopg2.connect(
    host='10.127.32.90',
    user='odoo',
    password='odoo',
    database='estp',
    port=5432
)

agg_cur = agg_conn.cursor(cursor_factory=RealDictCursor)
estp_cur = estp_conn.cursor(cursor_factory=RealDictCursor)

sens_query = """select distinct ers.id as sensor_id,
                           erep.egts_field
                    from estp_registers_sensor ers
                        inner join estp_registers_egts_protocol erep on ers.protocol_field_id = erep.id;
"""

sens_cache = {}
estp_cur.execute(sens_query)

for r in estp_cur:
    sens_cache[r['sensor_id']] = r['egts_field']

agg_cur.execute(f"""select bnso_code, nph_request_id, lon, lat, pdop, dut, kbm, navigate_date
FROM sh_dwh.bnso_data_t{data_partition()} bdt where provider_id = 10232951""")

for p in agg_cur:
    packet = {
        'client': int(p['bnso_code']),
        'nph_request_id': p['nph_request_id'],
        'nav_data': {
            'longitude': p['lon'],
            'latitude': p['lat'],
            'time_stamp': p['navigate_date'],
            'pdop': p['pdop']
        }
    }
    if p['kbm']:
        for k in p['kbm']:
            s = sens_cache.get(k['sensor_id'], None)
            if s:
                section, field = s.split('.')
                num_port = k['number']

                if section == 'data_type_20':
                    if not packet.get(section, None):
                        packet[section] = {
                            "flag_high": "00000000000000000000000000000000",
                            "flag_low": "00000000000000000000000000000000"
                        }
                    # todo: поставить нужный индекс
                    t = list(packet[section][field])
                    t[-num_port] = str(k["raw_value"])
                    packet[section][field] = "".join(t)
                    #packet[section][field] = (packet[section][field][:-num_port] + str(k["raw_value"]) + packet[section][field][-num_port + 1:])
                    #packet[section][field][num_port] = k["raw_value"]

                elif section == 'data_type_2':
                    if not packet.get(section, None):
                        packet[section] = {}

                    packet[section]["an_in{}".format(num_port)] = k["raw_value"]
    if p['dut']:
        for d in p['dut']:
            s = sens_cache.get(d['sensor_id'], None)
            if s:
                section, field = s.split('.')

                s_rec = None
                if section == 'data_type_8':
                    s_rec = {
                        "temperature": 0,
                        "level_l": 0,
                        "det_dtatus": 0,
                        "nav_data_number": d['number'],
                        "level_mm": d['raw_value']
                    }
                elif section == 'data_type_10':
                    s_rec = {
                        "FuelLevel": d['raw_value'],
                        "nav_data_number": d['number'],
                        "AllTrack": "0",
                        "AllTimeEngine": 0
                    }

                if s_rec:
                    if not packet.get(section, None):
                        packet[section] = []

                    packet[section].append(s_rec)

    channel.basic_publish(
        exchange='',
        routing_key='queue',
        body=simplejson.dumps(packet, default=py_default),
        properties=pika.BasicProperties(delivery_mode=2, )
    )
