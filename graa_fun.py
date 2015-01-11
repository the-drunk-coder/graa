import datetime, time
from pythonosc import osc_message_builder
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
    msg.add_arg(args[1] + ":" + args[2]) #sample name:number
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(1.0)
    msg.add_arg(1.0)
    msg.add_arg(0.5)
    msg.add_arg(0.0)
    msg.add_arg(kwargs.get('vowel', ' '))
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0)
    msg.add_arg(1.0)
    msg.add_arg(0)
    msg.add_arg(0.0)
    msg.add_arg(-1.0)
    msg.add_arg(-1.0)
    msg.add_arg(0.0)
    msg.add_arg(0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg = msg.build()
    dc[int(args[0])].send(msg)
    print("sample: {}, out: {}".format(args[1] + ":" + args[2], args[0]), file=outfile, flush=True)
    
