// нагрузочное тестирование эндпоинта в сервисе psd-lastpoint-service
import { SharedArray } from "k6/data";
import http from 'k6/http';
import papaparse from "https://jslib.k6.io/papaparse/5.1.1/index.js";
import {  sleep, check } from 'k6';

const csvRead = new SharedArray("credentials", function() {
    return papaparse.parse(open('./client.csv'), {header: true}).data; // returning array
});


const url = 'https://psd-test.tech.mos.ru/web/session/authenticate'; //авторизация
const url_read = 'https://psd-test.tech.mos.ru/web/dataset/search_read'; //запросы
const url_open = 'https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.stp.work.order/default_get'; //открытие формы
const url_create = 'https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.stp.work.order/create' // создание заявки нарядов
const url_cancel = 'https://psd-test.tech.mos.ru/web/dataset/call_button' //отмена заявки
// //============ параметры обработки данных в нашем случае application/json
const params = {
  headers: {
    'Content-Type': 'application/json',
  },
};



//export const options = {
    //количество виртуальных пользователей
//    vus: 50,
    //промежуток времени в течении которого отправляются запросы
//    duration: '1h',
//    };
//scenarios: {
//   test_api: {
//    executor: 'constant-vus',
//      exec: 'test_api',
//      vus: 5,
//      duration: '1h',
//    },
//    ets_test: {
//      executor: 'constant-vus',
//      exec: 'test_ets',
//      vus: 2,
//      duration: '1h',
//    },
//    test_users: {
//        executor: 'constant-vus',
//        exec: 'test_users',
//        vus: 3,
//         duration: '1h',
//       },
//   },
//   thresholds: {
//     'checks{scenario:test_users}': [{ threshold: 'rate>0.95', abortOnFail: true }],

     //'checks{scenario:test_users}': ['rate>0.95'],
//     //'checks{scenario:ets_test}': ['rate>0.95'],
//     //'checks{scenario:test_api}': ['rate>0.95', ],
//   },
    
// };

export const options = {
  scenarios: {
    test_api: {
      "executor": "ramping-vus",
      "exec": "test_api",
      "stages": [
        { "duration": "1m", "target": 10 },
        { "duration": "3m", "target": 10 },
        { "duration": "1m", "target": 20 },
        { "duration": "3m", "target": 20 },
        { "duration": "1m", "target": 35 },
        { "duration": "3m", "target": 35 },
        { "duration": "1m", "target": 40 },
        { "duration": "3m", "target": 40 },
        { "duration": "1m", "target": 45 },
        { "duration": "3m", "target": 45 }

      ]
    },
    ets_test: {
      "executor": "ramping-vus",
      "exec": "test_ets",
      "stages": [
        { "duration": "1m", "target": 30 },
        { "duration": "3m", "target": 30 },
        { "duration": "1m", "target": 40 },
        { "duration": "3m", "target": 40 },
        { "duration": "1m", "target": 55 },
        { "duration": "3m", "target": 55 },
        { "duration": "1m", "target": 70 },
        { "duration": "3m", "target": 70 },
        { "duration": "1m", "target": 90 },
        { "duration": "3m", "target": 90 }
      ]
    },
    test_users: {
      "executor": "ramping-vus",
      "exec": "test_users",
      "stages": [
        { "duration": "1m", "target": 30 },
        { "duration": "3m", "target": 30 },
        { "duration": "1m", "target": 40 },
        { "duration": "3m", "target": 40 },
        { "duration": "1m", "target": 55 },
        { "duration": "3m", "target": 55 },
        { "duration": "1m", "target": 70 },
        { "duration": "3m", "target": 70 },
        { "duration": "1m", "target": 90 },
        { "duration": "3m", "target": 90 }
      ]
    },
  },
  thresholds: {
    'checks{scenario:test_users}': [{ threshold: 'rate>0.95', abortOnFail: true }],
    'checks{scenario:ets_test}': [{ threshold: 'rate>0.95', abortOnFail: true }],
    //'checks{scenario:test_users}': ['rate>0.95'],
//     //'checks{scenario:ets_test}': ['rate>0.95'],
//     //'checks{scenario:test_api}': ['rate>0.95', ],
  },
};






export function test_api() {
    //for (let data of csvRead){
    //     console.log(JSON.stringify(data['client']));
    // }
    var client = csvRead[Math.floor(Math.random() * csvRead.length)]['client'];

    let h = {
        headers: {
           'Content-Type': 'application/json'
        }
    }

    let res = http.get(
        'https://psd-test.tech.mos.ru/points/?client=' + client,
        h
    );
    check(res, {
       'status is 200': (r) => r.status === 200,
     });
    console.log('client: ' + client, 'status: ' + res.status)

    res = http.get(
        'https://psd-test.tech.mos.ru/points/sensor?client=' + client,
        h
    );
    check(res, {
      'status is 200': (r) => r.status === 200,
      });
    console.log('sensor_client: ' + client, 'status: ' + res.status)  
};



export function test_ets() {
    let h = {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    }

    var client = csvRead[Math.floor(Math.random() * csvRead.length)]['client'];
    // console.log('headers Content-Type: ', h.headers['Content-Type'])

    let response = http.post(
        'https://psd-test.tech.mos.ru/ets/login', 
        'login=root@localhost&password=********',
        h
    );
    //console.log('response status: ', response.status)
    //console.log('response body: ', response.body)
    //console.log(response.status)
    //uptimeTrendCheckLogin.add(response.timings.duration);
    //sleep(1)
    let token = response.json().token
    //console.log('token: ', token)
    h.headers['Content-Type'] = 'application/json'
    h.headers['Authorization'] = 'Bearer ' + token


    console.log('Client: ', client)
    const z = JSON.stringify({"bnso_list": [client], 
    "start_date": "2023-01-25",
     "end_date": "2023-01-26"
    });
    
    let res = http.post('https://psd-test.tech.mos.ru/ets/api/recalc_leak_refills', z, h);
    //console.log('response status: ', res.status)
    console.log('response body: ', res.body)
    sleep(Math.floor(Math.random() * 10))
    //console.log('response status: ', response.status)
    //console.log('response body: ', response.body)
    check(res, {
        'status is 200': (r) => r.status === 200,
    //    'is authenticated': (r) => r.json().authenticated === true,
        //'is correct user': (r) => r.json().user === username,
      });
    // console.log('headers Content-Type: ', h.headers['Content-Type'])
    // console.log('headers Authorization: ', h.headers['Authorization'])
}



export function test_users() {
    //==================== Сценарий 1 Редактирование наряда (СТП)===============================
    // 1.	Авторизоваться в Подсистеме;
    // 2.	Нажать на вкладку «СТП»;
    // 3.	Нажать меню «Наряды»;
    // 4.	Выбрать любой наряд в статусе «Новый» (можно выбрать наряд, созданный в предыдущем шаге) и нажать на запись;
    // 5.	Нажать кнопку «Редактировать»;
    // 6.	В поле «Время устранения, ч» изменить число таким образом, чтобы новое число было от 1 до 168;
    // 7.	Нажать кнопку «Сохранить».
  
    sleep(Math.floor(Math.random() * 10))
    const payload = JSON.stringify({
      params:{
      db:'estp',
      login: 'root@localhost',
      password: '123',
    }});
    
    // ================ авторизация пользователя ================================
    let res_auto = http.post(url, payload, params); 
    let session = res_auto.json().result["session_id"]
    console.log('session: ', session)
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    //--------------------------2й шаг-----------------------------
    // ===========переход на вкладку СТП/наряды =================================
    const z = JSON.stringify({"jsonrpc":"2.0",
    "method":"call",
    "params":{"model":"estp.stp.work.order",
    "fields":["order_name","executor_id","comment","start_date","end_date",
    "state","elimination_time","sla_remain_time","is_overdue_sla"],"domain":[],
    "context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,"params":{"action":92},
    "bin_size":true},"offset":0,"limit":80,"sort":""}}
    );
    ////////////////////////////////////////////////////////////
    let res_naryad = http.post(url_read,z, params);
    console.log('response status: ', res_naryad.status)
    //console.log('сокращенный ответ' , res.body)
    check(res_naryad, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    //------------------------------------3й шаг-----------------------------------
    // =====================Выбрать любой наряд в статусе «Новый» (можно выбрать наряд, созданный в предыдущем шаге) и нажать на запись=============
  
    const q = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.work.order","method":"default_get",
      "args":[["comment","message_ids","elimination_time","claim_ids","state",
      "start_date","executor_id","end_date","sla_remain_time","order_name"]],
      "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,
      "params":{"action":92}}}}}
    )
    const res_new_starus = http.post(url_open,q, params);
    console.log('response status: ', res_new_starus.status)
    console.log(res_new_starus.body)
    check(res_new_starus, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    //-------------------------5 шаг ------------------------------------
    //================ Сохранение заявки наряда===========================
    let c = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.work.order","method":"create",
      "args":[{"state":"new","executor_id":2,"comment":false,"elimination_time":Math.floor(Math.random() * 167) + 1,
      "claim_ids":[],"message_ids":false}],
      "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,"params":{"action":92}}}}}
    )
    const res_save = http.post(url_create,c, params);
    console.log('response status: ', res_save.status)
    console.log('созданная заявка' ,res_save.body)
    check(res_save, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    //====================================================================
    //====================Сценарий 2 =====================================
    
    // 1.	Авторизоваться в Подсистеме;
    // 2.	Нажать на вкладку «СТП»;
    // 3.	Нажать меню «Наряды»;
    // 4.	Выбрать любой наряд в статусе «Новый» (можно выбрать наряд, созданный в предыдущем шаге);
    // 5.	Нажать кнопку «Отменён».
    //====================================================================
    let result_naryad = res_save.json().result
    console.log(result_naryad)  //номера заявки наряда
  
    res_auto;  // авторизация пользователя
    res_auto.json().result["session_id"]
    console.log('session 2.0: ', session)
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
  
    res_naryad; // переход на вкладку стп/ наряды
    check(res_naryad, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    // переход на форму наряда недавно созданного
    let a = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"ir.attachment",
      "fields":["name","url","type","create_uid","create_date","write_uid","write_date"],
      "domain":[["res_model","=","estp.stp.work.order"],["res_id","=",result_naryad],
      ["type","in",["binary","url"]]],"context":{"lang":"ru_RU","tz":"Europe/Moscow",
      "uid":1,"params":{"action":92}},"offset":0,"limit":false,"sort":""}}
    )
    let res_open = http.post(url_read,a, params);
    console.log('response status: ', res_open.status)
    console.log('сокращенный ответ' , res_open.body)
    check(res_open, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    // действие на отмену созданного наряда. 
    let b = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.work.order",
      "method":"action_cancel","domain_id":null,
      "context_id":1,"args":[[result_naryad],
      {"lang":"ru_RU","tz":"Europe/Moscow","uid":1,"params":{"action":92}}]}}
    )
    let rec_cancel = http.post(url_cancel,b, params);
    console.log('response status: ', rec_cancel.status)
    console.log('сокращенный ответ' , rec_cancel.body)
    check(rec_cancel, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    //=====================================================================================
    //============ Сценарий 3 =========================
    // Создание записи справочника «Неисправности БНСО и датчиков» (Справочники)
    //-------------------------------------------------------------------------------------
    // 1.	Авторизоваться в Подсистеме;
    // 2.	В разделе «Справочники» выбрать меню «Неисправности БНСО и датчиков»;
    // 3.	Выбрать любую существующую неисправность и нажать на запись;
    // 4.	Снять/установить чекбокс атрибута «Активность» и нажать кнопку «Сохранить».
    
    res_auto;  // авторизация пользователя
    res_auto.json().result["session_id"]
    console.log('session 2.0: ', session)
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
    // переход в раздел Справочники/ Неисправности БНСО и датчиков
  
    const с = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.malfunction",
      "fields":["name","is_activity"],"domain":[],
      "context":{"lang":"ru_RU","tz":"Europe/Moscow",
      "uid":1,"params":{"action":177},"bin_size":true},
      "offset":0,"limit":80,"sort":""}}
    );
    ////////////////////////////////////////////////////////////
    let res_d = http.post(url_read,с, params);
    console.log('response status: ', res_d.status)
    //console.log('сокращенный ответ' , res.body)
    check(res_d, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    // Выбрать любую существующую неисправность и нажать на запись;
    const coun = Math.floor(Math.random() * 5) + 1
    const d = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.malfunction","method":"search_read","args":[[["id","in",[coun]]],
      ["name","is_activity"]],
      "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,
      "params":{"action":177}}}}
    }
    );
    let res_op = http.post('https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.stp.malfunction/search_read',d, params)
    console.log('response status: ', res_op.status)
    check(res_op, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
    // Снять/установить чекбокс атрибута «Активность» и нажать кнопку «Сохранить».
    const e = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.stp.malfunction",
      "method":"write","args":[[coun],{"is_activity":Math.random() < 0.5}],
      "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow",
      "uid":1,"params":{"action":177}}}}}
    );
    let res_s = http.post('https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.stp.malfunction/write',e, params)
    console.log('response status: ', res_s.status)
    check(res_s, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    //========================================================================================
    
    //============= Сценарий 4 ===============================
    // Редактирование записи в реестре «Оборудование» (Реестры)
    // 1.	Авторизоваться в Подсистеме;
    // 2.	Нажать на вкладку «Реестры»;
    // 3.	Нажать меню «Оборудование»;
    // 4.	Выбрать любую существующую запись оборудования и нажать на неё;
    // 5.	Нажать кнопку «Редактировать»;
    // 6.	Снять/установить признак «ДУТ установлены в одном топливном бак»
    // 7.	Нажать кнопку «Сохранить»
  
  //-----------------------------------------------------------
    //авторизация
    res_auto;  // авторизация пользователя
    res_auto.json().result["session_id"]
    console.log('session 2.0: ', session)
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
    // переход на вкладку реестры
    const f = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.registers.organization",
      "fields":["name","short_name","region_id"],"domain":[],
      "context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,
      "params":{"action":78},"bin_size":true},"offset":0,"limit":80,"sort":""}}
    );
    let res_reestr = http.post(url_read,f, params);
    console.log('response status: ', res_reestr.status)
    check(res_reestr, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    // Все что выше РАБОТАЕТ!!!
    // переход в меню оборудование
    let h = JSON.stringify(
      
    {"jsonrpc":"2.0","method":"call","params":{"model":"estp.registers.equipment",
    "fields":["name","type_id","vehicle_id","gos_number","model",
    "construct_type","func_type","start_date","end_date"],
    "domain":[],"context":{"lang":"ru_RU","tz":"Europe/Moscow",
    "uid":1,"params":{"action":161},"bin_size":true},"offset":0,"limit":80,"sort":""}
    }
    );
    let res_oborud = http.post(url_read,h, params);
    console.log('response status переход в меню оборудование: ', res_oborud.status)
    check(res_oborud, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    const coun_1 = Math.floor(Math.random() * 150) + 1
    console.log('номер для записи', coun_1)
    // Выбрать любую существующую запись оборудования и нажать на неё;
    h = JSON.stringify({"jsonrpc":"2.0","method":"call",
    "params":{"model":"ir.attachment","fields":["name","url","type","create_uid",
    "create_date","write_uid","write_date"],"domain":[["res_model","=","estp.registers.equipment"],
    ["res_id","=",coun_1],["type","in",["binary","url"]]],"context":{"lang":"ru_RU","tz":"Europe/Moscow",
    "uid":1,"params":{"action":161}},"offset":0,"limit":false,"sort":""}}
      );
    let res_open_form = http.post(url_read,h, params);
    console.log('response status вход в запись: ', res_open_form.status)
    check(res_open_form, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
  
      // 	Нажать кнопку «Редактировать» установить/снять чекбокс дут установлены в одном баке
      h = JSON.stringify({"jsonrpc":"2.0","method":"call",
      "params":{"model":"estp.registers.equipment","method":"write",
      "args":[[coun_1],{"is_one_fuel_tank":Math.random() < 0.5}],
      "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,
      "params":{"action":161}}}}}
      );
      let res_save_form = http.post('https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.registers.equipment/write',h, params);
      console.log('response status: ', res_save_form.status)
      check(res_save_form, {
        'status is 200': (r) => r.status === 200,
      });
      sleep(Math.floor(Math.random() * 10))
  //=================================================================================================
  // ==== Сценарий 5  Просмотр Отчета Отчет об исправности датчиков ГЛОНАСС =======
  // 1.	Авторизоваться в Подсистеме;
  //  2.	Нажать на вкладку «Отчеты»;
  // 3.	Нажать меню «Похожие треки»; 
  // 
    res_auto;
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
    // переход на вкладку отчеты
    h = JSON.stringify({"jsonrpc":"2.0","method":"call",
    "params":{"model":"estp.reports.config","method":"get_report_template",
    "args":[],"kwargs":{"name":"report_map"}}}
      );
      let res_map = http.post('https://psd-test.tech.mos.ru/web/dataset/call_kw/estp.reports.config/get_report_template',h, params);
      console.log('response status: ', res_map.status)
      check(res_map, {
        'status is 200': (r) => r.status === 200,
      });
      sleep(Math.floor(Math.random() * 10))
  
      // ===================================================
      //=========== Сценарий 6 ============================
      //===========Редактирование наряда (СТП)===============
  
      res_auto;
      res_auto.json().result["session_id"]
      check(res_auto, {
        'status is 200': (r) => r.status === 200,
      });
    
      res_naryad; // переход на вкладку стп/ наряды
      check(res_naryad, {
        'status is 200': (r) => r.status === 200,
      });
      sleep(Math.floor(Math.random() * 10))
    
      // переход на форму наряда недавно созданного
      a = JSON.stringify(
        {"jsonrpc":"2.0","method":"call",
        "params":{"model":"ir.attachment",
        "fields":["name","url","type","create_uid","create_date","write_uid","write_date"],
        "domain":[["res_model","=","estp.stp.work.order"],["res_id","=",result_naryad],
        ["type","in",["binary","url"]]],"context":{"lang":"ru_RU","tz":"Europe/Moscow",
        "uid":1,"params":{"action":92}},"offset":0,"limit":false,"sort":""}}
      )
    res_open = http.post(url_read,a, params);
    console.log('response status: ', res_open.status)
    console.log('сокращенный ответ' , res_open.body)
    check(res_open, {
        'status is 200': (r) => r.status === 200,
      });
    sleep(Math.floor(Math.random() * 10))
  
    // сохранение наряда
      //================  Изменение и сохранение заявки наряда===========================
    c = JSON.stringify(   
    {"jsonrpc":"2.0","method":"call","params":{"model":"estp.stp.work.order",
    "method":"write","args":[[result_naryad],{"elimination_time":Math.floor(Math.random() * 167) + 1}],
    "kwargs":{"context":{"lang":"ru_RU","tz":"Europe/Moscow",
    "uid":1,"params":{"action":92}}}}}
    )
    const res_save_edit = http.post(url_create,c, params);
    console.log('response status: ', res_save_edit.status)
    console.log('созданная заявка' ,res_save_edit.body)
    check(res_save_edit, {
      'status is 200': (r) => r.status === 200,
    });
    sleep(Math.floor(Math.random() * 10))
    //=========================================================================
    //сценарий 7. Нажатие и просмотр инцидентов
    res_auto;
    res_auto.json().result["session_id"]
    check(res_auto, {
      'status is 200': (r) => r.status === 200,
    });
  
        // переход на форму наряда недавно созданного
    a = JSON.stringify(
      {"jsonrpc":"2.0","method":"call",
      "params":{"model":"ir.attachment",
      "fields":["name","url","type","create_uid",
      "create_date","write_uid","write_date"],
      "domain":[["res_model","=","estp.stp.incident"],["res_id","=",34272],["type","in",["binary","url"]]],
      "context":{"lang":"ru_RU","tz":"Europe/Moscow","uid":1,"params":{"action":89}},
      "offset":0,"limit":false,
      "sort":""}}
    )
    res_open = http.post(url_read,a, params);
    console.log('response status: ', res_open.status)
    console.log('сокращенный ответ' , res_open.body)
    check(res_open, {
          'status is 200': (r) => r.status === 200,
    });
  }
  
