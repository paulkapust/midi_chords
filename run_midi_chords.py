#!/usr/bin/python
from subprocess import Popen

script_name = "midi_chords.py"
while True:
    print("\nStarting " + script_name)
    p = Popen("python " + script_name, shell=True)
    p.wait()
