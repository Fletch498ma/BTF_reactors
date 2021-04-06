import time
from viciValve import ViciValve

seq = [1,5,2,6,3,7,4,8]
delta = 120
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