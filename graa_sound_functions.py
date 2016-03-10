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
    play_note.vel = int(127.0 * kwargs.get("gain", 0.5))
    play_note.absolute_duration = kwargs.get("length", 100)
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
Synthetic sounds, created with the SC3 backend ... so, yes, you need SuperCollider installed!
"""


# Client to send OSC stuff to SCSynth 
scsynth_client = dirt_client.UDPClient("127.0.0.1", 57110, 54442)

scsynth_client.sendMsg("/g_new", 1, 0, 0)

def sine(*args, **kwargs):
    """
    Play a sine wave (with SCSynth).
    """
    # Gather % Process Information
    freq = None
    if type(args[0]) is gnote:
        freq = float(args[0].pitch.frequency)
    else:
        freq = float(args[0] )
    gain = float(kwargs.get("gain", 0.5))
    sus = kwargs.get("length", 100) 
    attack = float(kwargs.get("a", max(4, min(50, sus*0.25))) / 1000)
    decay = float(kwargs.get("d", 5) / 1000)
    release = float(kwargs.get("r", max(4, min(50, sus*0.1))) / 1000)
    rev = float(kwargs.get("rev", 0.0))
    synth_name = "sine"
    if(rev > 0.0):
        synth_name = "sinerev"
    pan = kwargs.get("pan", 0.5)
    pan = float((pan * 2) - 1) 
    sus = float((sus - attack - decay - release) / 1000)   
    if sus <= 0:
        log.action("sine duration too short!")
    # send message
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "freq", freq, "gain", gain, "a", attack, "d", decay, "s", sus, "r", release, "rev", rev, "pan", pan)
# end sine()

def nois(*args, **kwargs):
    """
    Play a white noise (with SC).
    """    
    gain = float(kwargs.get("gain", 0.5))    
    sus = kwargs.get("length", 100)
    attack = kwargs.get("a", max(4, min(50, sus*0.25)));
    decay = kwargs.get("d", 0);
    release = kwargs.get("r", max(4, min(50, sus*0.1)));
    rev = kwargs.get("rev", 0.0)
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("nois duration too short!")
    synth_name = "noise"
    if(rev > 0.0):
        synth_name = "noiserev"
    # send message
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "gain", gain, "a", attack, "d", decay, "s", sus, "r", release, "rev", rev, "pan", pan)
# end noiz()

# dict mapping samplename to bufnum
class sampl_info:
    graa_samples = {}
    sample_root = "/home/nik/REPOSITORIES/graa/samples"
    bufnum = 0

def free_samples():
    for sample in sampl_info.graa_samples:
        scsynth_client.sendMsg("/b_free", sampl_info.graa_samples[sample])

atexit.register(free_samples)

def sampl(*args, **kwargs):
    """
    Play a sample or a part of it (with SC).
    """
    folder = str(args[0])
    name = str(args[1])
    sample_id = folder + ":" + name
    speed = float(kwargs.get("speed", 1.0))
    rev = float(kwargs.get("rev", 0.0))
    pan = float((kwargs.get("pan", 0.5) * 2) - 1)
    cutoff = float(kwargs.get("cutoff", 20000))
    gain = float(kwargs.get("gain", 1.0))
    start = float(kwargs.get("start", 0.0))
    a_ms = kwargs.get("a", 4)
    r_ms = kwargs.get("r", 4)
    l_ms = kwargs.get("length", 0) - a_ms - r_ms
    #print("a: " + str(a_ms) + " l: " + str(l_ms) + " r: " + str(r_ms)) 
    release = float(r_ms / 1000)
    attack = float(a_ms / 1000)
    length = float(l_ms / 1000)
    #print("a sc: " + str(attack) + " l sc: " + str(length) + " r sc: " + str(release)) 
    if rev > 0.0:
        if length > 0.0:
            synth_name="grainrev"
        else:
            synth_name="samplrev"
    else:
        if length > 0.0:
            synth_name="grain"
        else:
            synth_name="sampl"
    #print(synth_name + ":" + str(length))
    if sample_id not in sampl_info.graa_samples:
        sample_path = sampl_info.sample_root + "/" + folder + "/" + name + ".wav"
        # create buffer on scsynth
        scsynth_client.sendMsg("/b_allocRead", sampl_info.bufnum, sample_path)
        sampl_info.graa_samples[sample_id] = sampl_info.bufnum
        sampl_info.bufnum += 1
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "bufnum", sampl_info.graa_samples[sample_id], "speed", speed, "rev", rev, "pan", pan, "cutoff", cutoff, "gain", gain, "start", start, "length", length, "a", attack, "r", release)
# end sampl()

def sampl8ch(*args, **kwargs):
    """
    Play a sample or a part of it (with SC), with 8-Channel panning
    """
    folder = str(args[0])
    name = str(args[1])
    sample_id = folder + ":" + name
    speed = float(kwargs.get("speed", 1.0))
    rev = float(kwargs.get("rev", 0.0))
    pan = float((kwargs.get("pan", 0.0)))
    #print(pan)
    cutoff = float(kwargs.get("cutoff", 20000))
    gain = float(kwargs.get("gain", 1.0))
    start = float(kwargs.get("start", 0.0))
    length = float(kwargs.get("length", 0) / 1000)
    if rev > 0.0:
        if length > 0.0:
            synth_name="grain8rev"
        else:
            synth_name="sampl8rev"
    else:
        if length > 0.0:
            synth_name="grain8"
        else:
            synth_name="sampl8"
    #print(synth_name + ":" + str(length))
    if sample_id not in sampl_info.graa_samples:
        sample_path = sampl_info.sample_root + "/" + folder + "/" + name + ".wav"
        # create buffer on scsynth
        scsynth_client.sendMsg("/b_allocRead", sampl_info.bufnum, sample_path)
        sampl_info.graa_samples[sample_id] = sampl_info.bufnum
        sampl_info.bufnum += 1
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "bufnum", sampl_info.graa_samples[sample_id], "speed", speed, "rev", rev, "pan", pan, "cutoff", cutoff, "gain", gain, "start", start, "length", length)
# end sampl()


def subt(*args, **kwargs):    
    """
    Play a subtractive synth sound (with SC).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))
    sus = kwargs.get("length", 100)
    attack = kwargs.get("a", max(4, min(50, sus*0.25)));
    decay = kwargs.get("d", 0);
    release = kwargs.get("r", max(4, min(50, sus*0.1)));
    rev = kwargs.get("rev", 0.0)
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    sus = sus - attack - decay - release
    if sus <= 0:
        log.action("subt duration too short!")
    synth_name = "subt"
    if(rev > 0.0):
        synth_name = "subtrev"
    # send message
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "gain", gain, "a", attack, "d", decay, "s", sus, "r", release, "rev", rev, "pan", pan) 
# end subt()


def buzz(*args, **kwargs):
    """
    Play a buzz bass synth sound (with SC).
    """  
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))    
    sus = kwargs.get("length", 100)
    attack = kwargs.get("a", max(4, min(30, sus*0.1))) / 1000
    decay = kwargs.get("d", max(4, min(30, sus*0.25))) / 1000
    release = kwargs.get("r", max(4, min(50, sus*0.1))) / 1000
    sus = (sus - attack - decay - release) / 1000
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", freq)
    if type(cutoff) is gnote:
        cutoff = cutoff.pitch.frequency
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    if sus <= 0:
        log.action("sine duration too short!")    
    if rev > 0.0:
        synth_name="buzzrev"
    else:
        synth_name="buzz"    
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "freq", freq, "gain", gain, "a", attack, "d", decay, "s", sus, "r", release, "rev", rev, "pan", pan, "cutoff", cutoff)
# end buzz()


def sqr(*args, **kwargs):
    """
    Play a sqr bass synth sound (with SC).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.5))    
    sus = kwargs.get("length", 100)
    attack = kwargs.get("a", max(4, min(30, sus*0.1))) / 1000
    decay = kwargs.get("d", max(4, min(30, sus*0.25))) / 1000
    release = kwargs.get("r", max(4, min(50, sus*0.1))) / 1000
    sus = (sus - attack - decay - release) / 1000
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", freq)
    if type(cutoff) is gnote:
        cutoff = cutoff.pitch.frequency
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    if sus <= 0:
        log.action("sine duration too short!")
    if rev > 0.0:
        synth_name="sqrrev"
    else:
        synth_name="sqr"    
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "freq", freq, "gain", gain, "a", attack, "d", decay, "s", sus, "r", release, "rev", rev, "pan", pan, "cutoff", cutoff)
# end sqr()

def risset(*args, **kwargs):
    """
    Play a risset bell synth sound (with SC).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.1) / 10)    
    sus = kwargs.get("length", 200) / 1000
    #attack = kwargs.get("a", max(4, min(30, sus*0.1))) / 1000
    #decay = kwargs.get("d", max(4, min(30, sus*0.25))) / 1000
    #release = kwargs.get("r", max(4, min(50, sus*0.1))) / 1000
    #sus = (sus - attack - decay - release) / 1000
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", freq)
    if type(cutoff) is gnote:
        cutoff = cutoff.pitch.frequency
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    if sus <= 0:
        log.action("bell duration too short!")
    if rev > 0.0:
        synth_name="rissetrev"
    else:
        synth_name="risset"    
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "freq", freq, "gain", gain, "length", sus, "rev", rev, "pan", pan, "cutoff", cutoff)
# end risset()

def pluck(*args, **kwargs):
    """
    Play a karplus strong pluck synth sound (with SC).
    """
    freq = None
    if type(args[0]) is gnote:
        freq = args[0].pitch.frequency
    else:
        freq = args[0]    
    gain = float(kwargs.get("gain", 0.1) * 0.9)    
    sus = kwargs.get("length", 200) / 1000
    #attack = kwargs.get("a", max(4, min(30, sus*0.1))) / 1000
    #decay = kwargs.get("d", max(4, min(30, sus*0.25))) / 1000
    #release = kwargs.get("r", max(4, min(50, sus*0.1))) / 1000
    #sus = (sus - attack - decay - release) / 1000
    rev = kwargs.get("rev", 0.0)
    cutoff = kwargs.get("cutoff", freq)
    if type(cutoff) is gnote:
        cutoff = cutoff.pitch.frequency
    pan = float((kwargs.get("pan", 0.5) * 2) - 1) 
    if sus <= 0:
        log.action("pluck duration too short!")
    if rev > 0.0:
        synth_name="pluckrev"
    else:
        synth_name="pluck"    
    scsynth_client.sendMsg("/s_new", synth_name, -1, 0, 1, "freq", freq, "gain", gain, "length", sus, "rev", rev, "pan", pan, "cutoff", cutoff)
# end pluck()



def say(*args, **kwargs):
    text = args[0]
    gain = kwargs.get("gain", 0.6)
    speed = kwargs.get("speed", 140)
    amp = 100 * gain
    command = "espeak -s{} -a{} --stdout \"{}\" | aplay -q" .format(int(speed), int(amp), text)
    os.system(command)
# end say()    

