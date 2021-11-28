from dmxpy import DmxPy
import datetime
import time
import sys
import json
import math
from colors import *
from jelly import *
import redis

def usage():
    print ("lights.json")

def render_light(channel, light_type, color, brightness, settings, context):
    light_key_prefix = "light_" + str(channel)
    (r,g,b) = get_rgb(color)
    #print("brightness: " + str(brightness))
    if light_type == "RGB":
        DMX.setChannel(channel, (int) (r * brightness))
        DMX.setChannel(channel + 1, (int) (g * brightness))
        DMX.setChannel(channel + 2, (int) (b * brightness))
    elif light_type == "RGBx3":
        DMX.setChannel(channel, (int) (r * brightness))
        DMX.setChannel(channel + 1, (int) (g * brightness))
        DMX.setChannel(channel + 2, (int) (b * brightness))
        DMX.setChannel(channel + 3, (int) (r * brightness))
        DMX.setChannel(channel + 4, (int) (g * brightness))
        DMX.setChannel(channel + 5, (int) (b * brightness))
        DMX.setChannel(channel + 6, (int) (r * brightness))
        DMX.setChannel(channel + 7, (int) (g * brightness))
        DMX.setChannel(channel + 8, (int) (b * brightness))
    elif light_type == "jelly_dome":
        current_color = context.get(light_key_prefix + "_color", "black")
        current_direction = context.get(light_key_prefix + "_direction", True)

        direction = current_direction
        if (color != current_color):
            direction = not direction
        
        bright_val = jelly_bright(brightness)
        color_val = jelly_code_for_color(color)
        rotation_val = jelly_speed_direction(10.0, direction)

        context[light_key_prefix + "_color"] = color
        context[light_key_prefix + "_direction"] = direction
        #print ("direction:" + str(direction))

        if settings["special_on"] == "False":
            bright_val = 0
            rotation_val = 0
        
        DMX.setChannel(channel, int(bright_val))
        DMX.setChannel(channel + 1, color_val)
        DMX.setChannel(channel + 2, rotation_val)
        

def get_colors(palette, switch_time, context):
    s = context["s"]
    num_colors = len(palette)
    if num_colors == 0:
        l = c = r = "ffffff"
        return

    last_palette = context.get("palette", [])
    if last_palette != palette:
        #new palette, switch color, update last change
        last_color_change = s
        current_color_index = 0
    else:    
        #is it time to update?
        last_color_change = context.get("last_color_change", 0)
        current_color_index = context.get("current_color_index", 0)
    
        if (last_color_change + switch_time) < s:
            current_color_index = (current_color_index + 1) % num_colors
            last_color_change = s

    l = palette[current_color_index % num_colors]
    c = palette[(current_color_index + 1) % num_colors]
    r = palette[(current_color_index + 2) % num_colors]

    context["last_color_change"] = last_color_change
    context["current_color_index"] = current_color_index
    context["palette"] = palette

    return (l,c,r)


def clamp(val, minVal, maxVal):
    return min(max(val, minVal), maxVal)

def set_color(lights_list, location, color, settings, acoustics, context):

    stdevs = 0.0
    if float(acoustics["stdev_loudness"]) > 0.0:
        stdevs = (float(acoustics["loudness"]) - float(acoustics["avg_loudness"])) / float(acoustics["stdev_loudness"])
    std_brightness =  clamp(0.5 + (stdevs / 2.0), 0.0, 1.0)
    
    for light in lights_list:
        locations = light["location"]
        if location in locations:
            channel = light["channel"]
            if "back" in locations:
                brightness = float(settings["brightness_back"])
                brightness = std_brightness
            elif "front" in locations:
                brightness = float(settings["brightness_front"])
            else:
                brightness = float(settings["brightness_middle"])

            render_light(channel, light["type"], color, brightness, settings, context)


def render(lights_list, settings, acoustics, context):

    palette = settings["palette"].split(",")
    switch_time = float(settings["switch_time"])
    (l,c,r) = get_colors(palette, switch_time, context)

    set_color(lights_list, "left", l, settings, acoustics, context)
    set_color(lights_list, "center", c, settings, acoustics, context)
    set_color(lights_list, "right", r, settings, acoustics, context)

    DMX.render()   

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    lights_path = sys.argv[1]
    lights_f = open(lights_path, "r")
    lights_lines = lights_f.read()
    lights = json.loads(lights_lines)["lights"]

    DMX = DmxPy.DmxPy('/dev/ttyUSB0')
    DMX.blackout()

    r = redis.Redis(decode_responses=True)
    frame_rate = 20
    micros_per_frame = 1000000.0 / frame_rate
    start = datetime.datetime.now()

    render_context = {}
    while True:
        before = datetime.datetime.now()
        settings = r.hgetall("settings")
        acoustics = r.hgetall("acoustics")
        #current_palette = ["6a0dad","6a0dad","ff000", "6a0dad","6a0dad","00ffff"]
        render_context["s"] = (before - start).total_seconds()
        render(lights, settings, acoustics, render_context)
        after = datetime.datetime.now()
        elapsed = (after - before).microseconds
        diff = micros_per_frame - elapsed
        time.sleep(diff / 1000000.0)
    
