from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import json
from datetime import datetime, timedelta
from colorama import *

init(autoreset=True)
person = []
quest = ['qDesertpsv', 'SteelFist']

with open('options/amulet.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
    boi_dict = json.load(f)

with open('options/amulet_animal.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
    boi_dict_animation = json.load(f)

with open('options/metro.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
    metro = json.load(f)

banki = {'Инфериум', 'Титаниум', 'Ториум'}

m_crack = {'Рунический Шлем', 'Рунический Доспех', 'Руническая Накидка', 'Кулон Сумрака', 'Сумеречный Колпак',
           'Сумеречный Кинжал', 'Зачарованный Капюшон', 'Зачарованная Накидка', 'Зачарованные Одеяния', 'Шляпа Покоя',
           'Туника Покоя', 'Жезл Покоя', 'Покаяния', 'Покорного', 'Рассвета', 'Странника',
           'Заката', 'Покров Ночи', 'Неба', 'Череп раба', 'Жезл Дня и Ночи', 'Скипетр Всех Бед',
           'Отражение', 'Ночные Откровения', 'Перстень Барона', 'Тотем Болот', 'Талисман Болотоходца',
           'Ремень Егеря', 'Варлорда', 'Роба Теней', 'Шаль из Тени', 'Сумеречная Маска', 'Сумеречный Щит', 'Кровь Теней',
           'Экзекутора', 'Экзекутор', 'Титана', 'Титанов', 'Титанический Посох', 'Боевые Наплечи', 'Маяк Создателя', 'Маска Механика',
           'Титановая Подвеска Злобы', 'Рока', 'Авантюриста', 'Предвестник Смерти', 'Жнец', 'Предсказателя',
           'Кинжал Прозрения', 'Посох Судьбы', 'Бессмертного', 'Страха', 'Палач', 'Кольцо Обретенной Надежды',
           'Кольцо Раскаяния', 'Печать Бессмертия', 'Колье-оберег Судьбы', 'Пламенная Крона', 'Непрощенного',
           'Свиток Прощения', 'Бессонницы', 'Наплечи Бессонного', 'Книга Тайного Знания', 'Покоритель Духов', 'Непокорного', 
           'Лазуритовая Кираса', 'Щит Искусителя', 'Лазуритовый Клинок', 'Кольцо Бессонного', 'Непокорного',
           'Кольцо Искусителя', 'Отрекшихся', 'Наплечи Лорда Рагнар', 'Разделитель', 'Рогатый Щит', 'Странника',
           'Кольцо Мертвого Лорда', 'Кулон Мертвеца', 'Искупления', 'Укус Горгульи', 'Доспехи Изменчивых Теней', 'Изменчивая Мантия Тени',
           'Изменчивый', 'Изменника', 'Искателя Теней', 'Посох Неумолимого Искателя', 'Кольцо Изменчивой Природы',
           'Адамантитовое Забрало', 'Адамантитовый', 'Дух Адамантитовой Горы', 'Маска Великих',
           'Наплечи Великих', 'Мантия Великих', 'Дух Шамбалы', 'Молот Семипалого', 'Этерниев',
           'Виверны', 'Грозового Дракона', 'Повелитель Ветров', 'Драконий Посох', 'Небесного', 'Колдуна', 'Епископа', 'Коса Очищения',
           'Душегуба', 'Мстителя', 'Скверны', 'Верховного Вождя', 'Посох Главенства Тьмы', 'Непреодолим', 
           'Кольцо Осквернения', 'Непреодолимости', 'Кольцо Темного Вождя', 'Кулон Вождя',
           'Шлем Геральда', 'Кристальные Наплечи', 'Мифрильные Латы', 'Боевой Молот', 'Геральдический Щит',
           'Праведника', 'Клинок Ветров', 'Огненный Клинок', 'Тиара Забытия', 'Некротик', 'Облачение Некроманта',
           'Кольцо Превосходства', 'Кольцо Грозовой Бури', 'Кольцо Душевной Боли', 'Ожерелье Ярости Богов',
           'Эфира', 'Ожерелье Медитации', 'Жизни', 'Животворящий Посох', 'Знак Небес', 'Гнев Небес', 'Падшего', 
           'Меч Правосудия', 'Плазмы', 'Плазменная Броня', 'Солнечный Щит', 'Дробитель', 'Чернокнижника',
           'Мантия Тьмы', 'Ритуальный Череп', 'Собиратель Душ', 'Феникса', 'Огненные Наплечи', 'Терпения',
           'Кристалл Нетающего Льда', 'Легкий Щит', 'Лезвие Ветра', 'Облачный Клинок', 'Эфирные Доспехи', 'Эфирный Канал',
           'Одеяние Дель Солис', 'Странника', 'Авантюриста', 'Стальной', 'Охранника', 'Стражи', 'Рассветной Магии', 
           'Старое Копье', 'Наставника', 'Иллюзиониста', 'Волхва', 'Магическая Роба', 'Магической Силы', 'Свиток Силы',
           'Магический Молот', 'Кадило Черного Света', 'Скипетр Неизбежности', 'Безмятежность Смерти', 'Объятия Мора',
           'Маска Пожинателя', 'Удар', 'Острие Молнии', 'Сияние Звезд', 'Скипетр Небес', 'Облачного',
           'Святоши', 'Священный Клинок', 'Адепта', 'Молитвенн', 'Рунный Посох', 'Хранителя', 'Мантия Колдуна',
           'Полуночной Молитвы', 'Сонник', 'Видений', 'Колдовской',
           'Тяжелые Латы', 'Командира', 'Командирский', 'Энергии', 'Энергетический', 'Полюса Серого Отречения',
           'Молот Непричастности', 'Кольчуга Охраны', 'Грозовых Чар', 'Клинок Грозы', 'Отваги', 'Лекаря', 'Пехотинца',
           'Боевого Мага', 'Дырявый Халат', 'Боевой', 'Боевые Наплечи', 'Свет Луны', 'Жезл Причащения', 'Платье Кардинала',
           'Звездная пыль I', 'Новой Веры', 'Обруч Ведания', 'Записки Отшельника', 'Знахаря',
           'Офицерский Клинок', 'Мясник', 'Магический Меч', 'Арбитра', 'Путеводная Звезда', 'Солнечный камень',
           'Чужака', 'Генеральский', 'Небесное Сияние', 'Служителя', 'Колба Баланса', 'Боевой Щит',
           'Шапка Колдуна', 'Шлем Доблести', 'Холщовая', 'Стража',
           'Небесное Сияние', 'Генеральск', 'Латы Славы', 'Послушника', 'Ренегата', 'Грозовой Магии',
           'Легионера', 'Мастера', 'Осколок Бессмертия', 'Убор Бесчестия',
           'Мутный', 'Треснувший', 'Надколотый', 'Руна Терпения', 'Руна Коварства',
           'Ратный', 'Ратные Наплечи', 'Корона Подземелий', 'Наплечи Северной Шахты',
           'Броня Южных Лабиринтов', 'Клинок Западных Катакомб', 'Щит Восточных Расселин', 'Легиона',
            'Объятия Земли', 'Огонь Вечности', 'Старый Шлем', 'Кулон Наказаний', 'Заря',
           'Гром', 'Накидка Глубокой Печали', 'Лезвия Правителя', 'Лорда', 
           'Пламя Славы', 'Стремления', 'Лезвие Зеленого Титана', 'Кленовый Посох', 'Кожаные Наплечи',
           'Посох Призывателя Гроз',
           'Кираса Офицера', 'Авантюриста', 'Ветхая Ряса', 'Осколок Небес', 'Облегченные Латы', 'Нефритовая бусина',
           'Руна Живучести', 'Руна Перемен', 'Руна Гнева', 'Свиток Качества', 'Свиток Улучшения',
           'Зачарованный свиток', 'Бронза', 'Кристалл Создателя', 'Слеза Купидона',
           'Астральная Сфера'}

m_open = {'Сокровища Бездны', 'Драгоценности Культа', 'Драгоценности Смотрителей', 'Сундук Древних', 'Сундук Барона',
          'Узорный Ящик', 'Дар Чародея', 'Загадка Азалотха', 'Малый Сундук',
          'Средний Сундук', 'Большой Сундук',
          'Ларец Любовных Медальонов'}


def xpath_exists(xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        exist = True
    except NoSuchElementException:
        exist = False
    return exist


def text_exists(text):
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, text)
        exist = True
    except NoSuchElementException:
        exist = False
    return exist


def id_exits(id1):
    try:
        driver.find_element(By.ID, id1)
        id1 = True
    except NoSuchElementException:
        id1 = False
    return id1


def css_exits(css):
    try:
        driver.find_element(By.CSS_SELECTOR, css)
        css = True
    except NoSuchElementException:
        css = False
    return css


def pomeha():
    pomeha_list = ["//a[contains(text(),'Закрыть')]",  # закрытие щедрого предложения +
                   "//a[contains(text(),'Продолжить')]",  # закрытие бонуса отдыха +
                   "//div[@id='achievePopup']/div/a",  # закрытие достижения +
                   "//a[contains(text(),'Спасибо')]",  # cпасибо за эфирный канал/амулет +
                   "//div[5]/div/div/div/a/span",  # закрытие вкладки улучшить амы
                   "//div[@class='notice-rich3-close']"  # закрытие всплывающих окон
                   ]

    for j in range(3):
        for pom in pomeha_list:
            try:
                if xpath_exists(f"{pom}"):
                    driver.find_element(By.XPATH, f"{pom}").click()
                    time.sleep(0.2)
            except Exception:
                print('\033[1m\033[31m{}\033[0m'.format("Ошибка: не найден элемент, чтобы скрыть это безобразие"))
            finally:
                continue


def proverka_and_boi():
    # TODO на случай случайного выхода из метро и старта не с начала!!!
    if xpath_exists("//*[contains(text(), 'Продолжить')]"):
        driver.find_element(By.XPATH, "//span[contains(text(), 'Продолжить')]").click()
    elif xpath_exists("//*[contains(text(), 'Начать')]"):
        driver.find_element(By.XPATH, "//*[contains(text(), 'Начать')]").click()
    if xpath_exists("//a[@class='attack-button-link']"):
        print("Выбрана боевка для анимационных боев")
        boi_smart()
    else:
        print("Выбрана классическая боевка без анимации")
        boi_obla()


def boi_smart(time_limit=2200):
    end_time = datetime.now() + timedelta(seconds=time_limit)
    while datetime.now() < end_time:
        if xpath_exists("//*[text()='Обновить']"):
            driver.find_element(By.XPATH, "//*[text()='Обновить']")
            driver.refresh()
            time.sleep(20)
        # TODO первый этап. Определяем, когда будет осущестлвяться окончание метро
        else:
            if xpath_exists("//a[@title='Замок на Воротах']") or xpath_exists(
                    "//*[text()='Подземелье закрыто']") or xpath_exists(
                "//div[@class='ya-share2__container ya-share2__"
                "container_size_m ya-share2__container_color-scheme_normal "
                "ya-share2__container_shape_normal']"):
                time.sleep(1)
                driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
                break

            # TODO сбор монеток во время ивента. КОгда ивентов нет. Можно отключать
            if xpath_exists("//div[contains(@id, 'loot_box')]"):
                couts = driver.find_elements(By.XPATH, "//div[contains(@id, 'loot_box')]")
                while couts:
                    try:
                        m = couts.pop(0)
                        if m:
                            m.click()
                            time.sleep(0.2)
                    except Exception:
                        pass
                    finally:
                        continue
            # TODO опция возвращает персонажа к жизни в случаем смерти например ШГ
            if xpath_exists("//span[text()='Покинуть бой']/.."):
                driver.find_element(By.XPATH, "//span[text()='Покинуть бой']/..").click()
            elif xpath_exists("//*[@class='go-btn-in _font-art']"):
                driver.find_element(By.XPATH, "//*[@class='go-btn-in _font-art']/ancestor::a").click()
            elif xpath_exists("//*[contains(text(), 'Начать')]"):
                driver.find_element(By.XPATH, "//*[contains(text(), 'Начать')]").click()

            if xpath_exists(
                    "//div[@class='battlefield-head-left _breath']//div[contains(@class,'battlefield-head-hp-fill')]"):
                try:
                    style = driver.find_element(By.XPATH, "//div[@class='battlefield-head-left _breath']//div[contains"
                                                          "(@class,'battlefield-head-hp-fill')]").get_attribute(
                        'style').split()
                    if int(style[1].replace('%;', '')) < 40:
                        for i in banki:
                            if xpath_exists(f"//a[@title='{i}']/..//div[@class='potion-link-img _time-lock']"):
                                pass
                            elif xpath_exists(f"//a[@title='{i}']"):
                                driver.find_element(By.XPATH, f"//a[@title='{i}']").click()
                                print('\033[1m\033[33m{}\033[0m'.format('БАХНУЛ СТОПАРИК'))
                                time.sleep(0.1)
                except:
                    pass

            # TODO собственно сам бой, а именно перебор всех амулетов и нажатие доступных
            for key, value in boi_dict_animation.items():
                try:
                    if xpath_exists(f"//div[@class='{key}']"):
                        driver.find_element(By.XPATH, f"//a[@title='{value}']").click()
                        time.sleep(0.15)
                except Exception:
                    print('\033[1m\033[31m{}\033[0m'.format("Я потерял амулет. Перехожу к следующей итерации"))
                finally:
                    continue

            # TODO Кнопка атаковать. В случае потери кнопки сообщать в консоль
            if xpath_exists("//a[@class='attack-button-link']"):
                try:
                    if xpath_exists("//*[@title='Джек-Искуситель']"):
                        time.sleep(0.8)
                        driver.find_element(By.XPATH, "//*[@title='Джек-Искуситель']").click()
                    elif xpath_exists("//a[@class='attack-button-link']"):
                        time.sleep(0.8)
                        if xpath_exists("//a[@class='attack-button-link']"):
                            driver.find_element(By.XPATH, "//a[@title='Атаковать']").click()
                except Exception:
                    print('\033[1m\033[31m{}\033[0m'.format("упс, потерялась кнопка Атаковать, не страшно!"))
                finally:
                    continue
            elif xpath_exists("//a[@class='go-btn mt5 _for-center']"):
                driver.find_element(By.PARTIAL_LINK_TEXT, 'Продолжить бой').click()


def deistia():
    if xpath_exists("//*[contains(text(), 'Варлорд вскидывает руки,')]") \
            or xpath_exists("//*[contains(text(), 'Варлорд управляет темной')]") \
            or xpath_exists("//*[contains(text(), 'Варлорд снова поднимает руку')]") \
            or xpath_exists("//*[contains(text(), 'изредко внося в книгу поправки!"
                            " Кто знает, что он там пишет!')]") \
            or xpath_exists("//*[contains(text(), 'Старик продолжает следить')]"):
        driver.refresh()
        time.sleep(1)
    elif xpath_exists("//*[contains(text(), 'гладиатор, готовясь вступить в бой.')]") \
            or xpath_exists("//*[contains(text(), 'Между вами и книгой лишь отряд бессмертных')]"):
        if xpath_exists("//*[text()='Атаковать']"):
            driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
        time.sleep(0.8)
        driver.refresh()
    elif xpath_exists("//*[contains(text(), 'Призраки готовятся к нападению. Они не издают"
                      " ни звука - зловещая тишина режет уши.')]") \
            or xpath_exists("//*[contains(text(), 'Быстрее вперед! Не стоим на месте!')]"):
        if xpath_exists("//*[text()='Атаковать']"):
            driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
        time.sleep(0.8)
        driver.refresh()


def boi_obla(time_limit=2200):
    end_time = datetime.now() + timedelta(seconds=time_limit)
    while datetime.now() < end_time:
        if xpath_exists("//*[text()='Обновить']"):
            driver.find_element(By.XPATH, "//*[text()='Обновить']")
            driver.refresh()
            time.sleep(20)
        else:
            if xpath_exists("//div[@class='ya-share2__container ya-share2__"
                            "container_size_m ya-share2__container_color-scheme_normal "
                            "ya-share2__container_shape_normal']") \
                    or xpath_exists("//div[contains(text(),'Подземелья')]"):
                driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
                break

            # TODO ФУнкции Начать/Продолжить/Покинуть бой в случаем смерти и вернуться на локацию
            if xpath_exists("//*[contains(text(), 'Продолжить')]"):
                driver.find_element(By.XPATH, "//span[contains(text(), 'Продолжить')]").click()
            elif xpath_exists("//*[contains(text(), 'Начать')]"):
                driver.find_element(By.XPATH, "//*[contains(text(), 'Начать')]").click()
            elif xpath_exists("//span[text()='Покинуть бой']/.."):
                driver.find_element(By.XPATH, "//span[text()='Покинуть бой']/..").click()
                if xpath_exists("//*[@class='go-btn-in _font-art']/ancestor::a"):
                    driver.find_element(By.XPATH, "//*[@class='go-btn-in _font-art']").click()
            # TODO взаимодействие с мобами.
            if xpath_exists("//*[contains(text(), 'Варлорд вскидывает руки,')]") \
                    or xpath_exists("//*[contains(text(), 'Варлорд управляет темной')]") \
                    or xpath_exists("//*[contains(text(), 'Варлорд снова поднимает руку')]") \
                    or xpath_exists("//*[contains(text(), 'изредко внося в книгу поправки!"
                                    " Кто знает, что он там пишет!')]") \
                    or xpath_exists("//*[contains(text(), 'Старик продолжает следить')]"):
                driver.refresh()
                time.sleep(1)
            elif xpath_exists("//*[contains(text(), 'гладиатор, готовясь вступить в бой.')]"):
                if xpath_exists("//*[text()='Атаковать']"):
                    driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
                time.sleep(0.8)
                driver.refresh()
            elif xpath_exists("//*[contains(text(), 'Призраки готовятся к нападению. Они не издают"
                              " ни звука - зловещая тишина режет уши.')]") \
                    or xpath_exists("//*[contains(text(), 'Быстрее вперед! Не стоим на месте!')]"):
                if xpath_exists("//*[text()='Атаковать']"):
                    driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
                time.sleep(0.8)
                driver.refresh()
            else:
                if xpath_exists("//span[contains(@class, 'i12-heart')]"):
                    try:
                        style = driver.find_element(By.XPATH, "//span[contains(@class, 'i12-heart')]").get_attribute(
                            'class').split()
                        if int(style[1].replace('i12-heart_', '')) < 40:
                            for i in banki:
                                if xpath_exists(f"//a[@class='belt_item lock'][@title='{i}']"):
                                    pass
                                elif xpath_exists(f"//a[@title='{i}']"):
                                    driver.find_element(By.XPATH, f"//a[@title='{i}']").click()
                                    print('\033[1m\033[35m{}\033[0m'.format('БАХНУЛ СТОПАРИК'))
                                    time.sleep(0.1)
                    except:
                        pass

                for key, value in boi_dict.items():
                    try:
                        if xpath_exists(
                                f"//*[@class='go-btn _go-btn-violet _amulet'][contains(@href, 'amuletType={value}')]"):
                            time.sleep(0.33)
                            driver.find_element(By.XPATH, f"//*[@class='go-btn _go-btn-violet _amulet']"
                                                          f"[contains(@href, 'amuletType={value}')]").click()
                    except Exception:
                        print('\033[1m\033[31m{}\033[0m'.format("Я потерял амулет. Перехожу к следующей итерации"))
                        driver.refresh()
                    finally:
                        pass

                if xpath_exists("//*[contains(text(), 'Варлорд вскидывает руки,')]") \
                        or xpath_exists("//*[contains(text(), 'Варлорд управляет темной')]") \
                        or xpath_exists("//*[contains(text(), 'Варлорд снова поднимает руку')]") \
                        or xpath_exists("//*[contains(text(), 'изредко внося в книгу поправки!"
                                        " Кто знает, что он там пишет!')]") \
                        or xpath_exists("//*[contains(text(), 'Старик продолжает следить')]"):
                    driver.refresh()
                    time.sleep(1)
                elif xpath_exists("//*[contains(text(), 'гладиатор, готовясь вступить в бой.')]"):
                    if xpath_exists("//*[text()='Атаковать']"):
                        driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
                    time.sleep(0.8)
                    driver.refresh()
                elif xpath_exists("//*[contains(text(), 'Призраки готовятся к нападению. Они не издают"
                                  " ни звука - зловещая тишина режет уши.')]") \
                        or xpath_exists("//*[contains(text(), 'Быстрее вперед! Не стоим на месте!')]"):
                    if xpath_exists("//*[text()='Атаковать']"):
                        driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
                    time.sleep(0.8)
                    driver.refresh()
                else:
                    if xpath_exists("//*[text()='Атаковать']"):
                        try:
                            if xpath_exists("//*[text()='Атаковать']"):
                                time.sleep(0.7)
                                driver.find_element(By.XPATH, "//*[text()='Атаковать']").click()
                        except Exception:
                            print('\033[1m\033[31m{}\033[0m'.format("упс, потерялась кнопка Атаковать, не страшно!"))
                            driver.refresh()
                        finally:
                            continue
                    elif xpath_exists("//*[text()='Бить любого']"):
                        try:
                            if xpath_exists("//*[text()='Бить любого']"):
                                time.sleep(0.7)
                                driver.find_element(By.XPATH, "//*[text()='Бить любого']").click()
                        except Exception:
                            print('\033[1m\033[31m{}\033[0m'.format("не могу найти бить любого"))
                            driver.refresh()
                        finally:
                            continue


def throw_things():
    driver.get("https://vmmo.vten.ru/user/rack?filter=1")
    count = 1
    print("приступаю к разбокре вещей")
    while count > 0:
        try:
            count = 0
            for l in m_crack:
                if xpath_exists(f"//*[contains(text(),'{l}')]/ancestor::div[5]"):
                    driver.find_element(By.XPATH, f"//*[contains(text(),'{l}')]"
                                                  f"/ancestor::div[5]//a[contains(@href, 'crackLink')]").click()
                    count += 1
                    if text_exists("Да, точно"):
                        driver.find_element(By.PARTIAL_LINK_TEXT, "Да, точно").click()
                    time.sleep(0.2)
        except Exception:
            print('\033[1m\033[31m{}\033[0m'.format("Ошибка потерялась кнопка разбора"))
            pomeha()
    count = 1
    while count > 0:
        try:
            count = 0
            for i in m_open:
                if xpath_exists(f"//*[contains(text(),'{i}')]/ancestor::div[5]"):
                    driver.find_element(By.XPATH, f"//*[contains(text(),'{i}')]"
                                                  f"/ancestor::div[5]//a[contains(@href, 'openLink')]").click()
                    time.sleep(0.2)
                    count += 1
                    if text_exists("Да, точно"):
                        driver.find_element(By.PARTIAL_LINK_TEXT, "Да, точно").click()
        except Exception:
            print('\033[1m\033[31m{}\033[0m'.format("Ошибка потерялась кнопка разбора"))
            pomeha()
    print("Закончил идем дальше")


def metro_go():
    count = 0
    driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
    try:
        for key, value in data[f"{login}"].items():
            if count == 2:
                throw_things()
                count = 0
            url_metro = f"https://vmmo.vten.ru/dungeon/landing/{value}"
            driver.get(url=url_metro)
            time.sleep(0.3)
            pomeha()
            if text_exists("Открыть"):
                print("\033[32m{}\033[0m".format(f"метро {key} закрыто"))
                time.sleep(1)
            elif text_exists("Войти"):
                count += 1
                print("\033[32m{}\033[0m".format(f"ищу кнопку войти и захожу в подземелье {key}"))
                driver.find_element(By.PARTIAL_LINK_TEXT, 'Войти').click()
                driver.refresh()
                time.sleep(0.3)
                if xpath_exists("//*[contains(text(), 'Начать')]"):
                    print("ищу кнопку Начать бой")
                    try:
                        driver.find_element(By.XPATH, "//*[contains(text(), 'Начать')]").click()
                        print("кнопка начать бой найдена")
                        proverka_and_boi()
                    except Exception:
                        print('\033[1m\033[31m{}\033[0m'.format("Кнопка потерялась, распускаю Банду и иду в новое метро"))
                        driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
                    finally:
                        continue
                driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
                if text_exists("Продолжить"):
                    print("нашел кнопку Продолжить, ухожу из локации")
                    driver.find_element(By.PARTIAL_LINK_TEXT, 'Продолжить').click()
                    time.sleep(1)
                    pomeha()
            else:
                driver.refresh()
                time.sleep(1)
                driver.get("https://vmmo.vten.ru/city?ppAction=leaveParty")
    except Exception as _exc:
        print('\033[1m\033[31m{}\033[0m'.format("Какой-то косяк в цикле метрошки") + str(_exc))


def autorisarion():
    while True:
        url = f"https://vmmo.vten.ru/login/"
        driver.get(url=url)
        if xpath_exists("//*[text()='Обновить']"):
            driver.find_element(By.XPATH, "//*[text()='Обновить']")
            driver.refresh()
            time.sleep(20)
            driver.get("https://vmmo.vten.ru/login/")
        try:
            login_input = driver.find_element(By.ID, "login")
            login_input.clear()
            login_input.send_keys(f"{login}")
            pas_input = driver.find_element(By.ID, "password")
            pas_input.clear()
            pas_input.send_keys(f"{parol}")
            time.sleep(1)
            pas_input.send_keys(Keys.ENTER)
        except:
            break


with open('options/user_pass.json', 'r', encoding='utf-8') as f:
    users = json.load(f)

with open('options/pers_metro.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
n = []
print('\033[1m\033[33m{}\033[0m'.format('МИР ТЕНЕЙ! \n     ФАРМ ЭТО ВЕСЕЛО'))
print('')
print('\033[1m\033[35m{}\033[0m'.format('СОБЕРЕМ ВСЕ ДО ПОСЛЕДНЕГО МИНЕРАЛА'))
while True:
    for login, parol in users.items():
        options = webdriver.ChromeOptions()

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_argument("--window-size=700,1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4X Build/N2G47H) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.81 Mobile Safari/537.36")
        options.add_argument("--headless")
        # options.headless = healders_mode
        driver = webdriver.Chrome(options=options)
        # r'C:\Users\mikhail.maksimchenko\Documents\klickSmart\chromedriver\chromedriver.exe'
        # /home/muxan/PycharmProjects/klickSmart/chromedriver/chromedriver
        print('\033[36m{}\033[0m'.format(login))
        autorisarion()
        pomeha()
        metro_go()
        throw_things()
        print("Конец локации")
        driver.quit()
        time.sleep(10)
