# Загрузчик данных из АГГ2 в RabbitMQ
Сервис подключается к агрегатору АГГ2, выгружает данные за указанный период, конвертирует в json и передаёт их в очередь RabbitMQ.

## Формат запуска:

Установка и настройка репозитория:

```
virtualenv env
env/bin/pip install -r requirements.txt

python loader.py config.py
```

_config.py_ - файл конфигурации

### Файл конфигурации

Пример готового файла:
```py
# даные подключения к posgresql
pg_secret = {'host': '127.0.0.1',
             'user': 'postgres',
             'password': '1234',
             'db_name': 'vts',
             'port': '5432'
             }

# данные подключения к rabbit_mq
rabbit_secret = {'host': '127.0.0.1',
                 'username': 'mqadmin',
                 'password': 'mqadmin',
                 'port': '5672',
                 'exchange': 'workers',
                 'virtualHost': '/',
                 'exchange_type': 'direct',
                 'queue': 'workers_queue1'
                 }
```

db
- _host_ - _string_ - Адрес базы данных.
- _user_ - _string_ - Логин.
- _password_ - _string_ - Пароль.
- _db_name_ - _string_ - Имя базы данных.
- _port_ - _int_ - Порт базы данных.



[rabbit_secret]
- _host_ - _string_ - Адрес брокера сообщений.
- _username_ - _string_ - Логин к брокеру.
- _password_ - _string_ - Пароль к брокеру.
- _port_ - _string_ - Порт брокера сообщений
- _exchange_ - _string_ - название обменника
- _virtualHost_ - _string_ - виртуальных хост брокера
- _exchange_type_ - _string_ - тип exchange (обменника) (direct, topic, headers, fanout)
- _queue_ - _string_ - Очередь брокера"




## Работа со скриптом

```
Установить все зависимости из файла requirements.txt. Запустить.
При успешном запуске должна появится строка: "Enter the date in 'yyyy-mm-dd format' or 'yyyy-mm-dd hh:mm:ss' '>': "
Вводим даты в вышеуказанном формате. (дата начала периода) 
Следующим сообщением дату окончания периода.
Сообщения преобразуются в json формат и отправляются брокеру
```

## Docker
```
сборка из исходников:
docker build . -t psd-postgresql-exporter

запуск:
docker run -it --network=host psd-postgresql-exporter
```
