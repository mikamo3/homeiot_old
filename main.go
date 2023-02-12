package main

import (
	"context"
	"encoding/json"
	"fmt"
	"homeiot/lib"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/go-ble/ble"
	"github.com/go-ble/ble/linux"
)

func main() {
	//prepare signalch
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
	ctx, cancel := context.WithCancel(context.Background())
	//prepare devicech
	sensorCh := make(chan lib.Sensor)
	go func() {
		<-sigCh
		fmt.Println("signal received.")
		cancel()
	}()

	//prepare blescan
	d, err := linux.NewDevice()
	if err != nil {
		log.Fatalln(err)
	}
	// start udp client
	conn, err := net.Dial("udp4", "127.0.0.1:1111")
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()
	go func(ch <-chan lib.Sensor) {
		for {
			sensor := <-ch
			go sendUDP(conn, sensor)
		}
	}(sensorCh)

	ble.SetDefaultDevice(d)
	go ble.Scan(ctx, true, lib.MakeAdvHandler(sensorCh), lib.FilterScan())
	<-ctx.Done()
}

func sendUDP(conn net.Conn, sensor lib.Sensor) {
	if jsondata, err := json.Marshal(sensor); err != nil {
		log.Fatalln(err)
	} else {
		conn.Write(jsondata)
	}
}
