import influxdb
import datetime

DEVICETYPE_METER = 0x54
DEVICETYPE_MOTION = 0x73
DEVICETYPE_CONTACT = 0x64
DEVICETYPE_CURTAIN = 0x63
DEVICETYPE_BOT = 0x48


def getMeasurementName(deviceType):
    if deviceType == 'd':
        return 'contact'
    elif deviceType == 's':
        return 'motion'
    elif deviceType == 'c':
        return 'curtain'
    elif deviceType == 'H':
        return 'bot'
    elif deviceType == 'T':
        return 'meter'
    elif deviceType == 'Z':
        return 'env'
    else:
        return None


class Db():
    def __init__(self) -> None:
        self.db = influxdb.InfluxDBClient(
            host='127.0.0.1',
            port=8086,
            database='homeiot'
        )

    def insert(self, data):
        name = getMeasurementName(data['deviceType'])
        if name == None:
            return
        points = [{
            'measurement': name,
            'tags': {
                'macaddr': data['macaddress']
            },
            'time': datetime.datetime.utcnow(),
            'fields': data
        }]
        self.db.write_points(points)
