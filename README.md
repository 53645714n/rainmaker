# rainmaker
Remote control and timer for springkler system.
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

### Schematics
![schematics, also available in gpio configuration](https://github.com/53645714n/rainmaker/Rainmaker.png "Schematics")

## Software
I'm assuming you have git and python/pip installed, if not do this first.

After:
```
git clone https://github.com/53645714n/rainmaker.git
```

### Dependencies
On raspbian, everything is there. On other systems:
```
pip install -r rainmaker/requirements.txt
```

### Setup
If you wired everything exactly like I did, run the program.
```
python3 rainmaker/rainmaker.py & #this will start the script
tail -f rainmaker.log #this will show you what it's doing.
```

If you wired something differently, open the file and edit the GPIO section.
```
nano rainmaker/rainmaker.py
```

### Auto start
```
sudo nano /home/pi/.bashrc
```
add to the end of the file
```
echo Running at boot 
python3 /home/pi/rainmaker/rainmaker.py &
```

## Manual
The program will start at boot and log any events to rainmaker.log in the home folder.

### Buttons
The green and A buttons turn on the pump indefinately
The red and B buttons turn off the pump and interrupt any timer set
The C and D buttons set a timer for a set time (standard 30 and 60 minutes)

### LED's
| Green | Red | *Function* |
| --- | --- | --- |
| On | Off | Pump is off |
| Off | On | Error occured, view logging |
| Blinking | On | Pump is on indefinately |
| Blinking | Blinking | Pump is on on timer |
