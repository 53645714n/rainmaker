# rainmaker
Remote control and timer for sprinkler system.
The pumpcontroller for the sprinkler system is a DAB ESC 4 T, which has a s/w connection for turning on and off the pump which I will be switching with a relais connected to a Raspberry Pi.

## The concept
### Remote
Because it is hard to find the correct spot for the sprinkler at once, the farmer spends a lot of time walking back and forth between the sprinkler and the pump controller. Being able to switch the pump remotely can save lots of time and miles.

### Timer
Waiting for the moment to switch off the pump isn't exactly time well spent, with this program the farmer is able to set a timer to two pre-defined times remotely and go home.

## Hardware
- 4 channel 433Mhz RF remote with receiver
- Raspberry Pi B+ (yeah, the oldie)
- 5V relais 1-channel high-active
- Green and red buttons with switchable LED
- 2 x 16 LCD with I2C backpack
- KEYES040 rotary encoder

### Schematics
![schematics, also available in gpio configuration](https://raw.githubusercontent.com/53645714n/rainmaker/master/Rainmaker.png "Schematics")

## Raspberry Pi
### Enable I2C
For the I2C backpackfor the lcd screen we need to enable I2C. Type:
```
sudo raspi-config
```

In the menu, select '5 Interfacing options' and then 'P5 I2C'. Choose Yes when asked: 'Would you like the ARM I2C interface to be enabled?'

### Setup HW-clock
Follow this guide: https://trick77.com/adding-ds3231-real-time-clock-raspberry-pi-3/
Use sudo a bit more often (everywhere) and reboot between step #3 and #4.

### Software
Install python and git if you haven't already and then clone the repository and install the dependencies.
```
sudo apt-get update
sudo apt-get upgrade
sudo apt install python3-pip
sudo apt-get install git
git clone https://github.com/53645714n/rainmaker.git
pip install -r rainmaker/requirements.txt
```

### Setup
If you wired everything exactly like I did, skip this and go to run the program.
```
nano rainmaker/rainmaker.py
```

### Run the program
```
python3 rainmaker/rainmaker.py #this will start the script
tail -f rainmaker.log #this will show you what it's doing.
```
Type 'kill -9 [PROCESS]'  to kill the script where [PROCESS] is the number returned after the python3 command.

### Auto start
Move the systemd service file I created to the systemd folder and change it's permissions by doing the following.
```
sudo mv rainmaker/rainmaker.service /lib/systemd/system/rainmaker.service
sudo chmod 644 /lib/systemd/system/rainmaker.service
```
After this, reload the daemon and enable the service
```
sudo systemctl daemon-reload
sudo systemctl enable rainmaker.service
```
Reboot and check the service:
```
sudo systemctl status rainmaker.service
```

## Manual
The program will start at boot and log any events to rainmaker.log in the home folder.

### Buttons
The green and A buttons turn on the pump indefinately
The red and B buttons turn off the pump and interrupt any timer set
The C and D buttons set a timer for a set time (standard 60 and 120 minutes)
Pushing the rotary encoder opens the timer menu, the first time you enter is the start time, the second time (after pushing again) is the end-time. Pushing a third time starts the timer. Witht the red button you can exit the menu any time and interrupt the timer.

### LED's
| Green | Red | *Function* |
| --- | --- | --- |
| On | Off | Pump is off |
| Off | On | Error occured, view logging |
| Blinking | On | Pump is on indefinately |
| Blinking | Blinking | The timer is enabled |
| Off | Blinking 0.2 seconds | In timer menu, push to exit | 
