// нагрузочное тестирование эндпоинта в сервисе psd-lastpoint-service
import { SharedArray } from "k6/data";
import http from 'k6/http';
import papaparse from "https://jslib.k6.io/papaparse/5.1.1/index.js";
import { check } from 'k6';

const csvRead = new SharedArray("credentials", function() {
    return papaparse.parse(open('./client.csv'), {header: true}).data; // returning array
});


export const options = {
    
    //количество виртуальных пользователей
    vus: 50,
    //промежуток времени в течении которого отправляются запросы
    duration: '30s',
    };

export default function () {
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
       'status is 200 points client': (r) => r.status === 200,
     });
    console.log('client: ' + client, 'status: ' + res.status)

    res = http.get(
        'https://psd-test.tech.mos.ru/points/sensor?client=' + client,
        h
    );
    check(res, {
        'status is 200 ': (r) => r.status === 200,
      });
    console.log('sensor_client: ' + client, 'status: ' + res.status)  
};