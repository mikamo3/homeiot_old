import device
from bluepy.btle import Scanner, DefaultDelegate
import socket
import json
import db


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        try:
            for (adtype, desc, value) in dev.getScanData():

                if (adtype == 22):
                    sensor = device.getDevice(dev.addr, value)
                    if sensor != None:
                        data = sensor.perse()
                        db.insert(data)
                        s.sendto(json.dumps(data).encode(),
                                 ("127.0.0.1", 1111))
        except:
            print("error: {}".format(dev))


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
db = db.Db()
scanner = Scanner().withDelegate(ScanDelegate())
scanner.scan(0)
