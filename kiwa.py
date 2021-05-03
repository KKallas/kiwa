import socket
import time
import json
import sounddevice as sd
import numpy as np

import os
from multiprocessing import Process, Pipe

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

    return json.dumps(message).encode()

class NetworkSender():
    def __init__(self, networking_pipe):
        self.networking_pipe = networking_pipe
        self.server = None # Is initialized later in execNetworkingProcess (in another process)
        self.networking_process = Process(target=self.execNetworkingProcess, args=(networking_pipe_parent, ))
        self.last_write_time = time.time()

        self.listA = [
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
        '192.168.1.72',
        #new
        '192.168.1.40',
        '192.168.1.77',
        '192.168.1.61',
        '192.168.1.54',
        '192.168.1.62',
        '192.168.1.39'
        ]

        self.listB = [
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
        '192.168.1.65',
        #new
        '192.168.1.43',
        '192.168.1.52'
        ]

    def start(self):
        self.networking_process.start()

    def join(self):
        self.networking_process.join()

    # Is called from another process
    def handleNetworkingData(self, v1, v2):
        msg1 = createMessage(v1)
        msg2 = createMessage(v2)

        try:
            for lampIp in self.listA:
                self.server.sendto(msg1, (lampIp,30001))

            for lampIp in self.listB:
                self.server.sendto(msg2, (lampIp,30001))
        except:
            pass


    # Main loop of another process
    def execNetworkingProcess(self, networking_pipe):
        # Init socket in other process
        self.server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(0.002)

        while(True):
            (v1, v2) = networking_pipe.recv()
            self.handleNetworkingData(v1, v2)

def updateColor(indata):

    vol_norm1=np.linalg.norm(indata[0])
    vol_norm2=np.linalg.norm(indata[1])

    networking_pipe_child.send((vol_norm1*200-20, vol_norm2*200-20))



def streamEvent(indata, outdata, frames, frametime, status):
    '''
    global nextUpdate
    currentTime = time.time()
    if currentTime < nextUpdate:
        time.sleep(0.1)
        return

    nextUpdate = currentTime + 0.1
    '''
    updateColor(indata)
    sd.sleep(110)


if __name__ == '__main__':
    networking_pipe_parent, networking_pipe_child = Pipe()
    network_sender = NetworkSender(networking_pipe_parent)
    network_sender.start()

    with sd.Stream(callback=streamEvent):
        while 1:
            time.sleep(0.1) # Dont stress current core

    # Test pipe multiprocess delay
    # Delay was 5.00+ ms, very minimal. varied delay is introduced by sounddevice.
    # Delay was minimal with sd.sleep(1) => 20 - 30ms
    #while 1:
    #    time.sleep(0.005) # Dont stress current core
    #    networking_pipe_child.send((0, 1))
    #    pass

    network_sender.join()
