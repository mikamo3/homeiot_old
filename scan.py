import binascii
from bluepy.btle import Scanner, DefaultDelegate


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (adtype, desc, value) in dev.getScanData():
            print(dev.addr)
            print(adtype)
            print(value)
            print()


scanner = Scanner().withDelegate(ScanDelegate())
scanner.scan(0)
