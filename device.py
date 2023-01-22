import binascii
DEVICETYPE_METER = 0x54
DEVICETYPE_MOTION = 0x73
DEVICETYPE_CONTACT = 0x64
DEVICETYPE_CURTAIN = 0x63
DEVICETYPE_BOT = 0x48
DEVICETYPE_ENV = 0x5A


def getDevice(macaddr, rawdata):
    deviceType = int("0x"+rawdata[4:6], 16)
    if deviceType == DEVICETYPE_METER:
        return Meter(macaddr, rawdata)
    elif deviceType == DEVICETYPE_MOTION:
        return MotionSensor(macaddr, rawdata)
    elif deviceType == DEVICETYPE_CONTACT:
        return ContactSensor(macaddr, rawdata)
    elif deviceType == DEVICETYPE_CURTAIN:
        return Curtain(macaddr, rawdata)
    elif deviceType == DEVICETYPE_BOT:
        return Bot(macaddr, rawdata)
    elif deviceType == DEVICETYPE_ENV:
        return EnvSensor(macaddr, rawdata)
    else:
        return None


class Device():
    def __init__(self, macaddr, rawdata) -> None:
        self.macaddr = macaddr
        self.rawdata = rawdata

    def perse(self):
        resp = {}
        resp['sensorData'] = self.rawdata[4:]
        resp['macaddress'] = self.macaddr
        return resp


class SwitchbotDevice(Device):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])
        resp = super().perse()
        resp['deviceType'] = chr(getbit(sensorData[0], 6, 0))
        resp['battery'] = (getbit(sensorData[2], 6, 0))
        return resp


class MotionSensor(SwitchbotDevice):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])

        resp = super().perse()

        resp['scopeTested'] = bool(getbit(sensorData[1], 7))
        resp['ripState'] = getbit(sensorData[1], 6)
        resp['ledState'] = getbit(sensorData[5], 5)
        resp['iotState'] = getbit(sensorData[5], 4)
        resp['sensingDistance'] = getbit(sensorData[5], 3, 2)
        resp['lightIntensity'] = getbit(sensorData[5], 1, 0)
        resp['sinceLastTriggerRipTime'] = (sensorData[3] << 8)+sensorData[4]
        return resp


class Meter(SwitchbotDevice):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])

        resp = super().perse()

        resp['temperatureHighAlert'] = getbit(sensorData[3], 7)
        resp['temperatureLowAlert'] = getbit(sensorData[3], 6)
        resp['humidityLowAlert'] = getbit(sensorData[3], 5)
        resp['humidityLowAlert'] = getbit(sensorData[3], 4)

        positiveNegativeTemperatureFlag = getbit(sensorData[4], 7)
        temperature = getbit(sensorData[3], 3, 0) / \
            10 + getbit(sensorData[4], 6, 0)
        if not positiveNegativeTemperatureFlag:
            temperature = -temperature
        resp['temperature'] = temperature
        resp['humidity'] = getbit(sensorData[5], 6, 0)
        resp['temperratureScale'] = getbit(sensorData[5], 7)
        return resp


class ContactSensor(SwitchbotDevice):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])

        resp = super().perse()
        resp['scopeTested'] = bool((sensorData[1] & 0b10000000) >> 7)
        resp['ripState'] = (sensorData[1] & 0b01000000) >> 6
        resp['halState'] = (sensorData[3] & 0b00000110) >> 1
        resp['lightLevel'] = sensorData[3] & 0b00000001
        resp['ripUTC'] = ((sensorData[3] & 0b10000000) << 9) + \
            (sensorData[4] << 8)+sensorData[5]
        resp['halUTC'] = ((sensorData[3] & 0b01000000) << 10) + \
            (sensorData[6] << 8)+sensorData[7]
        resp['entranceCount'] = (sensorData[8] & 0b11000000) >> 6
        resp['goOutCount'] = (sensorData[8] & 0b00110000) >> 4
        resp['buttonPushCount'] = sensorData[8] & 0b00001111

        resp['scopeTested'] = bool(getbit(sensorData[1], 7))
        resp['ripState'] = getbit(sensorData[1], 6)
        resp['halState'] = getbit(sensorData[3], 2, 1)
        resp['lightLevel'] = getbit(sensorData[3], 0)
        resp['ripUTC'] = (getbit(sensorData[3], 7) << 9) + \
            (sensorData[4] << 8)+sensorData[5]
        resp['halUTC'] = (getbit(sensorData[3], 6) << 10) + \
            (sensorData[6] << 8)+sensorData[7]
        resp['entranceCount'] = getbit(sensorData[8], 7, 6)
        resp['goOutCount'] = getbit(sensorData[8], 5, 4)
        resp['buttonPushCount'] = getbit(sensorData[8], 3, 0)
        return resp


class Curtain(SwitchbotDevice):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])

        resp = super().perse()
        resp['wheterToAllowConnection'] = getbit(sensorData[1], 7)
        resp['calibrationSituation'] = getbit(sensorData[1], 6)
        resp['motionState'] = getbit(sensorData[3], 7)
        resp['position'] = getbit(sensorData[3], 6, 0)
        resp['lightLevel'] = getbit(sensorData[4], 7, 4)
        resp['deviceChain'] = getbit(sensorData[4], 3, 0)
        return resp


class Bot(SwitchbotDevice):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])

        resp = super().perse()
        resp['mode'] = getbit(sensorData[1], 7)
        resp['state'] = getbit(sensorData[1], 6)
        return resp


class EnvSensor(Device):
    def __init__(self, macaddr, rawdata) -> None:
        super().__init__(macaddr, rawdata)

    def perse(self):
        sensorData = binascii.unhexlify(self.rawdata[4:])
        resp = super().perse()
        resp['sensorData'] = self.rawdata[4:]
        resp['macaddress'] = self.macaddr
        resp['deviceType'] = chr(sensorData[0])
        resp['range'] = (sensorData[1] << 8)+sensorData[2]
        resp['tvoc'] = (sensorData[3] << 8)+sensorData[4]
        resp['co2'] = (sensorData[5] << 8)+sensorData[6]
        return resp


def getbit(char, pos_start, pos_end=-1):

    if pos_end == -1:
        pos_end = pos_start
    mask = 0
    for n in range(pos_start, pos_end-1, -1):
        mask = mask+pow(2, n)
    return ((char & mask) >> pos_end)
