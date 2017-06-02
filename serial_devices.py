import os
import time
import numpy as np
import pandas as pd
import hashlib
import random
import uuid
serial_ports = [ "COM%i" % i for i in range(1,10)] 
import threading
import copy

# Lock to save publish data
lock = threading.Lock()

current_data = []


class LedDisplay:
  def __repr__(self):
    return "Led"
class PressureSensor:
  def __repr__(self):
    return "Pressure"
class TempSensor:
  def __repr__(self):
    return "Temp"
class Gyro:
  def __repr__(self):
    return "Gyro"

def get_capabilities():
  possible_capabilities = [Gyro(), LedDisplay(), PressureSensor(), TempSensor()] 
  return random.sample(set(possible_capabilities), random.randint(0, len(possible_capabilities)-1))


def new_serial_device(port):
  id_length = 8
  device_ttl = random.choice([5,10,15]) 
  return {
    'id'            : uuid.uuid4().hex[:id_length+1],
    'port'          : port,
    'ttl'           : device_ttl,
    'max_ttl'       : device_ttl,
    'alive'         : True, # Use to simulate devices disconnecting
    'capabilities'  : get_capabilities()
  }

def get_device_data():
  with lock:
    return copy.deepcopy(current_data)

serial_devices = []

# Generate random ports that has connected devices from the beginning 
for port_number in random.sample(set([1, 2, 3, 4, 5, 6, 7, 8, 9]), 3):
  serial_devices.append(new_serial_device('COM%i' % port_number))

def run_simulation():
  global current_data

  while(1):
    os.system('cls')  # on windows
    
    table = {}
    table['id'] =   [ device['id'] for device in serial_devices]
    table['port'] = [ device['port'] for device in serial_devices]
    table['ttl'] = [ device['ttl'] for device in serial_devices]
    table['alive'] = [ device['alive'] for device in serial_devices]
    table['capabilities'] = [ ",".join("%15s" % cap for cap in map(str,device['capabilities'])) for device in serial_devices]
    print("")
    df = pd.DataFrame(table)

    with lock:
      current_data = df.to_dict(orient='records')

    used_ports = set(df['port'])
    not_used_ports = set(serial_ports) - used_ports
    
    # Add empty rows for not used ports
    df_empty = pd.DataFrame([ ['-',port,'','',''] for port in not_used_ports ], columns=['id','port','ttl','alive','capabilities'])
    df = df.append(df_empty,ignore_index=True)      
    df = df.sort_values(by=["port"], ascending=[True])
    pd.set_option('display.width', 1000)
    print(df[['port','id','ttl','alive','capabilities']])
    print("")


    # Update data
    #serial_devices['temperature'] += np.array(np.random.randn(len(serial_ports)))

    # Handle all devices
    for index in range(len(serial_devices)-1,0-1,-1):
      # Decrease time-to-live counter
      serial_devices[index]['ttl'] -= 1

      # Remove device if time-to-live counter has reached zero
      if serial_devices[index]['ttl'] == 0:
        print('device "%s" has disconnected too long has been removed.' % serial_devices[index]['id'])
        serial_devices.pop(index)
        continue

      # Do nothing more if device has been disconnected
      if not serial_devices[index]['alive']:
        continue

      # Chance that device disconnects 
      if random.random() < 0.15:
        serial_devices[index]['alive'] = False
        print('device "%s" disconnected.' % serial_devices[index]['id'])

      # Refresh TTL 
      serial_devices[index]['ttl'] = serial_devices[index]['max_ttl']


    for port in not_used_ports:

      # Chance that device disconnects 
      if random.random() < 0.05:
        new_device = new_serial_device(port)
        serial_devices.append(new_device)
        print('device "%s" connected on port "%s".' % (new_device['id'], new_device['port']))


    # Create new device
    time.sleep(1)

if __name__ == '__main__':
  run_simulation()