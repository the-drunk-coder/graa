import datetime, time
from pythonosc import osc_message_builder
from graa_logger import GraaLogger as log
import dirt_client

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

outfile = open("out", "a")

#iisffffffsffffififfff

def dirt(*args, **kwargs):   
    msg = osc_message_builder.OscMessageBuilder(address = "/play")
    msg.add_arg(int(time.time()))
    msg.add_arg(datetime.datetime.now().microsecond)
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

if a node is already playing, dont play again 

"""
