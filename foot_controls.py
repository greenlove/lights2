import time
import sys
import json
import rtmidi
from colors import *
import redis

SWITCH_TIME = 10
FRONT_BRIGHTNESS = 0.7
BACK_BRIGHTNESS = 0.7
MIDDLE_BRIGHTNESS = 0.7
PALETTE_NUM = 0
NUM_PALETTES = 0
PALETTE = {}
COLOR_VALUES = {}
SPECIAL_ON = False
MODE="brightness"


def usage():
    print ("palette.json controls.json")

def handle_midi_command(midi_in, commands):
    global PALETTE_NUM
    global NUM_PALETTES
    global FRONT_BRIGHTNESS
    global BACK_BRIGHTNESS
    global MIDDLE_BRIGHTNESS
    global SWITCH_TIME
    global MODE
    global SPECIAL_ON
    
    while True:
        msg = midi_in.get_message()
        if not msg:
            return

        (t, velocity) = msg
        l = [ hex(e) for e in t]
        first = l[0]
        second = l[1]
        value = None
        if len(l) > 2:
            value = int(l[2], 16)

        print ("first:" + str(first) + " second:" + str(second) + " value:" + str(value))
        key = (first, second)
        if not key in commands:
            continue
        command = commands[key]

        print ("command:" + str(command))
        
        if (command == "next_palette" and value == 0):
            PALETTE_NUM = (PALETTE_NUM + 1) % NUM_PALETTES
            set_palette()
        elif (command == "prev_palette" and value == 0):
            PALETTE_NUM = (PALETTE_NUM + NUM_PALETTES - 1) % NUM_PALETTES
            set_palette()
        elif (command == "brightness"):
            MODE = "brightness"
        elif (command == "timing"):
            MODE = "timing"
        elif (command == "special"):
            MODE = "special"
        elif (command == "first_adjust" and MODE == "brightness"):
            FRONT_BRIGHTNESS = float(value) / 123.0
            set_brightness()
        elif (command == "first_adjust" and MODE == "special"):
            MIDDLE_BRIGHTNESS = float(value) / 123.0
            set_brightness()
        elif (command == "second_adjust" and MODE == "brightness"):
            BACK_BRIGHTNESS = float(value) / 123.0
            set_brightness()
        elif (command == "first_adjust" or command == "back_adjust") and MODE == "timing":
            SWITCH_TIME = 40.0 * (float(value) / 123.0)
            set_timing()
        elif (command == "home"):
            PALETTE_NUM = 0
            set_palette()
        elif (command == "toggle_special" and value == 0):
            SPECIAL_ON = not SPECIAL_ON
            set_special()


def commands_from_controls(controls):
    midi_to_command = {}
    for (command,matchers) in controls.items():
        key = (matchers["first"], matchers["second"])
        if key in midi_to_command:
            print ("same midi for:" + midi_to_command[key] + " and " + command)
            continue
        midi_to_command[key] = command

    print (str("midi_to_command:" + str(midi_to_command)))
    return midi_to_command

def set_palette():
    global PALETTE
    global COLORS
    global PALETTE_NUM
    global R
    PALETTE = palettes["palettes"][PALETTE_NUM]
    print ("cycling: " + PALETTE["name"])
    COLORS = [resolve_color(c) for c in PALETTE["colors"]]
    colorsStr = ",".join(COLORS)
    R.hset("settings", "palette", colorsStr)
    

def set_brightness():
    R.hset("settings", "brightness_front", FRONT_BRIGHTNESS)
    R.hset("settings", "brightness_back", BACK_BRIGHTNESS)
    R.hset("settings", "brightness_middle", MIDDLE_BRIGHTNESS)
    

def set_timing():
    R.hset("settings", "switch_time", SWITCH_TIME)
    

def set_special():
    R.hset("settings", "special_on", str(SPECIAL_ON))
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    midiin = rtmidi.MidiIn()
    midiin.close_port()
    midiin.open_port(1)

    R = redis.Redis()
    
    palette_path = sys.argv[1]
    palette_f = open(palette_path, "r")
    controls_path = sys.argv[2]
    # starting_palette = sys.argv[3].strip()
    controls_f = open(controls_path, "r")
    controls_lines = controls_f.read()
    controls = json.loads(controls_lines)
    commands = commands_from_controls(controls)

    palette_lines = palette_f.read()
    palettes = json.loads(palette_lines)
    NUM_PALETTES = len(palettes["palettes"])

    set_palette()
    set_brightness()
    set_timing()
    set_special()
    
    count = 0
    while True:
        handle_midi_command(midiin, commands)
        time.sleep(0.05) # 1/20 second
    
