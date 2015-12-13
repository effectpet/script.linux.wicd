import sys
import xbmc
import xbmcaddon
import xbmcgui
import threading

nm = None
lblTimer = 0
getLS   = sys.modules[ "__main__" ].__language__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__addon__ = sys.modules[ "__main__" ].__addon__

class GUI(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.doModal()

    def check_wicd(self):
        try:
            import dbus
        except:
            err = 300
            return False, err
        try:
            bus = dbus.SystemBus()
        except:
            err = 301
            return False, err
        try:
            daemon = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon'), 'org.wicd.daemon')
            wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'), 'org.wicd.daemon.wireless')
        except:
            err = 302
            return False, err

        return True, ''

    def onInit(self):
        self.defineControls()

        wicd_OK, err = self.check_wicd()
        if wicd_OK == True:
            global nm
            import nm
            self.updateList()
        else:
            xbmc.executebuiltin('Notification('+getLS(105)+','+getLS(err)+',5000)')
            self.closeDialog()

        
    def defineControls(self):
        self.control_heading_label_id = 2
        self.control_list_label_id = 3
        self.control_list_id = 10
        self.control_refresh_button_id = 18
        self.control_ok_button_id = 19
        self.control_disconnect_button_id = 20
        self.control_status_label_id = 100
        self.heading_label = self.getControl(self.control_heading_label_id)
        self.list_label = self.getControl(self.control_list_label_id)
        self.list = self.getControl(self.control_list_id)
        self.refresh_button = self.getControl(self.control_refresh_button_id)
        self.ok_button = self.getControl(self.control_ok_button_id)
        self.disconnect_button = self.getControl(self.control_disconnect_button_id)
        self.status_label = self.getControl(self.control_status_label_id)

    def closeDialog(self):
        self.close()

    def onClick(self, controlId):
        # List - Item click
        if controlId == self.control_list_id:
            position = self.list.getSelectedPosition()
            if self.connect_wireless(position) == True:
                self.updateList()
        # Button - scan
        elif controlId == self.control_refresh_button_id:
            self.updateList()
        # Button - Ok
        elif controlId == self.control_ok_button_id:
            self.closeDialog()
        # Button - Disconnect
        elif controlId == self.control_disconnect_button_id:
            self.setFixLabel(getLS(205))
            self.controlsSetEnabled(False)
            nm.disconnect_wireless()
            self.controlsSetEnabled(True)
            self.updateList()
#####################################################################################################   
    def updateList(self):
        self.setFixLabel(getLS(203))
        self.controlsSetEnabled(False)

        hasConnection = False

        self.list.reset()
        nm.scan_wireless()
        connection_list = nm.get_wireless_networks()
    
        for connection_dict in connection_list:
            if connection_dict['connected'] == True:
                state = getLS(208)
                hasConnection = True
            elif connection_dict['automatic'] == 1:
                state = ""
            else:
                state = ""
        
            item = xbmcgui.ListItem(label=connection_dict['essid'])
            item.setProperty('state',state)
            item.setProperty('signal',str(connection_dict['signal']))
            item.setProperty('ssid',connection_dict['essid'])
            item.setProperty('encryption',connection_dict['encrypt'])
            self.list.addItem(item)

        if not connection_list:
            self.setFixLabel(getLS(209))
        else:
            self.setFixLabel('')

        self.disconnect_button.setVisible(hasConnection)
        self.controlsSetEnabled(True)
#####################################################################################################
    def connect_wireless(self, network_id):
        isConnected = False
        self.controlsSetEnabled(False)
        self.setFixLabel(getLS(206))

        key = nm.wireless.GetWirelessProperty(network_id, 'key')
        if key != "":
            isConnected = nm.connect_wireless(network_id, key)
            if isConnected == False:
                nm.remove_wireless(network_id)

        if isConnected == False:
            key = ""
            kb = xbmc.Keyboard("", getLS(201), False)
            kb.doModal()
            if (kb.isConfirmed()):
                key = kb.getText()

            if  key == "":
                self.setLabel(getLS(202))
                return False
            else:
                isConnected = nm.connect_wireless(network_id, key)

        if isConnected == True:
            self.setLabel(getLS(204))
        else:
            self.setLabel(getLS(207))
        self.controlsSetEnabled(True)
        return isConnected
#####################################################################################################
    def controlsSetEnabled(self, val):
        self.list.setEnabled(val)
        self.refresh_button.setEnabled(val)
        self.ok_button.setEnabled(val)
        self.disconnect_button.setEnabled(val)
#####################################################################################################
    def labelThread(self):
        global lblTimer
        if lblTimer > 0:
            lblTimer = lblTimer - 1
            threading.Timer(1, self.labelThread).start()
        elif lblTimer == 0:
            self.status_label.setLabel('')

    def setLabel(self, text):
        self.status_label.setLabel(text)
        global lblTimer
        if lblTimer <= 0:
            lblTimer = 5
            threading.Timer(1, self.labelThread).start()
        else:
            lblTimer = 5

    def setFixLabel(self, text):
        global lblTimer
        lblTimer = -1
        self.status_label.setLabel(text)
#####################################################################################################