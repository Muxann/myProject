package services

import (
	"github.com/go-gorp/gorp"
	"psd-billing2/database"
	"psd-billing2/models"
	"time"
)

//метод, который возвращает хеш таблицы со статусами и с со значениями датчиков за расчетные сутки по каждому БНСО

func GetHashTables(dbmap *gorp.DbMap, dateBilling time.Time) (map[int64][]models.VehicleState, map[int64][]models.SensorCalibration, error) {
	vehicleStates, err := database.GetVehicleStates(dbmap, dateBilling)
	if err != nil {
		return nil, nil, err
	}

	bnsoCalibration, err := database.GetBnsoCalibration(dbmap, dateBilling)
	if err != nil {
		return nil, nil, err
	}

	return vehicleStates, bnsoCalibration, nil
}

//func CalculationBilling(h *rest.Handler, contractVehicle models.ContractVehicle, srvPrices models.ServicePrices,
//	contractId int64, billingDateStr string, billingDate time.Time, vehicleCount int) error {
//
//	//maxBillingPrice := float64(0)
//
//	billingRecord := models.Billing{
//		CreateUid:      models.ADMINISTRATOR_ID,   //есть
//		WriteUid:       models.ADMINISTRATOR_ID,   // есть
//		CreateDate:     time.Now(),                // текущая дата
//		WriteDate:      time.Now(),                // текущас дата
//		VehicleId:      contractVehicle.VehicleId, // VehicleId есть в наличии
//		BnsoId:         contractVehicle.BnsoId,    // есть в наличии
//		ContractId:     contractId,                // контракт на текущую дату
//		Date:           billingDate,               // дата билинга вводится в ручную
//		GosNumber:      contractVehicle.GosNumber, // гос номер
//		BnsoCode:       contractVehicle.BnsoCode,  // БНСО код есть в структуре
//		VehicleSummary: vehicleCount,              // ??????
//		SummaryPrice:   0,                         // ??????
//	}
//
//	// получение по БНСО и дате
//	bnsoTrackData, err := database.GetBnsoTrackData(contractVehicle.BnsoCode, billingDate)
//	if err != nil {
//		return fmt.Errorf("Couldn't get bnso point for analisys: %v\n", err)
//	}
//	return nil
//
