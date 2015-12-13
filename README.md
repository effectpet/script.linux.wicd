# script.linux.wicd
Wicd font-end for Kodi 15.02


## Howto install Wicd
**Howto remove network-manager & install wicd (Ubuntu 14.04):**
```
Remove NetworkManager:
  sudo apt-get purge network-manager network-manager-gnome```
```
```
Install Wicd:
  sudo apt-get install wicd-curses
```

**Howto remove network-manager & install wicd (Arch Linux):**

[Thanks to jack@forum.manjaro.org](https://forum.manjaro.org/index.php?topic=3534.0)
```
Install Wicd:
  sudo pacman -Sy wicd
```
```
Stop the NetworkManager, dhcpcd and netcfg services: 
  sudo systemctl stop NetworkManager.service
  sudo systemctl stop dhcpcd.service
  sudo systemctl stop netcfg.service
```
```
Stop those services from loading at startup.
  sudo systemctl disable NetworkManager.service
  sudo systemctl disable dhcpcd.service
  sudo systemctl disable netcfg.service
```
```
Start the Wicd service.
  sudo systemctl start wicd.service
```
```
Start the Wicd service on boot.
  sudo systemctl enable wicd.service
```
