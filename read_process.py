#!/usr/bin/env python
from __future__ import print_function

import time
import sqlite3
import os.path
from sys import exit
from datetime import datetime

import RPi.GPIO as GPIO
from RPIO import PWM

data1 = 7  # (White) PIN
data0 = 11  # (Green) PIN
servo_pin = 27
servo_range = [600, 1300]  # Left, Right (2300 Max, 500 Min)
DATABASE = 'doorlock.db'
base_timeout = 5
RFID_STATUS_FILE = '/tmp/rfid_running'

timeout = base_timeout
bits = ''

PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
servo = PWM.Servo()


def gpio_setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(data1, GPIO.IN)
    GPIO.setup(data0, GPIO.IN)
    GPIO.add_event_detect(data1, GPIO.FALLING, callback=one)
    GPIO.add_event_detect(data0, GPIO.FALLING, callback=zero)


def sql_setup():
    if os.path.isfile(DATABASE) != True:
        print('''
        Missing Database. Run sql_setup.py script w/o root to create.
        Cannot use sudo or other user programs cannot interact with tables.
        ''')

def connect_db():
    return sqlite3.connect(DATABASE)

def one(channel):
    global bits
    global timeout
    bits = bits + '1'
    timeout = base_timeout


def zero(channel):
    global bits
    global timeout
    bits = bits + '0'
    timeout = base_timeout


def loop():
    global timeout
    global bits
    print('Ready')
    while True:
        if len(bits) > 0:
            timeout -= 1
            if timeout == 0:
                process_card(bits)
                bits = ''
                timeout = base_timeout
        time.sleep(.001)


def process_card(binary):
    name, status = auth_status(binary)
    if status == True:
        print(u'Allowed "{}" entry.'.format(name))
        unlock_door()
        log(status, binary, name)
    else:
        print('Disallowed:', binary)
        log(False, binary)


def auth_status(bit_query):
    con = connect_db()
    with con:
        cur = con.cursor()
        cur.execute(
            'SELECT name FROM users WHERE Binary = ?', [bit_query])
        row = cur.fetchone()
        if row is None:
            return row, False
        else:
            return row[0], True


def log(status, binary, name=None):
    con = connect_db()
    with con:
        cur = con.cursor()
        cur.execute('''INSERT INTO log (date, name, binary, status)
                       VALUES(?,?,?,?)''',
                       (datetime.utcnow(), name, binary, status))


def unlock_door(method='card'):
    if method == 'button':
        log('True', 'Web Button', 'Web User')
    print('Unlocking...')
    servo.set_servo(servo_pin, servo_range[1])
    time.sleep(4)
    print('Locking...')
    servo.set_servo(servo_pin, servo_range[0])
    time.sleep(2)
    servo.stop_servo(servo_pin)
    return True


def main():
    try:
        open('RFID_STATUS_FILE', 'w')
        gpio_setup()
        sql_setup()
        loop()
    except KeyboardInterrupt:
        os.remove('RFID_STATUS_FILE')
        GPIO.cleanup()
        print('Clean Exit.')

if __name__ == '__main__':
    main()
