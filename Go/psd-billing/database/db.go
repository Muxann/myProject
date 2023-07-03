package database

import (
	"database/sql"
	"fmt"
	"github.com/go-gorp/gorp"
	_ "github.com/lib/pq"
	"psd-billing2/models"
	"time"
)

// Инициализация базы
func InitDb(dbConnStr string) (*gorp.DbMap, error) {
	// initialize db connection
	var dbmap *gorp.DbMap

	db, err := sql.Open("postgres", dbConnStr)
	if err != nil {
		return dbmap, fmt.Errorf("DB connection error: %s\n", err)
	}

	dbmap = &gorp.DbMap{Db: db, Dialect: gorp.PostgresDialect{}}

	return dbmap, err
}

// Получет активный контракт на заданную дату
func GetActualContract(dbmap *gorp.DbMap, currentDate string) (int64, error) {
	return dbmap.SelectInt(
		`SELECT id FROM estp_billing_contract WHERE (:currentDate::DATE BETWEEN start_date AND end_date)`,
		map[string]interface{}{
			"currentDate": currentDate,
		},
	)
}

// Метод для получения действующего списка ТС по актуальному контракту
func GetActualContractVehicles(dbmap *gorp.DbMap, contractId int64, currentDate string) (models.ContractVehicleList, error) {
	var cvl models.ContractVehicleList

	_, err := dbmap.Select(&cvl,
		`SELECT DISTINCT ON (ervv.vehicle_id)
			  ervv.vehicle_id as VehicleId,
			  erb.id as BnsoId,
			  ervv.name as GosNumber,
			  erb.name as BnsoCode,
			  ervv.condition as VehicleState,	
			  erb.is_executor_bnso as ExecutorBnso
			FROM estp_billing_vehicle_contract ebvc
			  INNER JOIN estp_registers_vehicle_version ervv on ebvc.vehicle_id = ervv.vehicle_id
			  LEFT JOIN estp_registers_vehicle_bnso ervb on ervv.vehicle_id = ervb.vehicle_id
			  LEFT JOIN estp_registers_bnso erb ON erb.id = ervb.bnso_id
			WHERE (:currentDate::DATE BETWEEN ervb.start_date AND ervb.end_date)
			      AND (:currentDate::DATE BETWEEN erb.start_date AND erb.end_date)
				  AND (:currentDate::DATE BETWEEN ervv.start_date AND ervv.end_date)
				  AND (:currentDate::DATE BETWEEN ebvc.start_date AND ebvc.end_date)
				  AND contract_id = :contractId
			ORDER BY ervv.vehicle_id, erb.name DESC;`,
		map[string]interface{}{
			"contractId":  contractId,
			"currentDate": currentDate,
		})
	return cvl, err
}

// получение всех точек по БНСО

func GetBnsoTrackData(bnso string, dateBilling time.Time) (models.BnsoPackages, error) {
	// т.к. в агрегаторе партиции создаются по уборочным суткам а биллинг считается по календарным, выбор точек
	// происходит из двух партиций
	partitionName := fmt.Sprintf("sh_dwh.bnso_data_t%s", dateBilling.Format("20060102"))

	additionalDate := dateBilling.Add(-time.Hour * 24).Format("20060102")
	additionalPartitionName := fmt.Sprintf("sh_dwh.bnso_data_t%s", additionalDate)

	query := fmt.Sprintf("SELECT bnso_code AS Client,"+
		"navigate_date    AS \"TimeStamp\","+
		"receive_date     AS DateCreate,"+
		"nph_request_id   AS NphRequestId,"+
		"speed            AS SpeedAvg,"+
		"lat              AS Latitude,"+
		"lon              AS Longitude,"+
		"pdop             AS Pdop,"+
		"dut              AS FuelSensorData,"+
		"kbm              AS KbmSensorData "+
		"FROM %s "+
		"WHERE nph_request_id not in (0, 1, 3, 4, 10, 11, 500) and bnso_code = :bnso "+
		"and navigate_date between :billingDate :: timestamp without time zone and :billingDate :: timestamp without time zone + interval '23 hours 59 minutes 59 seconds' "+
		"and receive_date between :billingDate :: timestamp without time zone and :billingDate :: timestamp without time zone + interval '1 day 23 hours 59 minutes 59 seconds' "+
		"union all "+
		"SELECT bnso_code        AS Client,"+
		"navigate_date    AS \"TimeStamp\","+
		"receive_date     AS DateCreate,"+
		"nph_request_id   AS NphRequestId,"+
		"speed            AS SpeedAvg,"+
		"lat              AS Latitude,"+
		"lon              AS Longitude,"+
		"pdop             AS Pdop,"+
		"dut              AS FuelSensorData,"+
		"kbm              AS KbmSensorData "+
		"FROM %s "+
		"WHERE nph_request_id not in (0, 1, 3, 4, 10, 11, 500) and bnso_code = :bnso "+
		"and navigate_date between :billingDate :: timestamp without time zone and :billingDate :: timestamp without time zone + interval '23 hours 59 minutes 59 seconds' "+
		"and receive_date between :billingDate :: timestamp without time zone and :billingDate :: timestamp without time zone + interval '1 day 23 hours 59 minutes 59 seconds' "+
		"ORDER BY NphRequestId", partitionName, additionalPartitionName)

	// Строка подключения к базе данных PostgreSQL AG2

	connStrAg2 := "user=postgres dbname=vts password=Xae4aep9 host=10.127.32.86 port=5432 sslmode=disable"

	aggdbmap, err := InitDb(connStrAg2)
	if err != nil {
		return nil, err
	}
	defer aggdbmap.Db.Close()
	points := models.BnsoPackages{}

	_, err = aggdbmap.Select(&points, query,
		map[string]interface{}{
			"bnso":        bnso,
			"billingDate": dateBilling,
		},
	)

	return points, err
}

// закешировать датчики и статусы
// метод получения периодов эксплуатации у ТС и сохранение результата в хеш таблицу

func GetVehicleStates(dbmap *gorp.DbMap, dateBilling time.Time) (map[int64][]models.VehicleState, error) {
	dateBilling1 := dateBilling.Add(-24 * time.Hour)

	// Создайте хеш-таблицу для хранения результатов
	vehicleStates := make(map[int64][]models.VehicleState)

	// Выполните запрос SELECT с использованием dbmap.Select
	rows, err := dbmap.Query(
		`SELECT vehicle_id, start_date, end_date
		FROM estp_registers_vehicle_state_history
		WHERE state_id = 3 AND start_date >= $1 AND start_date <= $2`, dateBilling1, dateBilling)

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	// Обработка строк результата запроса
	for rows.Next() {
		var vehicleId int64
		var startDate, endDate time.Time
		err := rows.Scan(&vehicleId, &startDate, &endDate)
		if err != nil {
			return nil, err
		}

		// Добавление данных в хеш-таблицу
		if _, ok := vehicleStates[vehicleId]; !ok {
			vehicleStates[vehicleId] = []models.VehicleState{}
		}
		vehicleStates[vehicleId] = append(vehicleStates[vehicleId], models.VehicleState{
			StartDate: startDate,
			EndDate:   endDate,
		})
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return vehicleStates, nil
}

// метод получения значений тарировок для датчиков у всех БНСО за расчетную дату
// в расчет должны попадать датчики, которые на дату расчета были включены в техническую поддержку
// результатом является хеш таблица где bnsoId ключ а данные по датчикам значение таблицы
// Поменять запрос !!! на будущее
func GetBnsoCalibration(dbmap *gorp.DbMap, date time.Time) (map[int64][]models.SensorCalibration, error) {

	// Выполнение SELECT-запроса и получение результатов

	rows, err := dbmap.Query(`
		SELECT
			erb.id as BnsoId,
			ers.id as SensorId,
			CASE WHEN ers.sensor_type_id = 2 THEN min(CASE WHEN coalesce(ep.bit::boolean, false) THEN 0 ELSE cv.raw_value end) ELSE 0 END MinRawValue,
			max(CASE WHEN coalesce(ep.bit::boolean, false) THEN 1 ELSE cv.raw_value end) as MaxRawValue,
			CASE WHEN ers.sensor_type_id = 2 THEN 'fuel' ELSE 'kbm' END SensorType
		FROM estp_billing_vehicle_contract ebvc
			INNER JOIN estp_registers_vehicle erv ON ebvc.vehicle_id = erv.id
			INNER JOIN estp_registers_vehicle_bnso ervb on erv.id = ervb.vehicle_id
			INNER JOIN estp_registers_bnso erb ON erb.id = ervb.bnso_id
			INNER JOIN estp_billing_vehicle_support_sensor ebvss ON ebvc.id = ebvss.vehicle_contract_id
			INNER JOIN estp_registers_sensor ers ON ers.id = ebvss.sensor_id
			INNER JOIN estp_registers_egts_protocol ep ON ers.protocol_field_id = ep.id
			LEFT JOIN estp_registers_calibration_table ct ON ebvss.sensor_id = ct.sensor_id
			LEFT JOIN estp_registers_calibration_value cv ON ct.id = cv.calibration_id
		WHERE raw_value IS NOT NULL
			AND $1 BETWEEN ebvss.start_date AND ebvss.end_date
			AND $1 BETWEEN ervb.start_date AND ervb.end_date
		GROUP BY erb.id, ers.id, ers.sensor_type_id`, date)

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	result := make(map[int64][]models.SensorCalibration)

	for rows.Next() {
		var BnsoId, SensorId int64
		var MinRawValue, MaxRawValue float64
		var SensorType string
		err := rows.Scan(&BnsoId, &SensorId, &MinRawValue, &MaxRawValue, &SensorType)
		if err != nil {
			return nil, err
		}
		// Добавление данных в хеш-таблицу
		if _, ok := result[BnsoId]; !ok {
			result[BnsoId] = []models.SensorCalibration{}
		}
		result[BnsoId] = append(result[BnsoId], models.SensorCalibration{
			SensorId:    SensorId,
			MinRawValue: MinRawValue,
			MaxRawValue: MaxRawValue,
			SensorType:  SensorType,
		})
	}

	return result, err
}

// очистка старых результатов, на случай пересчета
func RemoveOldBillingData(dbmap *gorp.DbMap, date string) error {
	if _, err := dbmap.Exec(
		`DELETE FROM estp_billing_billing WHERE date = :date`,
		map[string]interface{}{
			"date": date,
		},
	); err != nil {
		return err
	}

	return nil
}

// Метод для получения услуг
func GetPriceBillingService(dbmap *gorp.DbMap, currentDate string) (models.ServicePrices, error) {
	prices := models.ServicePrices{}
	var servicesPrice []models.BillingServicePrice

	_, err := dbmap.Select(&servicesPrice, `SELECT
		  ebbs.code as Code,
		  ebcbs.price as Price
		FROM estp_billing_contract ebc
		  INNER JOIN estp_billing_contract_billing_service ebcbs ON ebc.id = ebcbs.contract_id
		  INNER JOIN estp_billing_billing_service ebbs ON ebcbs.billing_service_id = ebbs.id
		WHERE (:currentDate::DATE BETWEEN ebc.start_date AND ebc.end_date)`,
		map[string]interface{}{
			"currentDate": currentDate,
		},
	)
	if err != nil {
		return prices, err
	}

	for _, p := range servicesPrice {
		prices[p.Code] = p.Price
	}

	return prices, err
}
