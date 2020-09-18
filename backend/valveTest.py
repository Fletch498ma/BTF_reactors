import time
from viciValve import ViciValve

seq = [2,3,4,1]
delta = 10000
experimentRun= True

def start():
    global v
    v = ViciValve()
    v.connect()
    v.setup()

def stop():
    v.reset()
    
def sequence(seq,delta):
    for i in seq:
        start()
        v.move(i)
        v.interpretPosition()
        stop()
        time.sleep(delta)
    
while experimentRun:
    sequence(seq,delta)