import sys
from rtmidi.midiutil import open_midiinput
import rtmidi
from PIL import Image
import time

# local import
from chord_list import chords
from chord_list import chord_lookup
from max7219_init import device

# global variables
noteBuffer = [None] * 10
counter = 0
chordPressed = False
notesPressed = [None] * 3

# go through all basic chords and check if a chord has been pressed
def checkForChord():
    global noteBuffer
    global notesPressed
    global chords
    root = False
    middle = False
    last = False
    for k in range(24):
        for l in range(3):
            if l == 0:
                root = False
                middle = False
                last = False
            for m in range(8):
                for i in range(10):
                    if noteBuffer[i] == chords[k][l][m] and l == 0:
                        notesPressed[l] = chords[k][l][m]
                        root = True
                    if noteBuffer[i] == chords[k][l][m] and l == 1:
                        notesPressed[l] = chords[k][l][m]
                        middle = True
                    if noteBuffer[i] == chords[k][l][m] and l == 2:
                        notesPressed[l] = chords[k][l][m]
                        last = True
        if root and middle and last:
            # if pressed chord has been found, draw it to the 8x8 LED screen
            drawChordToScreen(k)
            return True
    return False

# evaluates if current chord is still pressed, and thus updates boolean variable chordPressed
def checkForRelease(note):
    global notesPressed
    for l in range(3):
        if notesPressed[l] == note:
            notesPressed = [None] * 3
            clearScreen()
            return False
    return True

def addNote(note):
    global noteBuffer
    global counter
    if counter < 10:
        noteBuffer[counter] = note
        counter += 1
    else:
        counter = 0
        noteBuffer[counter] = note
        counter += 1

def releaseNote(note):
    global noteBuffer
    noteBuffer.remove(note)
    noteBuffer.append(None)
    
def clearScreen():
    device.clear()

# draw to max7218 LED 8x8 pixel screen
def drawChordToScreen(chord):
    global chord_lookup
    chord_id = chord_lookup[chord]
    img = Image.frombytes("1", (8,8), chord_id)
    device.display(img)

if __name__ == '__main__':

    # paino is currently set to port 1
    port = 1
    # checking if a usb MIDI instrument has been connected to the device
    midi_out = rtmidi.MidiOut()
    number_ports = len(midi_out.get_ports())
    while number_ports < 2:
        time.sleep(1)
        number_ports = len(midi_out.get_ports())

    try:
        midi, port_name = open_midiinput(port, interactive=False)
    except (EOFError, KeyboardInterrupt):
        sys.exit()

    print("Press any chords on your piano. Press crtl-c to exit.")
    try:
        while True:
            # check if MIDI instrument is still connected
            number_ports = len(midi_out.get_ports())
            if number_ports < 3:
                raise Exception("MIDI instrument has been removed")
            # receive MIDI messages (3 bytes long) from the piano
            msg = midi.get_message()

            if msg:
                message, tmp = msg
                # check, if note on/off
                if message[2] > 0:
                    addNote(message[1])
                    if not chordPressed:
                        chordPressed = checkForChord()
                else:
                    # release  note from buffer
                    releaseNote(message[1])
                    # check, if chord has been released
                    if chordPressed:
                        chordPressed = checkForRelease(message[1])
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midi.close_port()
        del midi
