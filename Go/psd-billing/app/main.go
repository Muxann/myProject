package main

import (
	"fmt"
	"psd-billing2/database"
	"psd-billing2/models"
	"psd-billing2/services"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	//Ввод даты с консоли
	fmt.Print("Введите дату биллинга (в формате ГГГГ-ММ-ДД): ")
	var currentDate string
	fmt.Scanln(&currentDate)

	// Преобразование строки с датой в объект time.Time
	// функция которая вызывает кеш на определенную дату!
	billingDate, err := time.Parse("2006-01-02", currentDate)
	if err != nil {
		println("Ошибка при парсинге даты:", err)
	}
	fmt.Println(billingDate)
	connStr := "user=postgres dbname=estp_local password=postgres host=127.0.0.1 port=5432 sslmode=disable"

	dbConnectMap, err := database.InitDb(connStr)

	// получение хеш таблиц
	hashVehicleStates, hashBnsoCalibration, err := services.GetHashTables(dbConnectMap, billingDate)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("размер хеш-таблицы статусов ", len(hashVehicleStates))
	fmt.Println("размер хеш-таблицы датчиков ", len(hashBnsoCalibration))

	contractId, err := database.GetActualContract(dbConnectMap, currentDate)

	//список ТС по актуальному контракту
	actualContractVehicle, err := database.GetActualContractVehicles(dbConnectMap, contractId, currentDate)
	//
	// Вывод результатов 2022-08-02
	fmt.Println("список ТС по актуальному контракту", len(actualContractVehicle))
	count := 0
	for _, vehicle := range actualContractVehicle {
		k := CalculationBilling(vehicle, 8, billingDate)
		fmt.Println(k)
		count += 1
	}

	//Ввод БНСО с консоли
	fmt.Print("Введите код БНСО машины по которому надо посчтитать билинг: ")
	var desiredBnso string
	fmt.Scanln(&desiredBnso)

}

func CalculationBilling(contractVehicle models.ContractVehicle,
	contractId int64, billingDate time.Time) error {
	//maxBillingPrice := float64(0)

	billingRecord := models.Billing{
		CreateUid:  models.ADMINISTRATOR_ID,
		WriteUid:   models.ADMINISTRATOR_ID,
		CreateDate: time.Now(),
		WriteDate:  time.Now(),
		VehicleId:  contractVehicle.VehicleId,
		BnsoId:     contractVehicle.BnsoId,
		ContractId: contractId,
		Date:       billingDate,
		GosNumber:  contractVehicle.GosNumber,
		BnsoCode:   contractVehicle.BnsoCode,
		//	//VehicleSummary: vehicleCount,
		//	SummaryPrice: 0,
	}

	fmt.Println(billingRecord)

	bnsoTrackData, err := database.GetBnsoTrackData(contractVehicle.BnsoCode, billingDate)
	if err != nil {
		return fmt.Errorf("Couldn't get bnso point for analisys: %v\n", err)
	}

	firstPkg, err := bnsoTrackData.GetFirstPackageNumber()
	if err != nil {
		return err
	}

	return err

}
