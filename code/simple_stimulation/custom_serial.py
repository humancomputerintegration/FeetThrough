"""
# serial client for MUX and DACs (to drive LRAs)
"""

from serial import Serial
import numpy as np
import logging
import struct

port = "COM9" # change this!
baudrate = 921600 # check this!

ELECTRO_HEADER = 0xFF

FAKE_SERIAL = False

if FAKE_SERIAL:
    print("[custom_serial] Notice FAKE_SERIAL is true. you cannot communicate with the controller ")
    myserial = None
else :
    myserial = Serial(port, baudrate, timeout=1.0)

def send_serial(data_bytes) :
    try :
        if (myserial is not None) :
            myserial.write(data_bytes)
    except Exception as e :
        logging.warning(e)

def is_open() :
    return myserial is not None

def close() :
    if (is_open()) :
        myserial.flush()
        myserial.close()