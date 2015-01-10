import datetime, time
from pythonosc import osc_message_builder, udp_client

dirt_client = udp_client.UDPClient("127.0.0.1", 7771)

outfile = open("out", "a")

#iisffffffsffffififfff

def dirt(name):
    msg = osc_message_builder.OscMessageBuilder(address = "/play")
    msg.add_arg(int(time.time()))
    msg.add_arg(datetime.datetime.now().microsecond)
    msg.add_arg(name + ":3")
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(1.0)
    msg.add_arg(1.0)
    msg.add_arg(0.5)
    msg.add_arg(0.0)
    msg.add_arg(" ")
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(0.0)
    msg.add_arg(1)
    msg.add_arg(1.0)
    msg.add_arg(1)
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
    dirt_client.send(msg)
    print("Yet playing sample: {}".format(name), file=outfile, flush=True)
    
