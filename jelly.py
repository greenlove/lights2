from colors import *

def jelly_colors():
    return ["red", "green", "blue", "yellow", "cyan", "magenta", "white"]


def jelly_code_for_color(color):
    (closest, c_dist) = closest_color(color, ["red", "green", "blue", "yellow", "cyan", "magenta", "white"])
    #print (str(color), str(closest), str(c_dist))
    if c_dist > 0.1:
        closest = "white"

    return jelly_color_code(closest)
    

def jelly_bright(brightness):
    return brightness * 199

def jelly_speed_direction(switch_time, clockwise):
    #switch time between 0 and 40
    #print ("SWITCH_TIME:" + str(switch_time), "CLOCKWISE:" + str(clockwise))
    amount = (40.0 - switch_time) * (110.0 / 80.0)
    if clockwise:
        return int(120 - amount)
    else:
        return int(135 + amount)
    

def jelly_color_code(color_name):
    #print ("color_name:" + str(color_name))
    if color_name == "blue":
        return 0

    if color_name == "green":
        return 17
    
    if color_name == "white":
        return 34

    if color_name == "red":
        return 51

    if color_name == "cyan":
        return 68

    if color_name == "light_blue":
        return 85

    if color_name == "magenta":
        return 102

    if color_name == "light_green":
        return 119

    if color_name == "yellow":
        return 136

    if color_name == "pink":
        return 153

    if color_name == "light_cyan":
        return 170

    if color_name == "red_green_blue":
        return 187

    if color_name == "light_magenta":
        return 204

    if color_name == "light_yellow":
        return 221

    if color_name == "all":
        return 238
    
    return 238
