# rainmaker
Remote control and timer for springkler system.
The pump for the sprinkler system is a DAB ESC 4 T, which has a s/w connection for turning on and off the pump which I will be switching with a relais connected to a Raspberry Pi.

## Components
- 4 channel 433Mhz RF remote with receiver
- Raspberry Pi B+ (yeah, the oldie)
- 5V relais 1-channel high-active
- Green and red buttons with switchable LED

## The concept
### Remote
Because it is hard to find the correct spot for the sprinkler at once, the farmer spends a lot of time walking back and forth between the sprinkler and the pump controller. Being able to switch the pump remotely can save lots of time and miles.

### Timer
Waiting for the moment to switch off the pump isn't exactly time well spent, with this program the farmer is able to set a timer to two pre-defined times remotely and go home.

## Wish list
