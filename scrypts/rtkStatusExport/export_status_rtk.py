import pandas as pd
import psycopg2
from datetime import datetime
import csv

status_mapping = {"Новое ТС": 1,
                  "Установка и настройка БНСО": 2,
                  "Эксплуатация": 3,
                  "Сезонное хранение": 4,
                  "Ремонт БНСО": 5,
                  "Ремонт ТС": 6}

conn = psycopg2.connect(host='localhost',
                        dbname='estp',
                        user='odoo',
                        password='odoo')

# 1) получение данных из БД и создание словаря
print("создаем соединение с базой данных")
cur = conn.cursor()

print("Открываем файл со статусами")
df = pd.read_csv("status+vehicle_id.csv", index_col=False, delimiter=',')
print("РАЗМЕР файла РТК до начала загрузки" + str(df.shape))
# Преобразование столбца старт к времени
df['start'] = pd.to_datetime(df['start'])  # Преобразование строки к времени
# замена столбца статус на state_id
df['state_id'] = df['status'].map(status_mapping)
df = df.rename(columns={'start': 'start_date', 'end': 'end_date'})
df = df.drop(['car', 'bnso', 'status'], axis=1)
# удаление статусов где старт дата >= 19.02.2023
df_merged = df[df['start_date'] <= '19-02-2023 00:00:00']
print("количество строк после удаления статусов корорые меньше 19-02-2023 00:00:00: " + str(df_merged.shape))
# Получаем из БД все данные о статусах которые >= 19.02.2023
print("Получаем все статусы из БД которые = '2023-02-19'")
# TODO если вдруг произошла ошибка при загрузке статусов, то коментируем следующие строки с 40-48 и
#  повторяем загрузку, но уже новые статусы будут грузится из файла csv
current_date = datetime.now().strftime("%Y-%m-%d")

cur.execute("SELECT * FROM public.estp_registers_vehicle_state_history WHERE start_date >= '2023-02-19'")
rows = cur.fetchall()
# # сохранение данных таблицы в файл CSV с текущей датой в названии файла
col_names = [desc[0] for desc in cur.description]

with open(f'output_{current_date}.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(col_names)
    writer.writerows(rows)
# ---------------------------------------------------------------------

new_status_psd = pd.read_csv(f"output_{current_date}.csv")
# new_status_psd = pd.read_csv(f"output_2023-04-12.csv")
# Сортировка по вехиль айди и старт дате данных полученных из БД
print("Соединяем файл РТК с новыми статусами, полученными из БД")
new_status_psd = new_status_psd.sort_values(['vehicle_id', 'start_date'])
df_merged = df_merged.sort_values(['vehicle_id', 'start_date'])

grouped_new_status_psd = new_status_psd.groupby('vehicle_id')
df_merged2 = df_merged.groupby('vehicle_id')

for group_id, group_df1 in grouped_new_status_psd:
    if not pd.isna(group_id) and group_id in df_merged2.groups:
        group_df2 = df_merged2.get_group(group_id)
        last_end_date = group_df2.iloc[-1]['end_date']

        first_start_date = group_df1.iloc[0]['start_date']
        print(group_id)
        print("дата начала из новых статусов: " + str(first_start_date))
        print(f"дата окончания файла для vehicle_id = {group_id} : " + str(last_end_date))
        if last_end_date > first_start_date:
            last_row_index = group_df2.index[-1]  # получение индекса последней строки в группе
            df_merged.at[last_row_index, 'end_date'] = first_start_date  # замена значения в конкретной ячейке

# возвращаем столбец с датой обратно к строке для объединения таблиц
df_merged['start_date'] = df_merged['start_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
db_full = pd.concat([df_merged, new_status_psd], axis=0)

# 10) получение текущей даты и заполнение пустых значений даты на текущую дату
today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
replace_dict = {'create_date': today, 'write_date': today}
db_full.fillna(value=replace_dict, inplace=True)

# 11) Заполнение пустых значений create_uid и write_uid на 5 и приведение столбцов к int
uid_dict = {'create_uid': 5, 'write_uid': 5}
db_full.fillna(value=uid_dict, inplace=True)

db_full['create_uid'] = db_full['create_uid'].astype(int)
db_full['write_uid'] = db_full['write_uid'].astype(int)

# 12) удаление столбца id
db_full.drop(labels='id', axis=1, inplace=True)

db_full['start_date'] = pd.to_datetime(db_full['start_date'])
# Сортировка по vehicle_id и start_date
db_full = db_full.sort_values(['vehicle_id', 'start_date'])

print("Удаление всех статусов где start_date >= '2021-01-01'")
# 13) Удалить из таблицы в ESTP все значения у которых дата start date >= 01.01.2021
query = "DELETE FROM public.estp_registers_vehicle_state_history WHERE start_date >= '2021-01-01'"
cur.execute(query)
conn.commit()

# 14) Получение максимальное id и добавление столбца с id к нашей таблцице
# Делаем запрос к бд на получение максимального id
cur.execute("SELECT MAX(id) FROM public.estp_registers_vehicle_state_history")
# извлечение результата запроса
max_id = cur.fetchone()[0]
# дописываем столбец id к нашему датафрейму
db_full = db_full.assign(id=pd.Series(range(max_id + 1, max_id + len(db_full) + 1)).values)

print("Загрузка статусов в БД")
# групировка по vehile_id
grouped = db_full.groupby('vehicle_id')
batch_size = 5
batch_counter = 0
summ = 0
batch_data = []
vehicle_ids = []  # создаем пустой список vehicle_id
skipped_ids = []  # список пропущенных значений vehicle_id
for vehicle_id, data in grouped:
    print(vehicle_id)
    vehicle_ids.append(vehicle_id)
    cur = conn.cursor()
    end = cur.execute(
        f"SELECT end_date FROM public.estp_registers_vehicle_state_history"
        f" WHERE vehicle_id='{vehicle_id}' ORDER BY end_date DESC LIMIT 1")
    result = cur.fetchone()
    if result is not None:
        last_end = result[0]
    else:
        last_end = datetime(2000, 1, 1, 0, 0, 0)
    # last_end = cur.fetchone()[0]  # .strftime('%Y-%m-%d %H:%M:%S')

    cur.close()
    print(last_end)
    first_start = data['start_date'].iloc[0]
    print(first_start)

    if last_end > first_start:
        try:
            cur = conn.cursor()
            # заменяем значение end из базы данных на значение start
            cur.execute(f"UPDATE public.estp_registers_vehicle_state_history"
                        f" SET end_date='{first_start}' WHERE vehicle_id='{vehicle_id}' AND end_date = '{last_end}'")
            cur.close()
        except Exception as _x:
            print(_x)
            continue
    # Преобразуем  start_date к строке, чтобы нормально загрузить в бд
    data['start_date'] = data['start_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    batch_data.append(data.values.tolist())
    summ += len(data)
    if len(batch_data) >= batch_size:
        cur = conn.cursor()
        data_values = ",".join([str(tuple(x)) for batch in batch_data for x in batch])
        insert_query = f"INSERT INTO public.estp_registers_vehicle_state_history " \
                       f"(start_date, end_date, vehicle_id, state_id, create_uid, create_date, write_date," \
                       f" write_uid, id) VALUES {data_values}"
        try:
            cur.execute(insert_query)
            conn.commit()
        except Exception as e:
            print(f"Ошибка! произошла ошибка при вставке vehicle_id: {vehicle_ids}: {e}")
            skipped_ids.extend(vehicle_ids)
            conn.rollback()  # откатываем транзакцию
            vehicle_ids = []  # очищаем список
            batch_counter = 0
            batch_data = []
            summ = 0
            continue
        cur.close()
        print(f"Загружены данные для следующих vehicle_id: {vehicle_ids}")
        print(f"Количество загруженных строк: {summ}")
        print(f"Пачка из {batch_size} vehicle_id загружена в базу данных.")
        vehicle_ids = []  # очищаем список
        batch_counter = 0
        batch_data = []
        summ = 0
    else:
        batch_counter += 1

if batch_data:
    cur = conn.cursor()
    data_values = ",".join([str(tuple(x)) for batch in batch_data for x in batch])
    insert_query = f"INSERT INTO public.estp_registers_vehicle_state_history " \
                   f"(start_date, end_date, vehicle_id, state_id, create_uid, create_date, write_date," \
                   f" write_uid, id) VALUES {data_values}"
    try:
        cur.execute(insert_query)
        conn.commit()
    except Exception as e:
        print(f"Ошибка! произошла ошибка при вставке vehicle_id: {vehicle_ids}: {e}")
        skipped_ids.extend(vehicle_ids)
        conn.rollback()  # откатываем транзакцию
    cur.close()

    print(f"Оставшаяся пачка из {len(batch_data)} vehicle_id загружена в базу данных.")
    print(f"Загружены данные для следующих vehicle_id: {vehicle_ids}")
    print(f"Количество загруженных строк: {summ}")
if skipped_ids:
    print(f"Следующие vehicle_id не загрузились в БД: {skipped_ids}")
