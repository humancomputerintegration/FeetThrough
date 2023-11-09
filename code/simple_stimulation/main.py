import electro_stimulator as es
import time
from pynput.keyboard import Listener, Key
import logging
import itertools
import numpy as np


is_stimulating = False
is_calibration = False
channel = 1
N = 60

# """ electrode order
# ---------------
# 5   4  3  2  1 |
# ---------------
# 10  9  8  7  6 |
# ---------------
# 15 14 13 12 11 |
# ---------------
# 20 19 18 17 16 |
# ---------------
# 25 24 23 22 21 |
# ---------------
# ...
# ---------------
# 60 59 58 57 56 |
# ---------------
# """

# examples
circle_ch = [2, 3, 9, 14, 18, 17, 11, 6] # an example
right_arrow_ch = [4, 3, 7, 6, 11, 12, 18, 19] # an example
all_ch = [i+1 for i in range(N)]

# press 'n' to change the shape
shape_cycle = itertools.cycle([all_ch, circle_ch, right_arrow_ch])
shape_names = ["all", "circle", "right_arrow"]

channel_list = next(shape_cycle)
index_cycle = itertools.cycle(channel_list)
focusing_channel_index = 0


global_intensity = 0

intensities = np.full(N, 0)

ROW_ELECTRODES = 5
COLUMN_ELECTRODES = 12


def keypress_callback(key) :
    global is_stimulating, channel, index_cycle, is_calibration
    global intensities, channel_list, focusing_channel_index, global_intensity
    if (hasattr(key, "char")) :
        c = key.char
        # turning stimulation on/off
        if (c == 's') :
            print("flip is_stimulating")
            is_stimulating = not is_stimulating
            print(f"is_stimulation: {is_stimulating}")

        
        elif (c == 'n') :
            print("next shape")
            channel_list = next(shape_cycle)
            print(channel_list)
            index_cycle = itertools.cycle(channel_list)
            # intensities = np.full(N, 0)
            channel = next(index_cycle)

        # turning stimulation on/off
        elif (c == 'c') :
            is_calibration = not is_calibration
            print(f"calibration: {is_calibration}")

            
    if (key == Key.up) :
        intensities[channel - 1] = min(intensities[channel - 1] + 1, 30)
        # global_intensity = min(global_intensity + 1, 30)
        print(f"{channel} channel - intensity: {intensities[channel - 1]}")
        # print(f"global intensity: {global_intensity}")
        

    elif (key == Key.down) :
        intensities[channel - 1] = max(intensities[channel - 1] - 1, 0)
        # global_intensity = max(global_intensity - 1, 0)
        print(f"{channel} channel - intensity: {intensities[channel - 1]}")
        # print(f"global intensity: {global_intensity}")

    elif (key == Key.left) :
        focusing_channel_index = (focusing_channel_index - 1) % len(channel_list)
        channel = channel_list[focusing_channel_index]
        print(f"[electro] current channel: {channel}, intensity: {intensities[channel - 1]}")
    elif (key == Key.right) :
        focusing_channel_index = (focusing_channel_index + 1) % len(channel_list)
        channel = channel_list[focusing_channel_index]
        print(f"[electro] current channel: {channel}, intensity: {intensities[channel - 1]}")

def keyrelease_callback(key) :
    # If I want to do something when keys are released, write a code here
    # ---
    if (hasattr(key, "char")) :
        c = key.char
    # ...


def main() :
    global is_stimulating, is_calibration, channel, intensities, global_intensity

    listener = Listener(on_press=keypress_callback, on_release=keyrelease_callback)
    listener.start()

    _index = 1
    while (True) :
        # can toggle by presssing 'c'
        # TODO: Calibrate the intensity first before applying stimulation to avoid pain sensations
        if (is_calibration) :
            print(channel)
            es.simple_stimulus_app(channel, 1, intensities[channel - 1])

        # can toggle this by pressing 's'
        elif (is_stimulating) :
            # === ===
            # _indices = [ch - 1 for ch in channel_list]
            # _intensities = intensities[_indices]
            # print(str(_intensities))
            # print(channel_list)
            # === ===

            # vertical moving line ---
            # _channel_list = []
            # for number in range(0, COLUMN_ELECTRODES) :
            #     _channel_list.append(number * ROW_ELECTRODES + _index)
            # _index = _index % ROW_ELECTRODES + 1

            # horizontal moving line ----
            _channel_list = []
            for number in range(1, ROW_ELECTRODES + 1) :
                _channel_list.append(number + ROW_ELECTRODES * (_index - 1))
            _index = _index % COLUMN_ELECTRODES + 1

            # predefined shapes
            # _channel_list = channel_list
            

            print(_channel_list)
            _intensities = [intensities[_ch - 1] for _ch in _channel_list]
            # print(_intensities)
            _pulse_count = 10
            es.array_stimulus_app(_channel_list, _pulse_count, _intensities)
            

        else :
            time.sleep(0.1)

if __name__ == "__main__" :
    logging.basicConfig(
        format = "%(levelname)s:%(message)s",
        level = logging.INFO
        # level = logging.DEBUG
    )
    print("""
key mappings:
          c (calib): toggle calibration
          s (stim): toggle stimlation
          n (next): change predefined shapes
          up arrow: increase intensity
          down arrow: decrease intensity
          right arrow: next channel of the current shape for calibration
          left arrow: previous channel of the current shape for calibration
""")
    main()