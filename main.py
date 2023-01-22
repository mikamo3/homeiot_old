import device
from bluepy.btle import Scanner, DefaultDelegate
import socket
import json
import db
import logging
from logging import handlers
import traceback


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (adtype, desc, value) in dev.getScanData():
            try:

                if (adtype == 22):
                    sensor = device.getDevice(dev.addr, value)
                    if sensor != None:
                        data = sensor.perse()
                        db.insert(data)
                        s.sendto(json.dumps(data).encode(),
                                 ("127.0.0.1", 1111))

            except Exception as e:
                my_logger.error("{}".format(e))
                my_logger.error(traceback.format_exc())


my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
my_logger.addHandler(handler)

my_logger.debug("start")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
db = db.Db()
scanner = Scanner().withDelegate(ScanDelegate())
scanner.scan(0)
