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

STARTING_DEVICES = 3
BIRTH_RATE = 0.0
DEATH_RATE = 0.0

# Lock to save publish data
lock = threading.Lock()

current_data = []
not_used_ports = []

def print_capability(capability):


  if capability['type'] == 'gyro':
    return "Gyro(%.3f)" % capability['value']

  elif capability['type'] == 'temp':
    return "Temp(%i)" % capability['value']

  elif capability['type'] == 'led':
    return "Temp(%s)" % capability['value']

  elif capability['type'] == 'pressure':
    return "Pressure(%s)" % capability['value']

  else:
    return ""

def update_capability(capability):

  if capability['type'] == 'gyro':
    capability['value'] += 0.1*random.random()

  elif capability['type'] == 'temp':
    capability['value'] += random.randint(-1,1)

  elif capability['type'] == 'led':
    pass

  elif capability['type'] == 'pressure':
    pass

  else:
    pass    



def get_capabilities(type):
  possible_capabilities = [
                              {'type': 'gyro',        'value': random.random()},
                              {'type': 'led',         'value': 'Hi!'},
                              {'type': 'pressure',    'value': random.randint(10,90)},
                              {'type': 'temp',        'value': random.randint(45,75)}

                          ]

  if type == None:
      selected_indicies = random.sample(range(len(possible_capabilities)), random.randint(1, len(possible_capabilities)-1))

      return [possible_capabilities[s] for s in selected_indicies]
  else:
    return [cap for cap in possible_capabilities if cap['type'] == type]


def new_serial_device(port, type=None):
  id_length = 8
  print(port, type)
  capabilities = get_capabilities(type)

  device_ttl = random.choice([5,10,15]) 
  return {
    'id'            : uuid.uuid4().hex[:id_length+1],
    'port'          : port,
    'ttl'           : device_ttl,
    'max_ttl'       : device_ttl,
    'alive'         : True, # Use to simulate devices disconnecting
    'capabilities'  : capabilities
  }

def add_device(type):
  with lock:
    new_port = random.choice(list(not_used_ports))
    serial_devices.append(new_serial_device(new_port, type))

def get_device_data():
  with lock:
    return copy.deepcopy(current_data)

serial_devices = []

# Generate random ports that has connected devices from the beginning 
for port_number in random.sample(set([1, 2, 3, 4, 5, 6, 7, 8, 9]), STARTING_DEVICES):
  serial_devices.append(new_serial_device('COM%i' % port_number))

def get_capabilities_from_device(device):
  
  capabilities = []
  for capability in device['capabilities']:
    cap = copy.copy(device)
    cap['capability'] = capability
    capabilities.append(cap)
    
  return capabilities


def send_signal():
  pass
  # Serial send 

def run_simulation():
  global current_data
  global not_used_ports

  while(1):
    os.system('cls')  # on windows

    capabilities = []
    list(map(capabilities.extend, [ get_capabilities_from_device(device) for device in serial_devices]))

    table = {}
    table['id'] = [ cap['id'] + cap['capability']['type'][:4] for cap in capabilities]
    table['port'] = [ cap['port'] for cap in capabilities]
    table['ttl'] = [ cap['ttl'] for cap in capabilities]
    table['alive'] = [ cap['alive'] for cap in capabilities]
    table['capability'] = [ cap['capability'] for cap in capabilities]



    #table['capabilities'] = [ ",".join("%15s" % cap for cap in map(str,device['capabilities'])) for cap in capabilities]

    print("")
    df = pd.DataFrame(table)

    with lock:
      current_data = df.to_dict(orient='records')
     # print(current_data)nt


    used_ports = set(df['port'])
    not_used_ports = set(serial_ports) - used_ports
    
    # Add empty rows for not used ports
    df_empty = pd.DataFrame([ ['-',port,'','',{'type':''}] for port in not_used_ports ], columns=['id','port','ttl','alive','capability'])
    df = df.append(df_empty,ignore_index=True)      
    df = df.sort_values(by=["port"], ascending=[True])
    pd.set_option('display.width', 1000)

    df['capability'] = [print_capability(cap) for cap in df['capability']]


#    df['capability'] = 1
    print(df[['port','id','ttl','alive','capability']])
    print("")

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

      # Update status of capability
      for cap in serial_devices[index]['capabilities']:
          update_capability(cap)

      # Chance that device disconnects 
      if random.random() < DEATH_RATE:
        serial_devices[index]['alive'] = False
        print('device "%s" disconnected.' % serial_devices[index]['id'])

      # Refresh TTL 
      serial_devices[index]['ttl'] = serial_devices[index]['max_ttl']


    for port in not_used_ports:

      # Chance that device onnects 
      if random.random() < BIRTH_RATE:
        new_device = new_serial_device(port)
        serial_devices.append(new_device)
        print('device "%s" connected on port "%s".' % (new_device['id'], new_device['port']))


    # Create new device
    time.sleep(1)

if __name__ == '__main__':
  run_simulation()