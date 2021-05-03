import socket
import time
import json
import sounddevice as sd
import numpy as np

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.settimeout(0.002)

listA = [
'192.168.1.67',
'192.168.1.56',
'192.168.1.73',
'192.168.1.60',
'192.168.1.38',
'192.168.1.49',
'192.168.1.44',
'192.168.1.58',
'192.168.1.74',
'192.168.1.51',
'192.168.1.69',
'192.168.1.41',
'192.168.1.72'
]

listB = [
'192.168.1.71',
'192.168.1.75',
'192.168.1.47',
'192.168.1.16',
'192.168.1.23',
'192.168.1.89',
'192.168.1.64',
'192.168.1.46',
'192.168.1.66',
'192.168.1.45',
'192.168.1.65'
]

nextUpdate = time.time()

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

def updateColor(indata):

    vol_norm1=np.linalg.norm(indata[0])
    vol_norm2=np.linalg.norm(indata[1])
    msg1 = createMessage(vol_norm1*200-20)
    msg2 = createMessage(vol_norm2*200-20)

    for lampIp in listA:
         server.sendto(msg1, (lampIp,30001))

    for lampIp in listB:
        server.sendto(msg2, (lampIp,30001))



def streamEvent(indata, outdata, frames, ltime, status):
    global nextUpdate


    currentTime = time.time()
    if currentTime < nextUpdate:
        time.sleep(0.1)
        return

    nextUpdate = currentTime + 0.1
    updateColor(indata)


with sd.Stream(callback=streamEvent):
    while 1:
        pass
    #sd.sleep(20 * 1000)
