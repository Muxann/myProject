package rest

import (
	"fmt"
	"github.com/go-gorp/gorp"
	"github.com/labstack/echo"
	"net/http"
	"psd-billing2/database"
	"psd-billing2/services"
	"strconv"
	"time"
)

type Handler struct {
	DB *gorp.DbMap
}

func (h *Handler) BillingCalculationHandler(c echo.Context) error {
	billingDate := c.QueryParam("date")
	date, err := time.Parse("2006-01-02", billingDate)
	if err != nil {
		return fmt.Errorf("Can't parse billing date: %v\n", err)
	}

	if err := database.RemoveOldBillingData(h.DB, billingDate); err != nil {
		return fmt.Errorf("Can't clear old billing data: %v\n", err)
	}
	c.Logger().Info("Remove old billing data success")

	contractId, err := database.GetActualContract(h.DB, billingDate)
	if err != nil {
		return fmt.Errorf("Error getting actual contract: %v\n", err)
	}
	contractVehicles, err := database.GetActualContractVehicles(h.DB, contractId, billingDate)
	if err != nil {
		return fmt.Errorf("Error getting vehicles of actual contract: %v\n", err)
	}
	summaryVehicleCount := len(contractVehicles)
	c.Logger().Info("Success getting contract vehicle. Count: ", summaryVehicleCount)

	// для каждой машины считаем услуги
	servicePrice, err := database.GetPriceBillingService(h.DB, billingDate)
	if err != nil {
		return fmt.Errorf("Can't get service price: %v\n", err)
	}

	VehicleProcessingSuccessCount := 0
	for _, curContractVehicle := range contractVehicles {

		if err := services.CalculationBilling(h, curContractVehicle, servicePrice, contractId, billingDate, date, summaryVehicleCount); err != nil {
			c.Logger().Warnf("Billing for bnso %s with vehicle id %d error: %v", curContractVehicle.BnsoCode, curContractVehicle.VehicleId, err)
			//return err
		}

		VehicleProcessingSuccessCount += 1
		c.Logger().Infof("Processing %d from %d", VehicleProcessingSuccessCount, summaryVehicleCount)
	}

	return c.String(http.StatusOK, "Billing calculation success")
}

func (h *Handler) BnsoBillingCalculationHandler(c echo.Context) error {
	billingDate := c.QueryParam("date")
	date, err := time.Parse("2006-01-02", billingDate)
	if err != nil {
		return fmt.Errorf("Can't parse billing date: %v\n", err)
	}

	bnsoId, err := strconv.Atoi(c.Param("bnso_id"))
	if err != nil {
		return fmt.Errorf("Can't parse bnso id: %v\n", err)
	}

	contractId, err := database.GetActualContract(h.DB, billingDate)
	if err != nil {
		return fmt.Errorf("Error getting actual contract: %v\n", err)
	}

	fmt.Println(date, bnsoId, contractId)

	return c.String(http.StatusOK, "Billing calculation success")
}
