# ----
# NEED IMPLEMENTATION
# https://github.com/humancomputerintegration/rehamove-integration-lib
# While we used RehaStim in this paper, RehaMove can also be used for electrical stimulation.
# please, rewrite stimulation parts for your stimulator.

# -----

import numpy as np
import time
import logging

import photo_relay_switching as mux


STIMULATION_FREQ = 50 # Hz

PC_ESP32_STIM_PATTERN = 0xFF

pulse_width = 250
pulse_count = 10

# client for electrical stimulator ----- 
# NEED IMPLEMENTATION
client = ## please implement a client for your stimulator

## ------------------ 


def sleep_time_ns(us) :
    # logging.debug(f"current time_ns: {time.time_ns()}")
    ct = time.time_ns()
    st = ct
    while ct < st + (us * 1000) :
        ct = time.time_ns()
    logging.debug(f"elapsed: {(time.time_ns() - st) / 1000000} ms")

def sleep_perf_counter(us) :
    # logging.debug(f"current time_ns: {time.perf_counter_ns()}")
    ct = time.perf_counter_ns()
    st = ct
    while ct < st + (us * 1000) :
        ct = time.perf_counter_ns()
    logging.debug(f"elapsed: {(time.perf_counter_ns() - st) / 1000000} ms")




# for final electroces (5x12)
def simple_stimulus_app(ch, _pulse_count, _intensity) :
    if (ch <= 0) : 
        return
    mux.make_one_point_stimulus_electro_foot(ch)
    mux.load_switch()
    sleep_for_switching = 1000 # depends on the number of boards
    sleep_perf_counter(sleep_for_switching)

    for i in range(_pulse_count) :
        # --- send one pulse ---
        # NEED IMPLEMENTATION
        # client.write()
        # --------

        sleep_us = (1000 * 1000) / STIMULATION_FREQ
        sleep_time_ns(sleep_us)


# for final electrodes (5x12)
def array_stimulus_app(ch_array, _pulse_count, _intensities) :
    sleep_for_switching = 1000 #750 # us
    # FIXME: we have to be careful for this sleep time. it needs more time than the ideal value sometimes

    # TODO temp_intensity => need to use calibrated intensity
    for i in range(_pulse_count) :
        st = time.perf_counter_ns()
        for _i, ch in enumerate(ch_array) :
            # print(ch, _intensities[_i])
            mux.make_one_point_stimulus_electro_foot(ch)
            mux.load_switch()
            sleep_perf_counter(sleep_for_switching)

            # --- send one pulse ---
            # NEED IMPLEMENTATION
            # client.write() # should use each calibrated intensity for each electrode for better sensations
            # --------

            sleep_for_pulses = (pulse_width * 2 + 100 + 100) # us
            # FIXME: we have to be careful for this sleep time. it needs more time than the ideal value
            if (sleep_for_pulses > 0) :
                sleep_perf_counter(sleep_for_pulses) # wait for the wave length (RehaStim)

        # manage stimulation frequency
        # when using large number of channels, might be better to comment out this part
        elapsed = (time.perf_counter_ns() - st) / 1000.0 # us
        sleep_time = (1000000 / STIMULATION_FREQ) - elapsed # - 2 * sleep_for_switching - sleep_for_pulses
        if (sleep_time > 0) : 
            # print(sleep_time)
            sleep_time_ns(sleep_time) # 50 Hz



def shape_stimulus_gel(ch_array, _intensities) :
    pulse_count = 5
    sleep_for_switching = 1000 #750 # us # check 
    # FIXME: should be careful for this sleep time. it needs more time than the ideal value sometimes

    # TODO temp_intensity => need to use calibrated intensity
    for i in range(pulse_count) :
        st = time.perf_counter_ns()
        for _i, ch in enumerate(ch_array) :
            # print(ch, _intensities[_i])
            mux.make_one_point_stimulus_gel(ch)
            mux.load_switch()
            sleep_perf_counter(sleep_for_switching)
            
            # --- send one pulse ---
            # NEED IMPLEMENTATION
            # client.write() # should use each calibrated intensity for each electrode for better sensations
            # --------

            sleep_for_pulses = (pulse_width * 2 + 100 + 100) # us
            # FIXME: shouldbe be careful for this sleep time. it needs more time than the ideal value sometimes
            if (sleep_for_pulses > 0) :
                sleep_perf_counter(sleep_for_pulses) # wait for the wave length (RehaStim)

        elapsed = (time.perf_counter_ns() - st) / 1000.0 # us
        sleep_time = (1000000 / STIMULATION_FREQ) - elapsed # - 2 * sleep_for_switching - sleep_for_pulses
        if (sleep_time > 0) : 
            # print(sleep_time)
            sleep_time_ns(sleep_time) # 50 Hz

def shape_stimulus_pcb(ch_array, _intensities) :
    pulse_count = 1
    sleep_for_switching = 1000 #750 # us
    # FIXME: should be careful for this sleep time. it needs more time than the ideal value sometimes

    for i in range(pulse_count) :
        st = time.perf_counter_ns()
        for _i, ch in enumerate(ch_array) :
            # print(ch, _intensities[_i])
            mux.make_one_point_stimulus_pcb(ch)
            mux.load_switch()
            sleep_perf_counter(sleep_for_switching)
            
            # --- send one pulse ---
            # NEED IMPLEMENTATION
            # client.write() # should use each calibrated intensity for each electrode for better sensations
            # --------

            sleep_for_pulses = (pulse_width * 2 + 100 + 100) # us

            if (sleep_for_pulses > 0) :
                sleep_perf_counter(sleep_for_pulses) # wait for the wave length (RehaStim)

        # elapsed = (time.perf_counter_ns() - st) / 1000.0 # us
        # sleep_time = (1000000 / STIMULATION_FREQ) - elapsed # - 2 * sleep_for_switching - sleep_for_pulses
        # if (sleep_time > 0) : 
        #     # print(sleep_time)
        #     sleep_time_ns(sleep_time) # 50 Hz



