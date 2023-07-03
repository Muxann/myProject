package models

import (
	"database/sql"
	"fmt"
	"time"
)

// Структура, соответствующая таблице в базе данных из estp
type ContractVehicle struct {
	VehicleId    int64
	BnsoId       int64
	GosNumber    string
	BnsoCode     string
	VehicleState sql.NullInt64
	ExecutorBnso sql.NullBool
}

type ContractVehicleList []ContractVehicle

// структура соответствующая данным из АГ2 БНСО
type BnsoPkg struct {
	Id             int64
	Client         string
	TimeStamp      time.Time
	DateCreate     time.Time
	NphRequestId   sql.NullInt64
	SpeedAvg       sql.NullFloat64
	Latitude       sql.NullFloat64
	Longitude      sql.NullFloat64
	Pdop           sql.NullInt64
	FuelSensorData []byte
	KbmSensorData  []byte
}
type BnsoPackages []BnsoPkg

//структура статусов для преобразования в хеш-таблицу

type VehicleState struct {
	StartDate time.Time
	EndDate   time.Time
}

type SensorCalibration struct {
	SensorId    int64
	MinRawValue float64
	MaxRawValue float64
	SensorType  string
}

type BillingServicePrice struct {
	Code  string
	Price float64
}

/*
Получаем цены услуг по контракту, активному на текущую дату

Возможные коды услуг:
- NAV_DATA
- BNSO_EXECUTOR
- SERVICE_MAINTENANCE
- INFORM_DRIVER
- TRANSPOTR_DATA
- KBM_SENS_DATA
- FUEL_SENS_DATA
- SUPPORT
*/
type ServicePrices map[string]float64

type Billing struct {
	Id                         int64     `db:"id"`
	CreateUid                  int64     `db:"create_uid"`
	WriteUid                   int64     `db:"write_uid"`
	CreateDate                 time.Time `db:"create_date"`
	WriteDate                  time.Time `db:"write_date"`
	ContractId                 int64     `db:"contract_id"`
	Date                       time.Time `db:"date"`
	VehicleId                  int64     `db:"vehicle_id"`
	GosNumber                  string    `db:"gos_number"`
	VehicleState               int       `db:"vehicle_state"`
	BnsoId                     int64     `db:"bnso_id"`
	BnsoCode                   string    `db:"bnso_code"`
	StartState                 string    `db:"start_state"`
	EndState                   string    `db:"end_state"`
	UsingSecs                  int       `db:"using_secs"`
	RepairSecs                 int       `db:"repair_secs"`
	RepairCount                int64     `db:"repair_count"`
	FuelSensCount              int64     `db:"fuel_sens_count"`
	KbmCount                   int64     `db:"kbm_count"`
	LossPkgCount               int64     `db:"loss_pkg_count"`
	LossPkgBlockCount          int64     `db:"loss_pkg_block_count"`
	PkgWithoutNavCount         int64     `db:"pkg_without_nav_count"`
	Delay5minPkgCount          int64     `db:"delay_5min_pkg_count"`
	Delay180minPkgCount        int64     `db:"delay_180min_pkg_count"`
	DelayDayPkgCount           int64     `db:"delay_day_pkg_count"`
	IsBnsoHaveInfoPanel        bool      `db:"driver_info_panel"`
	SupportDevice              int64     `db:"support_device"`
	SummaryPkgCount            int64     `db:"summary_pkg_count"`
	LastPkg                    int64     `db:"last_pkg"`
	FirstPkg                   int64     `db:"first_pkg"`
	VehicleSummary             int       `db:"vehicle_summary"`
	VehicleValid               int64     `db:"vehicle_valid"`
	NavDataCharging            int64     `db:"nav_data_charging"`
	NavDataPrice               float64   `db:"nav_data_price"`
	FuelSensCharging           int64     `db:"fuel_sens_charging"`
	FuelSensDataPrice          float64   `db:"fuel_sens_data_price"`
	KbmCharging                int64     `db:"kbm_charging"`
	KbmSensDataPrice           float64   `db:"kbm_sens_data_price"`
	TransferDataCharging       float64   `db:"transfer_data_charging"`
	TransferDataPrice          float64   `db:"transfer_data_price"`
	ServiceMaintenanceCharging int64     `db:"service_maintenance_charging"`
	ServiceMaintenancePrice    float64   `db:"service_maintenance_price"`
	InfoPanelCharging          int64     `db:"info_panel_charging"`
	InfoPanelPrice             float64   `db:"info_panel_price"`
	SupportCharging            int64     `db:"support_charging"`
	SupportPrice               float64   `db:"support_price"`
	ExecutorBnsoCharging       int64     `db:"executor_bnso_charging"`
	ExecutorBnsoPrice          float64   `db:"executor_bnso_price"`
	FinePrice                  float64   `db:"fine_price"`
	SummaryPrice               float64   `db:"summary_price"`
}

func (bps BnsoPackages) isEmpty() bool {
	if len(bps) > 0 {
		return false
	}

	return true
}

func (bps BnsoPackages) GetFirstPackageNumber() (BnsoPkg, error) {
	result := BnsoPkg{}
	if bps.isEmpty() {
		return result, fmt.Errorf("Package not found")
	}
	result = bps[0]

	return result, nil
}
