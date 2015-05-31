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
    msg.add_arg(0)
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
        pg_time.wait(int(play_note.absolute_duration))
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
    #gain = gain * 0.46
    sus = args[1]
    attack = kwargs.get("a", max(4, min(50, sus*0.25)));
    decay = kwargs.get("d", 0);
    release = kwargs.get("r", max(4, min(50, sus*0.1)));
    rev = kwargs.get("rev", 0.0)
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
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
    msg.add_arg(float(rev))
    msg.add_arg(pan)
    msg = msg.build()
    chuck_client.send(msg)
# end sine()

def nois(*args, **kwargs):
    """
    Play a white noise (with ChucK).
    """    
    gain = float(kwargs.get("gain", 0.5))    
    sus = args[0]
    attack = kwargs.get("a", max(4, min(50, sus*0.25)));
    decay = kwargs.get("d", 0);
    release = kwargs.get("r", max(4, min(50, sus*0.1)));
    rev = kwargs.get("rev", 0.0)
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("nois duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/nois")
    msg.add_arg(gain);
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))        
    msg.add_arg(float(rev))
    msg.add_arg(pan)
    msg = msg.build()
    chuck_client.send(msg)
# end noiz()

def grain(*args, **kwargs):
    """
    Play a grain from a sample (with ChucK).
    """
    path = str(args[0])
    start = float(args[1])
    length = int(args[2])
    gain = float(kwargs.get("gain", 0.5))
    speed = float(kwargs.get("speed", 1.0))          
    rev = float (kwargs.get("rev", 0.0))    
    msg = osc_message_builder.OscMessageBuilder(address = "/grain")
    msg.add_arg(path)
    msg.add_arg(start)
    msg.add_arg(length)
    msg.add_arg(gain)
    msg.add_arg(speed)        
    msg.add_arg(rev)    
    msg = msg.build()
    chuck_client.send(msg)
# end grain()

def grainB(*args, **kwargs):
    """
    Play a grain from a sample (with ChucK).
    """
    path = str(args[0])
    start = float(args[1])
    length = int(args[2])
    gain = float(kwargs.get("gain", 0.5))
    speed = float(kwargs.get("speed", 1.0))          
    rev = float (kwargs.get("rev", 0.0))    
    msg = osc_message_builder.OscMessageBuilder(address = "/grainb")
    msg.add_arg(path)
    msg.add_arg(start)
    msg.add_arg(length)
    msg.add_arg(gain)
    msg.add_arg(speed)        
    msg.add_arg(rev)    
    msg = msg.build()
    chuck_client.send(msg)
# end grainB()

def grainC(*args, **kwargs):
    """
    Play a grain from a sample (with ChucK).
    """
    path = str(args[0])
    start = float(args[1])
    length = int(args[2])
    gain = float(kwargs.get("gain", 0.5))
    speed = float(kwargs.get("speed", 1.0))          
    rev = float (kwargs.get("rev", 0.0))    
    msg = osc_message_builder.OscMessageBuilder(address = "/grainc")
    msg.add_arg(path)
    msg.add_arg(start)
    msg.add_arg(length)
    msg.add_arg(gain)
    msg.add_arg(speed)        
    msg.add_arg(rev)    
    msg = msg.build()
    chuck_client.send(msg)
# end grainC()

def grainD(*args, **kwargs):
    """
    Play a grain from a sample (with ChucK).
    """
    path = str(args[0])
    start = float(args[1])
    length = int(args[2])
    gain = float(kwargs.get("gain", 0.5))
    speed = float(kwargs.get("speed", 1.0))          
    rev = float (kwargs.get("rev", 0.0))    
    msg = osc_message_builder.OscMessageBuilder(address = "/graind")
    msg.add_arg(path)
    msg.add_arg(start)
    msg.add_arg(length)
    msg.add_arg(gain)
    msg.add_arg(speed)        
    msg.add_arg(rev)    
    msg = msg.build()
    chuck_client.send(msg)
# end grainD()


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
    sus = args[1]
    attack = kwargs.get("a", max(4, min(50, sus*0.25)));
    decay = kwargs.get("d", 0);
    release = kwargs.get("r", max(4, min(50, sus*0.1)));
    rev = kwargs.get("rev", 0.0)
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("subt duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/sub")
    msg.add_arg(float(freq));
    msg.add_arg(gain);
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))
    msg.add_arg(float(rev));
    msg.add_arg(pan);
    msg = msg.build()
    chuck_client.send(msg)
# end subt()


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
    sus = args[1]
    attack = kwargs.get("a", max(4, min(30, sus*0.1)));
    decay = kwargs.get("d", max(4, min(30, sus*0.25)));
    release = kwargs.get("r", max(4, min(50, sus*0.1)));    
    sus = sus - attack - decay - release
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", 1.0)
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
    if sus <= 0:
        log.action("sine duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/buzz")
    #print("f {} g {} a {} d {} s {} r {}".format(freq, gain, attack, decay, sus, release))
    msg.add_arg(float(freq))
    msg.add_arg(gain)
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))
    msg.add_arg(float(rev))
    msg.add_arg(float(cutoff))
    msg.add_arg(pan)
    msg = msg.build()
    chuck_client.send(msg)
# end buzz()


def sqr(*args, **kwargs):
    """
    Play a square wave synth sound (with ChucK).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))    
    sus = args[1]
    attack = kwargs.get("a", max(4, min(30, sus*0.1)));
    decay = kwargs.get("d", max(4, min(30, sus*0.25)));
    release = kwargs.get("r", max(4, min(50, sus*0.1)));    
    sus = sus - attack - decay - release
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", 1.0)
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
    if sus <= 0:
        log.action("sine duration too short!")
    msg = osc_message_builder.OscMessageBuilder(address = "/sqr")
    #print("f {} g {} a {} d {} s {} r {}".format(freq, gain, attack, decay, sus, release))
    msg.add_arg(float(freq))
    msg.add_arg(gain)
    msg.add_arg(int(attack))
    msg.add_arg(int(decay))
    msg.add_arg(int(sus))
    msg.add_arg(int(release))
    msg.add_arg(float(rev))
    msg.add_arg(float(cutoff))
    msg.add_arg(pan) 
    msg = msg.build()
    chuck_client.send(msg)
# end sqr()


def say(*args, **kwargs):
    text = args[0]
    gain = kwargs.get("gain", 0.6)
    speed = kwargs.get("speed", 140)
    amp = 100 * gain
    command = "espeak -s{} -a{} --stdout \"{}\" | aplay -q" .format(int(speed), int(amp), text)
    os.system(command)
# end say()    

