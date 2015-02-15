"""
In this file, find the functions that actually trigger the sound generators.

graa doesn't use it's own sound generation, but different backends, as seen below.

"""
import datetime, time, threading, atexit, os, fnmatch
from pythonosc import osc_message_builder
from graa_logger import GraaLogger as log
import dirt_client
from pygame import midi
from pygame import time as pg_time 
from graa_structures import GraaNote as gnote


"""
Output "routes" to dirt ...

"""

dc = []
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44442))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44448))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44454))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44460))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44466))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44472))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44476))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44482))
dc.append(dirt_client.UDPClient("127.0.0.1", 7771, 44488))

def dirt(*args, **kwargs):
    """
    Procedure to send an event to Alex McLean's marvellous dirt sample player!

    The dirt player takes osc messages as input, via udp, on port 7771

    Each source port is interpretad as an output to dirt ...

    """
    msg = osc_message_builder.OscMessageBuilder(address = "/play")
    msg.add_arg(int(time.time()))
    msg.add_arg(datetime.datetime.now().microsecond + 4)
    msg.add_arg(args[1] + ":" + str(args[2])) #sample name:number
    msg.add_arg(float(kwargs.get('offset', 0.0)))
    msg.add_arg(float(kwargs.get('begin', 0.0)))
    msg.add_arg(float(kwargs.get('end', 1.0)))
    msg.add_arg(float(kwargs.get('speed', 1.0)))
    msg.add_arg(float(kwargs.get('pan', 0.5)))
    msg.add_arg(float(kwargs.get('velocity', 0.0)))
    msg.add_arg(kwargs.get('vowel', ' '))
    msg.add_arg(float(kwargs.get('cutoff', 0.0)))
    msg.add_arg(float(kwargs.get('resonance', 0.0)))
    msg.add_arg(float(kwargs.get('accelerate', 0.0)))
    msg.add_arg(float(kwargs.get('shape', 0.0)))
    msg.add_arg(int(kwargs.get('kriole_chunk', 0)))
    msg.add_arg(float(kwargs.get('gain', 1.0)))
    msg.add_arg(int(kwargs.get('cutgroup', 0)))
    msg.add_arg(float(kwargs.get('delay', 0.0)))
    msg.add_arg(float(kwargs.get('delaytime', -1.0)))
    msg.add_arg(float(kwargs.get('delayfeedback', -1.0)))
    msg.add_arg(float(kwargs.get('crush', 0.0)))
    msg.add_arg(int(kwargs.get('coarse', 0)))
    msg.add_arg(float(kwargs.get('hcutoff', 0.0)))
    msg.add_arg(float(kwargs.get('hresonance', 0.0)))
    msg.add_arg(float(kwargs.get('bandf', 0.0)))
    msg.add_arg(float(kwargs.get('bandq', 0.0)))
    msg = msg.build()
    dc[int(args[0])].send(msg)
    log.beat("sample: {}, out: {}".format(args[1] + ":" + str(args[2]), args[0]))
    

"""

Midi (Disklavier) function, midi with "collision detection":

If a node is already playing, don't play again.

This is important fpr disklavier compatiblity!

"""

midi.init()

midi_out = midi.Output(0,0)
midi_out.set_instrument(0)

def del_out():
    midi.quit()
    del midi_out

# make sure midi out is removed on program exit, to avoid pointer exception
atexit.register(del_out)

# naive note mutex
notes_on = {}

def disk(*args, **kwargs):
    """
    Function to output midi.

    Can be used with disklavier, as there won't be two notes played at the same time.
    """
    play_note = args[0]
    play_note.vel = args[2]
    play_note.absolute_duration = args[1]
    play_pitch = play_note.pitch.midi
    log.beat("playing: {}".format(play_pitch))
    if play_pitch not in notes_on:
        notes_on[play_pitch] = True
        midi_out.note_on(play_pitch, play_note.vel)
        pg_time.wait(play_note.absolute_duration)
        midi_out.note_off(play_pitch,play_note.vel)
        del notes_on[play_pitch]
    else:    
        log.action("MIDI fail, note already on!")


"""
Synthetic sounds, created with the ChucK backend ... so, yes, you need ChucK installed!
"""

# Collect shreds ...

# shreds = for file in listdir("./shreds"):

# Start chuck with respective shreds


# Client to send OSC stuff to ChucK 
chuck_client = dirt_client.UDPClient("127.0.0.1", 6449, 54442)

def sine(*args, **kwargs):
    """
    Play a sine wave (with ChucK).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))
    gain = gain * 0.46
    sus = args[1]
    attack = kwargs.get("a", 4);
    decay = kwargs.get("d", 2);
    release = kwargs.get("r", 4);
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("sine duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/sine")
    msg.add_arg(float(freq));
    msg.add_arg(gain);
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))        
    msg = msg.build()
    chuck_client.send(msg)
# end sine()


def subt(*args, **kwargs):    
    """
    Play a subtractive synth sound (with ChucK).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))
    gain = gain * 0.65
    sus = args[1]
    attack = kwargs.get("a", 4);
    decay = kwargs.get("d", 2);
    release = kwargs.get("r", 4);
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("sine duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/sub")
    msg.add_arg(float(freq));
    msg.add_arg(gain);
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))        
    msg = msg.build()
    chuck_client.send(msg)
# end sub()


def buzz(*args, **kwargs):
    """
    Play a buzz bass synth sound (with ChucK).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))
    gain = gain * 0.07
    sus = args[1]
    attack = kwargs.get("a", 4);
    decay = kwargs.get("d", 2);
    release = kwargs.get("r", 4);
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("sine duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/buzz")
    msg.add_arg(float(freq))
    msg.add_arg(gain)
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))        
    msg = msg.build()
    chuck_client.send(msg)
# end buzz()


