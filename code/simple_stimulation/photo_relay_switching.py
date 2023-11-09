import numpy as np
import logging
import random

import custom_serial

# photorelays switching

HEAD_ELECTRO = 0xFF
HEAD_VIBRO = 0xFE

sw_channel_num = 64 # if the number of boards is changed, please change this!

STIMULATION_CHANNELS = 60
STATE_OPEN = 0
STATE_GND = 1
STATE_HIGH = 2

# for pcb
PCB_ROW_ELECTRODE = 5 # change this too!
PCB_COLUMN_ELECTRODE = 12 # change this too!

# for gel electrodes
GEL_ROW_ELECTRODE = 4
GEL_COLUMN_ELECTRODE = 4

sw_channel_state = np.full(sw_channel_num, STATE_OPEN, dtype="<u1")

def debug_print_states_pcb(row_number) :
    states = "\n"
    for i, s in enumerate(sw_channel_state) :
        if (i > 31) :
            i += 3
        if (s == STATE_OPEN) :
            # states.append("OPEN")
            states += " X"
        elif (s == STATE_GND) :
            # states.append("GND")
            states += " ○"
        elif (s == STATE_HIGH) :
            # states.append("HIGH")
            states += " ●"
        if ((i + 1) % row_number == 0 or i == 31) :
            states += "\n"
    logging.debug(states)


def is_all_same_state() :
    s = sw_channel_state[0]
    res = np.all(sw_channel_state == s)
    return res
        

def make_ch_high(ch) :
    if (ch <= 0 or sw_channel_num < ch) :
        logging.info("[mux] make_ch_high: ch is out of the range")
        return
    sw_channel_state[ch - 1] = STATE_HIGH

def make_ch_gnd(ch) :
    if (ch <= 0 or sw_channel_num < ch) :
        logging.info("[mux] make_ch_gnd: ch is out of the range")
        return
    sw_channel_state[ch - 1] = STATE_GND

def make_ch_open(ch) :
    if (ch <= 0 or sw_channel_num < ch) :
        logging.info("[mux] make_ch_open: ch is out of the range")
        return
    sw_channel_state[ch - 1] = STATE_OPEN

def make_all_switch_open() :
    for i in range(0, sw_channel_num) :
        sw_channel_state[i] = STATE_OPEN

def make_one_point_high_others_gnd(ch) :
    for i in range(0, sw_channel_num) :
        sw_channel_state[i] = STATE_GND
    sw_channel_state[ch - 1] = STATE_HIGH

def load_switch() :
    data = bytearray([HEAD_ELECTRO] + list(sw_channel_state))
    logging.debug(f"[mux] serial send: {data}")
    custom_serial.send_serial(data)

def load_kaji_switch() :
    data = bytearray(list(sw_channel_state))
    logging.debug(f"[mux] serial send: {data}")
    custom_serial.send_serial(data)

def is_vertical_edge(ch) :
    is_edge = (ch % PCB_ROW_ELECTRODE == 0) or ((ch - 1) % PCB_ROW_ELECTRODE == 0)
    return is_edge

def random_channel_set() :
    s1 = STATE_HIGH
    s2 = STATE_GND
    _MAX_CHANNEL = 60# 30
    ch = random.randint(1, _MAX_CHANNEL) # a <= ch <= b
    sw_channel_state[ch - 1] = s1 # overwrite
    # making reference electrodes
    for mul in [-1, 0, 1] :
        for offset in [-1, 0, 1] :
            _ch = ch + mul * PCB_ROW_ELECTRODE + offset
            if (_ch < 1 or sw_channel_num < _ch or ch == _ch) :
                continue
            if (ch % PCB_ROW_ELECTRODE == 0 and offset > 0) :
                continue
            if ((ch - 1) % PCB_ROW_ELECTRODE == 0 and offset < 0) :
                continue

            sw_channel_state[_ch - 1] = s2
    
    debug_print_states_pcb(PCB_ROW_ELECTRODE)


def make_two_points_stimuli(ch1, ch2) :
    # ch: 1 ~ 8
    s1 = STATE_HIGH
    s2 = STATE_GND
    center_ix1 = ch1 + PCB_ROW_ELECTRODE - 1
    center_ix2 = ch2 + PCB_ROW_ELECTRODE - 1

    for index in [center_ix1, center_ix2] :

        above_index = index - PCB_ROW_ELECTRODE
        sw_channel_state[above_index] = s2
        bottom_index = index + PCB_ROW_ELECTRODE
        sw_channel_state[bottom_index] = s2

        left_index = index - 1
        # print(left_index)
        if (left_index >= PCB_ROW_ELECTRODE) :
            sw_channel_state[left_index] = s2

        right_index = index + 1
        # print(right_index)
        if (right_index <= 2 * PCB_ROW_ELECTRODE - 1) :
            sw_channel_state[right_index] = s2

    sw_channel_state[center_ix1] = s1
    sw_channel_state[center_ix2] = s1

    debug_print_states_pcb(PCB_ROW_ELECTRODE)


def is_available(ch) :
    return (ch > 0) and (ch <= PCB_COLUMN_ELECTRODE * PCB_ROW_ELECTRODE) # if ch is more than one row
    
# def is_bottom_available(ch) :
#     return ch <= (COLUMN_ELECTRODE - 1) * ROW_ELECTRODE # if ch is less than the last row

def is_left_edge(ch) :
    return (((ch - 1) % PCB_ROW_ELECTRODE) == 0) # if ch is not on left edge?

def is_right_edge(ch) :
    return ((ch % PCB_ROW_ELECTRODE) == 0) # if ch is not on right edge?

def is_available_foot_electrodes(ch) :
    return (ch > 0) and (ch <= PCB_COLUMN_ELECTRODE * PCB_ROW_ELECTRODE + 2) # if ch is more than one row
    

def is_left_edge_foot_electrodes(ch) :
    if (ch > 32) :
        # if ch is converted, make it back temporaily
        ch -= 2
    return (((ch - 1) % PCB_ROW_ELECTRODE) == 0) # if ch is not on left edge?

def is_right_edge_foot_electrodes(ch) :
    if (ch > 32) :
        # if ch is converted, make it back temporaily
        ch -= 2
    return ((ch % PCB_ROW_ELECTRODE) == 0) # if ch is not on right edge?

# for final prototype (flexible pcb electrodes 5 x 12)
def make_surrouding_points_ref_for_foot_electrodes(ch, state, row_electrodes) :

    for row in [-1, 0, 1] :
        for col in [-1, 0, 1] :
            _ch = ch + row * row_electrodes + col
            if (ch >= 33 and ch <= 38 and row == -1) :
                _ch -= 2
            if (ch >= 26 and ch <= 30 and row == 1) :
                _ch += 2
            if (_ch >= sw_channel_num or _ch <= 0) :
                continue # avoid out of the range
            if (not is_available_foot_electrodes(_ch)) :
                continue # is it available?
            if ((is_left_edge_foot_electrodes(ch)) and col == -1) :
                continue # on left edge, there is no left side electrode
            if ((is_right_edge_foot_electrodes(ch)) and col == 1) :
                continue # on right edge...
            if (row == 0 and col == 0) :
                continue # don't overwrite the center point
            _index = _ch - 1
            sw_channel_state[_index] = state

# for final prototype (flexible pcb electrodes 5 x 12)
def make_one_point_stimulus_electro_foot(ch) :
    s1 = STATE_HIGH
    s2 = STATE_GND
    make_all_switch_open()
    if (ch < 0 or STIMULATION_CHANNELS < ch) :
        logging.warning("[mux] out of range")
        return
    
    # ---
    if (ch > 30) :
        ch += 2 # skip 31, 32 channels because they are not connected (hardware reason)
        # from here, stimulation channel is changed to ch + 2
    # --- 

    _index = ch - 1
    sw_channel_state[_index] = s1
    make_surrouding_points_ref_for_foot_electrodes(ch, s2, PCB_ROW_ELECTRODE)

    debug_print_states_pcb(PCB_ROW_ELECTRODE)

# for first prototype (flexible pcb electrodes 10 x 3)
def make_surrouding_points_ref(ch, state, row_electrodes) :

    for row in [-1, 0, 1] :
        for col in [-1, 0, 1] :
            _ch = ch + row * row_electrodes + col

            if (_ch >= sw_channel_num or _ch <= 0) :
                continue # avoid out of the range
            if (not is_available(_ch)) :
                continue # is it available?
            if (is_left_edge(ch) and col == -1) :
                continue # on left edge, there is no left side electrode
            if (is_right_edge(ch) and col == 1) :
                continue # on right edge...
            if (row == 0 and col == 0) :
                continue # don't overwrite the center point
            _index = _ch - 1
            sw_channel_state[_index] = state

# for gel in study 2
def make_one_point_stimulus_gel(ch) :
    s1 = STATE_HIGH
    s2 = STATE_GND
    make_all_switch_open()
    if (ch < 0 or STIMULATION_CHANNELS < ch) :
        logging.warning("[mux] out of range")
        return
    
    _index = ch - 1
    sw_channel_state[_index] = s1
    make_surrouding_points_ref(ch, s2, GEL_ROW_ELECTRODE)

    debug_print_states_pcb(GEL_ROW_ELECTRODE)


# for first prototypes (electrodes 3x10)
def make_one_point_stimulus_pcb(ch) :
    s1 = STATE_HIGH
    s2 = STATE_GND
    make_all_switch_open()
    if (ch < 0 or STIMULATION_CHANNELS < ch) :
        logging.warning("[mux] out of range")
        return

    _index = ch - 1
    sw_channel_state[_index] = s1
    make_surrouding_points_ref(ch, s2, PCB_ROW_ELECTRODE)

    debug_print_states_pcb(PCB_ROW_ELECTRODE)


def make_center_one_point_stimulus(ch) :
    # ch: 1 ~ 8
    s1 = STATE_HIGH
    s2 = STATE_GND
    center_index = ch + PCB_ROW_ELECTRODE - 1
    sw_channel_state[center_index] = s1

    # considering, physical layout: above -> minus, bottom -> pluse
    above_index = center_index - PCB_ROW_ELECTRODE
    sw_channel_state[above_index] = s2
    bottom_index = center_index + PCB_ROW_ELECTRODE
    sw_channel_state[bottom_index] = s2

    left_index = center_index - 1
    # print(left_index)
    if (left_index >= PCB_ROW_ELECTRODE) :
        sw_channel_state[left_index] = s2
        sw_channel_state[left_index + PCB_ROW_ELECTRODE] = s2 # up corner
        sw_channel_state[left_index - PCB_ROW_ELECTRODE] = s2 # bottom corner

    right_index = center_index + 1
    # print(right_index)
    if (right_index <= 2 * PCB_ROW_ELECTRODE - 1) :
        sw_channel_state[right_index] = s2
        sw_channel_state[right_index + PCB_ROW_ELECTRODE] = s2 # up corner
        sw_channel_state[right_index - PCB_ROW_ELECTRODE] = s2 # bottom corner

    debug_print_states_pcb(PCB_ROW_ELECTRODE)

def set_all_open() :
    make_all_switch_open()
    load_switch()

def set_one_point_stimulus(ch) :
    make_all_switch_open()
    make_center_one_point_stimulus(ch) # should consider to use "make_one_point_stimulus()"
    load_switch()

# for gel electrodes
def set_two_electrodes(ch1, ch2) :
    sw_channel_state[ch1 - 1] = STATE_GND
    sw_channel_state[ch2 - 1] = STATE_HIGH

    debug_print_states_pcb(PCB_ROW_ELECTRODE)
