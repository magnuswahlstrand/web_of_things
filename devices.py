import sys
import glob
import serial

from enum import Enum
class ConnectionType(Enum):
     UDP = 1
     TCP = 2
     SERIAL = 3

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

found_devices = []

def add_device(id, type):
  global found_devices
  found_devices.append({'id':id, 'type': type})


def get_devices():
  return found_devices

def get_udp_devices():
  return [device for device in found_devices if device['type'] is ConnectionType.UDP]

def get_serial_devices():
  return [device for device in found_devices if device['type'] is ConnectionType.SERIAL]

if __name__ == '__main__':
    #print(serial_ports())
    pass