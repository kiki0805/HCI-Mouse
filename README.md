# MouseTouch

## Main Dirs

- `/display` reads the data from mouse and controls the display content according to signal from `/py_dev`.
- `/py_dev` handles the data and calculates the position/angle of mouse, then send the according signal to `/display`.
- Not only the mouse data but also the control signal is shared by named pipe.

## /py_dev

- `hci` main file of receiver called by `/display`. Unpacks the packets and sends data to `angle`/`location`
- `angle` module to detect the angle of mouse.
- `location` module to decode the VLP packet.
- `comm_handler`/`setting`/`utils` helper class/funciton

## /image_processing

- `location_display` generate encoding layers with 1024 locations ID encoded
- `space_complement` generate encoding layers with 1 location

## /lab_code

- Feed csv files from `test_SimpleBG.exe` to `dynamic_bg_lab_11222019.ipynb`
- `dynamic_bg_lab_11222019.ipynb` generates input of `bg_test_analyzer.m`
