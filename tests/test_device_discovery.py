import pytest
import devices
from devices import ConnectionType

def test_test():
  print('yay')

# 
def test_get_devices():  
  
  assert len(devices.get_devices()) == 0
  
  devices.add_device('sensor1', ConnectionType.UDP) 
  devices.add_device('sensor2', ConnectionType.UDP) 
  devices.add_device('sensor3', ConnectionType.SERIAL) 
  assert len(devices.get_devices()) == 3
  assert len(devices.get_udp_devices()) == 2
  print(devices.get_serial_devices())
  assert len(devices.get_serial_devices()) == 1

