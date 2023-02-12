package lib

import (
	"github.com/go-ble/ble"
)

func MakeAdvHandler(ch chan Sensor) func(ble.Advertisement) {
	return func(a ble.Advertisement) {
		if len(a.ServiceData()) > 0 {
			for _, v := range a.ServiceData() {
				if sensor := GetDevice(a.Addr().String(), v); sensor != nil {
					ch <- sensor
				}
			}
		}
	}
}
func FilterScan() ble.AdvFilter {
	return func(a ble.Advertisement) bool {
		return len(a.ServiceData()) > 0
	}
}
