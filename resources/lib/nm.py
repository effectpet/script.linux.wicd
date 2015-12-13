#!/usr/bin/python
import os
import sys
import dbus
import dbus.service
import socket

from wicd import misc

if getattr(dbus, 'version', (0, 0, 0)) < (0, 80, 0):
  import dbus.glib
else:
  from dbus.mainloop.glib import DBusGMainLoop
  DBusGMainLoop(set_as_default=True)

def init():
  bus = dbus.SystemBus()
  misc.RenameProcess('nm')

  try:
    daemon = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon'), 'org.wicd.daemon')
    wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'), 'org.wicd.daemon.wireless')
    wired = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired'), 'org.wicd.daemon.wired')
    config = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/config'), 'org.wicd.daemon.config')
    return daemon, wireless, wired, config
  except dbus.DBusException:
    print 'Error: Could not connect to the daemon. Please make sure it is running.'
    print '(sudo /etc/init.d/wicd start)'
    sys.exit(3)

def is_valid_wireless_network_id(network_id):
  if not (network_id >= 0 and network_id < wireless.GetNumberOfNetworks()):
    print 'Invalid wireless network identifier.'
    return False
  else:
    return True

def is_valid_wired_network_id(network_id):
  num = len(wired.GetWiredProfileList())
  if not (network_id < num and network_id >= 0):
    print 'Invalid wired network identifier.'
    return False
  else:
    return True

def is_valid_wired_network_profile(profile_name):
  if not profile_name in wired.GetWiredProfileList():
    print 'Profile of that name does not exist.'
    return False
  else:
    return True

def scan_wireless():
  wireless.Scan(True)

def get_current_wireless():
  network_id = wireless.GetCurrentNetworkID(0)
  if is_valid_wireless_network_id(network_id) == True:
    print "ID: %s" % network_id
    print "IP: %s" % wireless.GetWirelessIP(0)
    return network_id
  else:
    print "Not connected"
    return -1

def set_wireless_property(network_id, aProperty,set_to):
  aProperty = aProperty.lower()
  if is_valid_wireless_network_id(network_id) == False:
    print "Not a valid network_id"
    return
  wireless.SetWirelessProperty(network_id, aProperty, set_to)

def disconnect_wireless():
  daemon.Disconnect()
  if wireless.GetCurrentNetworkID(0) > -1:
    print "Disconnecting from %s on %s" % (wireless.GetCurrentNetwork(0), wireless.DetectWirelessInterface())

def save_wireless(network_id):
  if not network_id >= 0:
    return False
  print "Saving:" + str(network_id)
  wireless.SaveWirelessNetworkProfile(network_id)
  return True

def remove_wireless(network_id):
  if not network_id >= 0:
    return False
  print "Removing:" + str(network_id)
  wireless.RemoveGlobalEssidEntry(network_id)
  return True

def save_current_wireless():
  save_wireless(get_current_wireless())

##############################################
#Support functions
##############################################

def check_net():
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("www.google.com", 80))
    return True

  except socket.error:
    return False

def str_properties(prop):
  if len(prop) == 0:
    return "None"
  else:
    return ', '.join("%s (%s)" % (x[0], x[1].replace("_", " ")) for x in prop)


def get_ssid2id_dict():
  ssid2id_dict = {}
  for network_id in range(0, wireless.GetNumberOfNetworks()):
    ssid2id_dict[wireless.GetWirelessProperty(network_id, 'essid')] = network_id
  return ssid2id_dict


def translate_encryption_method(method):
  if method == None:
    return
  elif method.lower()[0:3] == "wpa":
    return 'wpa'
  elif method.lower()[0:3] == "wep":
    return 'wep'	
  else:
    return 'not_supported'

###############################################################
#Compounded functions
###############################################################

def connect_wireless(network_id,key):
  if is_valid_wireless_network_id(network_id) == False:
    print "Not a valid network_id"
    return

  name = wireless.GetWirelessProperty(network_id, 'essid')
  new_enctype = translate_encryption_method(wireless.GetWirelessProperty(network_id, 'encryption_method'))
  wireless.SetWirelessProperty(network_id, 'enctype', new_enctype)
  wireless.SetWirelessProperty(network_id, 'key', key)

  wireless.SetWirelessProperty(network_id, 'automatic', 1)
  wireless.SetWirelessProperty(network_id, 'use_settings_globally', True)

  enctype = wireless.GetWirelessProperty(network_id, 'enctype')

  print "Connecting to %s with %s on %s" % (name, enctype, wireless.DetectWirelessInterface())
  wireless.ConnectWireless(network_id)

  check = lambda: wireless.CheckIfWirelessConnecting()
  message = lambda: wireless.CheckWirelessConnectingMessage()

  last = None
  while check():
    next = message()
    if next != last:
      print next.encode('utf-8').replace("_", " ")
      if next == "done":
        break
      last = next
  print "done!"
  return (wireless.GetCurrentSignalStrength("") != 0 and wireless.GetCurrentNetworkID(wireless.GetIwconfig())==network_id and wireless.GetWirelessIP('') != None)

def remove_auto(network_id):
  if is_valid_wireless_network_id(network_id) == False:
      print "Not a valid network_id"
      return

  wireless.SetWirelessProperty(network_id, 'automatic', 0)
  print "automatic set = 0"
  wireless.SaveWirelessNetworkProfile(network_id)

  print "saved"

def connect_wireless_ssid(ssid, key):
  ssid2id_dict = get_ssid2id_dict()
  try:
    network_id = ssid2id_dict[ssid]
  except:
    print "SSID:", ssid, " does not exist"
    return

  connect_wireless(network_id, key)


def get_wireless_networks():
  wlessL = []
  if daemon.GetSignalDisplayType() == 0:
      strenstr = 'quality'
  else:
      strenstr = 'strength'
  for network_id in range(0, wireless.GetNumberOfNetworks()):
      net_dict = {}
      net_dict['network_id'] = network_id 

      connected = wireless.GetCurrentSignalStrength("") != 0 and wireless.GetCurrentNetworkID(wireless.GetIwconfig())==network_id and wireless.GetWirelessIP('') != None
      net_dict['connected'] = connected
      net_dict['bssid'] = wireless.GetWirelessProperty(network_id , 'bssid')
      net_dict['essid'] = wireless.GetWirelessProperty(network_id , 'essid')
      net_dict['signal'] = daemon.FormatSignalForPrinting(str(wireless.GetWirelessProperty(network_id , strenstr)))
      net_dict['automatic'] = wireless.GetWirelessProperty(network_id , 'automatic')

      if wireless.GetWirelessProperty(network_id , 'encryption'):
          net_dict['encrypt']= wireless.GetWirelessProperty(network_id ,'encryption_method')
      else:
          net_dict['encrypt']= 'None'

      net_dict['mode']= wireless.GetWirelessProperty(network_id , 'mode') # Master, Ad-Hoc
      net_dict['channel'] = wireless.GetWirelessProperty(network_id , 'channel')

      wlessL.append(net_dict)

  return (wlessL)

daemon, wireless, wired, config = init()