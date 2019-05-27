main dirs:
- `/display` code for transmitter.
- `/py_dev` code for receiver.
- `/ImageProcessing` code for generating encoding layers.


## Overview

- `/display` reads the data from mouse and controls the display content according to signal from `/py_dev`.
- `/py_dev` handles the data and calculates the position/angle of mouse, then send the according signal to `/display`.
- Not only the mouse data but also the control signal is shared by named pipe.

## /display

## /py_dev

- `hci` main file of receiver called by `/display`. Unpacks the packets and sends data to `angle`/`location`
- `angle` module to detect the angle of mouse.
- `location` module to decode the VLP packet.
- `comm_handler`/`setting`/`utils` helper class/funciton


## /ImageProcessing

- `location_display` generate encoding layers with 1024 locations ID encoded
- `space_complement` generate encoding layers with 1 location
