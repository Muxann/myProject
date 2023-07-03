// нагрузочное тестирование эндпоинтов (login и recalc_leak_refills) взаимодействующих с odoo в сервисе psd-ets
import { SharedArray } from "k6/data";
import http from 'k6/http';
//import { Trend } from 'k6/metrics';
import { sleep, check } from 'k6';
import papaparse from "https://jslib.k6.io/papaparse/5.1.1/index.js";
//const uptimeTrendCheckLogin = new Trend('/POST API login uptime');
//const uptimeTrendCheckRecalc = new Trend('/POST API recalc uptime');
const csvRead = new SharedArray("credentials", function() {
    return papaparse.parse(open('./client.csv'), {header: true}).data; // returning array
});
export const options = {
    //количество виртуальных пользователей
    vus: 20,
    //промежуток времени в течении которого отправляются запросы
    duration: '1h',
 //   stages: [
 //       { duration: '2m', target: 200 }, // simulate ramp-up of traffic from 1 to 200 users over 2 minutes.
 //       { duration: '10m', target: 200 }, // stay at 100 users for 10 minutes
 //       { duration: '2m', target: 0 }, // ramp-down to 0 users
 //     ],
};

export default function () {
    let h = {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    }

    var client = csvRead[Math.floor(Math.random() * csvRead.length)]['client'];
    // console.log('headers Content-Type: ', h.headers['Content-Type'])

    let response = http.post(
        'https://psd-test.tech.mos.ru/ets/login', 
        'login=root@localhost&password=*******',
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
    sleep(Math.floor(Math.random() * 40))
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
