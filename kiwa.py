import socket
import time
import json
import schedule
import sounddevice as sd
import numpy as np

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.settimeout(0.2)

def createMessage(intensity):
    '''
    Create bytearray json message for lamp with intensity between 0-100%
    '''

    message = { "op_code":"set_itshe",
                "timestamp":time.time(),
                "itshe":{
                    'i':intensity/100,
                    't':(5600-1500)/8500,
                    's':0,
                    'h':0,
                    'e':0}}

    message = json.dumps(message)
    messageB = bytearray()
    messageB.extend(map(ord,message))
    return messageB

def sendColor(indata, outdata, frames, time, status):
    vol_norm1=np.linalg.norm(indata[0])*200
    vol_norm2=np.linalg.norm(indata[1])*200
    schedule.run_pending()
    msg1 = createMessage(vol_norm1-20)
    msg2 = createMessage(vol_norm2-20)
    server.sendto(msg1, ('192.168.2.2',30001))
    server.sendto(msg2, ('192.168.2.190',30001))
    sd.sleep(50)

with sd.Stream(callback=sendColor):
    while 1:
        pass
    #sd.sleep(20 * 1000)
