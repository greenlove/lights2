#!/bin/bash -f
python renderer.py lights.json  & 
python foot_controls.py palettes.json foot_controls.json &
python3 microphone.py
