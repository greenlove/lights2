#!/bin/bash -f
python3 renderer.py lights.json  & 
python3 foot_controls.py palettes.json foot_controls.json &
python3 microphone.py
