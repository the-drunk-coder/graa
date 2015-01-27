"""

In this file, find the functions that actually trigger the sound generators.

graa doesn't use it's own sound generation, but different backends, as seen below.

"""
import datetime, time, threading, atexit
from pythonosc import osc_message_builder
from graa_logger import GraaLogger as log
import dirt_client
from pygame import midi
from pygame import time as pg_time 
from music21 import note

"""
Procedure to send an event to Alex McLean's marvellous dirt sample player!

The dirt player takes osc messages as input, via udp, on port 7771

Each source port is interpretad as a road to dirt ...

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

Disklavier function, midi with "collision detection":

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

# fire-and-forget midi note player, one plaer for each note
class NotePlayer():
    def __init__(self, a_note):        
        self.note_thread = threading.Thread(target=self.fire, args=(a_note, ))
        self.note_thread.deamon = True
        self.played = False
    def fire(self, a_note):
        try:
            midi_out.note_on(a_note.pitch.midi, a_note.vel)
            pg_time.wait(a_note.absolute_duration)
            midi_out.note_off(a_note.pitch.midi,a_note.vel)
            self.played = True
        except Exception as e:
            print(e)
    def play(self):
        self.note_thread.start()
        self.note_thread.join()
        

# dictionary to store note players
note_dict = {}

# play midi note and make sure each note is only played once, for disklavier compat
def disk(*args, **kwargs):    
    play_note = args[0]
    play_note.vel = args[2]
    play_note.absolute_duration = args[1]
    play_pitch = play_note.pitch.midi
    if play_pitch in note_dict and not note_dict[play_note.pitch.midi].played:
        log.action("Midi note {} already playing!")
        return
    note_dict[play_note.pitch.midi] = NotePlayer(play_note)
    note_dict[play_note.pitch.midi].play()
    
    
