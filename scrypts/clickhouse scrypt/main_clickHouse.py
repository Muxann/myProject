import psycopg2
import clickhouse_connect
import pandas as pd
from pyarrow import csv
from config import pg_secret, kh_secret


def query_x(x=input("enter the date in 'yyyy-mm-dd format' or 'yyyy-mm-dd hh:mm:ss' '>': ")):
    return x


def query_y(y=input("enter the date in 'yyyy-mm-dd format' or 'yyyy-mm-dd hh:mm:ss' '>': ")):
    return y


try:
    # connect to exist database PostgresSQL
    print("[INFO] Connect to exist database PostgresSQL")
    connection = psycopg2.connect(
        host=pg_secret['host'],
        user=pg_secret['user'],
        password=pg_secret['password'],
        database=pg_secret['db_name'],
        port=pg_secret['port']
    )
    query = f"SELECT bnso_code, nph_request_id, navigate_date, provider_id,\
    asu_ods_user, owner_id, status_id, speed, lon, lat, y_msk, x_msk,\
    nsat, pdop, odh_id, yard_id, odh_owner_id, yard_owner_id, oktmo_code,\
    garage_id, trash_id, ssp_id, loadplace_id, gov_number, car_owner_id, car_type_id,\
    car_group_id, region_id, car_id, car_company_id, con_area, district,\
    wst, motor_depot_id, altitude, polygon_id FROM sh_dwh.bnso_data_t where\
    navigate_date  >= '{query_x()}' and navigate_date < '{query_y()}'"

    """connection.cursor() создает курсор для осуществление запросов в БД. Результатом запроса является генератор.
     Его мы распаковываем в переменную data_pg"""

    print("[INFO] Connection to PostgresSQL database established:")
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

        columns = []
        for desc in cursor.description:
            columns.append(desc[0])
        data_pg = pd.DataFrame(result, columns=columns)
    """.rename позволяет нам переименовать столбцы, которые имеют общее содержание но разные по названию"""

    rename_data_pg = data_pg.rename(columns={'bnso_code': 'client',
                                             'navigate_date': 'navigation_date',
                                             'lon': 'longitude',
                                             'lat': 'latitude',
                                             'con_area': 'con_area_id',
                                             'district': 'district_id',
                                             'wst': 'wst_id'
                                             })
    # print(rename_data_pg.info(memory_usage='deep'))
    names_tables_klickhouse = pd.DataFrame(columns=['client', 'nph_request_id', 'navigation_date',
                                                    'receive_ts', 'navigation_ts', 'provider_id',
                                                    'asu_ods_user', 'owner_id', 'status_id',
                                                    'speed', 'longitude', 'latitude', 'y_msk',
                                                    'x_msk', 'nsat', 'pdop', 'odh_id',
                                                    'yard_id', 'odh_owner_id', 'yard_owner_id', 'oktmo_code',
                                                    'garage_id', 'trash_id', 'ssp_id', 'loadplace_id',
                                                    'gov_number', 'car_owner_id', 'car_type_id', 'car_group_id',
                                                    'region_id', 'car_id', 'car_company_id', 'con_area_id',
                                                    'district_id', 'wst_id', 'dut.port', 'dut.raw_value',
                                                    'dut.value', 'kbm.type_id', 'kbm.port', 'kbm.raw_value',
                                                    'kbm.value', 'kbm.sensor_id', 'dut.sensor_id', 'motor_depot_id',
                                                    'altitude', 'polygon_id', 'ip_address', 'port', 'imei'])

    """"Производится конкатенация таблиц. Сначала берется таблица с названиями столбцов бд KlickHouse
    и в нее добавляется таблица из postgeSQL. Пустые столбцы наполняются нулевыми значениями NaN"""
    db_full = pd.concat([names_tables_klickhouse, rename_data_pg], axis=0)
    # -----------------------------------------------------------------------------------------------------------
    db_full[['dut.port', 'dut.raw_value', 'dut.value',
             'kbm.type_id', 'kbm.port', 'kbm.raw_value',
             'kbm.value', 'kbm.sensor_id', 'dut.sensor_id']] = db_full[['dut.port', 'dut.raw_value', 'dut.value',
                                                                        'kbm.type_id', 'kbm.port', 'kbm.raw_value',
                                                                        'kbm.value', 'kbm.sensor_id',
                                                                        'dut.sensor_id']].fillna('[]').astype('category')
    db_full['ip_address'] = db_full['ip_address'].fillna('10.127.33.33').astype('category')
    db_full[['gov_number', 'imei']] = db_full[['gov_number', 'imei']].fillna(' ').astype('category')
    db_full = db_full.fillna(0).astype('category')

    # ------------------------------------------------------------------------------------------------------------
    db_full.to_csv('df_kh.csv', index=False)
    print("File save")

except Exception as _ex:
    print("[INFO] Error while working with PostgresSQL", _ex)
finally:
    if connection:
        connection.close()
        print("[INFO] PostgresSQL connection closed")

# ------------------------------------------------------------------------------

try:
    # run to clickHouse
    print("[INFO] run to clickHouse")
    client = clickhouse_connect.get_client(host=kh_secret['host'],
                                           username=kh_secret['user'],
                                           password=kh_secret['password'],
                                           database=kh_secret['db_name'],
                                           port=kh_secret['port'],
                                           query_limit=0)

    table = csv.read_csv('df_kh.csv')
    client.insert_arrow('default.telemetry', table)
    print("[INFO] Table loaded!")
    # chunks = np.array_split(db_full, 10)
    # for chunk in chunks:
    #     ready_db_full = pa.Table.from_pandas(chunk, preserve_index=False)  # преобразование в pyarrow.Table
    #     client.insert_arrow('default.telemetry', ready_db_full)

except Exception as _ex:
    print("[INFO] Error while working with ClickHouse", _ex)
finally:
    if client:
        client.close()
        print("[INFO] KlickHouse connection closed")
