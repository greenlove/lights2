import sys
import colorsys
import json
import re
import math


COLOR_DEFS = {
    "red": "ff0000",
    "pink": "ffc0cb",
    "green": "00ff00",
    "orangered": "ff4500",
    "blue": "0000ff",
    "cyan": "00ffff",
    "black": "000000",
    "white": "ffffff",
    "faint_white": "999999",
    "yellow": "ffff00",
    "magenta": "ff00ff",
    "gold": "d4af37",
    "orange": "ffa500",
    "purple": "6a0dad",
    "amber" : "ffbf00",
    "blue_green": "33ffd1"
}

def get_hex(r, g, b):
    return "{0:0{1}x}".format(r, 2) + "{0:0{1}x}".format(g, 2) + "{0:0{1}x}".format(b, 2)

def get_rgb(c):
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:], 16)

    return (r, g, b)

def hls_dist(h1, h2, l1, l2, s1, s2):
    return math.sqrt((h1 - h2)**2 + (l1 - l2)**2 + (s1 -s2)**2)

def closest_color(color, colors):
    #print ("color:" + color)
    target = resolve_color(color)
    (t_r, t_g, t_b) = get_rgb(target)
    (t_h, t_l, t_s) = colorsys.rgb_to_hls(t_r / 255.0, t_g/ 255.0, t_b / 255.0)

    distances = []
    
    for c in colors:
        option = resolve_color(c)
        #print ("option:" + option)
        (c_r, c_g, c_b) = get_rgb(option)
        (c_h, c_l, c_s) = colorsys.rgb_to_hls(c_r / 255.0, c_g/ 255.0, c_b / 255.0)
        d_c = hls_dist(t_h, c_h, t_l, c_l, t_s, c_s)
        distances.append((c, d_c))

    
    distances_sorted = sorted(distances, key=lambda x:x[1])
    #print str(distances_sorted)
    return distances_sorted[0]


def change_color(color_start, color_end, change_fraction):
    (r_start, g_start, b_start) = get_rgb(color_start)
    (r_end, g_end, b_end) = get_rgb(color_end)
    new_r = (r_end * change_fraction + r_start * (1 - change_fraction))
    new_g = (g_end * change_fraction + g_start * (1 - change_fraction))
    new_b = (b_end * change_fraction + b_start * (1 - change_fraction))

    new_color = get_hex(int(new_r), int(new_g), int(new_b))
    return new_color

def color_shift(color, hue_shift):
    (r, g, b) = get_rgb(color)
    (h, l, s) = colorsys.rgb_to_hls(r / 255.0, g/ 255.0, b / 255.0)
    (r_new, g_new, b_new) = colorsys.hls_to_rgb(h + hue_shift / 360.0, l, s)
    return get_hex(int(r_new * 255), int(g_new * 255), int(b_new * 255))

def color_next(color1, color2):
    (r1, g1, b1) = get_rgb(color1)
    (r2, g2, b2) = get_rgb(color2)
    (h1, l1, s1) = colorsys.rgb_to_hls(r1 / 255.0, g1/ 255.0, b1 / 255.0)
    (h2, l2, s2) = colorsys.rgb_to_hls(r2 / 255.0, g2/ 255.0, b2 / 255.0)
    h3 = h2 + (h2 - h1) # shift h3 same distance ahead that h2 was
    (r_new, g_new, b_new) = colorsys.hls_to_rgb(h3, l1, s1)
    
    return get_hex(int(r_new * 255), int(g_new * 255), int(b_new * 255))


def color_mid(color1, color2):
    (r1, g1, b1) = get_rgb(color1)
    (r2, g2, b2) = get_rgb(color2)
    (h1, l1, s1) = colorsys.rgb_to_hls(r1 / 255.0, g1/ 255.0, b1 / 255.0)
    (h2, l2, s2) = colorsys.rgb_to_hls(r2 / 255.0, g2/ 255.0, b2 / 255.0)
    h3 = (h1 + h2) / 2.0 # h3 average of h1 and h2
    (r_new, g_new, b_new) = colorsys.hls_to_rgb(h3, l1, s1)
    
    return get_hex(int(r_new * 255), int(g_new * 255), int(b_new * 255))


def resolve_color(color_str):
    if color_str in COLOR_DEFS:
        return COLOR_DEFS[color_str]

    shift_pattern = "color_shift\(([a-z_0-9]*),\s?(-?[0-9]*)\)"
    shift_match = re.match(shift_pattern, color_str)
    if shift_match:
        color = resolve_color(shift_match.group(1))
        shift = float(shift_match.group(2))
        return color_shift(color, shift)

    next_pattern = "color_next\(([a-z_0-9]*),\s?([a-z0-9]*)\)"
    next_match = re.match(next_pattern, color_str)
    if next_match:
        color1 = resolve_color(next_match.group(1))
        color2 = resolve_color(next_match.group(2))
        return color_next(color1, color2)

    mid_pattern = "color_mid\(([a-z_0-9]*),\s?([a-z0-9]*)\)"
    mid_match = re.match(mid_pattern, color_str)
    if mid_match:
        color1 = resolve_color(mid_match.group(1))
        color2 = resolve_color(mid_match.group(2))
        return color_mid(color1, color2)

    return color_str


def usage():
    print ("palette.json color_string")
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    palettes_path = sys.argv[1]
    color_string = sys.argv[2]
    
    palettes_f = open(palettes_path, "r")
    palettes = json.loads(palettes_f.read())

    print(resolve_color(color_string, palettes))

