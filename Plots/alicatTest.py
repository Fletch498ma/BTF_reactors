from alicat import FlowController
from time import sleep
import numpy as np
from termcolor import colored, cprint

port_bench = '/dev/ttyUSB3'
port_incubator = '/dev/ttyUSB4'

unitIDs_bench = {'A':'3%CO2 in Air','B':'2%CH4 in N2','C':'N2'}
unitIDs_incubator = {'D':'R4-CH4','E':'R1-CH4','F':'R2-CH4','G':'R3-CH4','H':'R2-CO2','I':'R1-CO2','J':'R4-CO2','K':'R3-CO2'}

#flow_controllers_bench = [FlowController(port=port_bench,address=unitID) for unitID in unitIDs_bench]
#flow_controllers_incubator = [FlowController(port=port_incubator,address=unitID) for unitID in unitIDs_incubator]
#
#flow_controllers = flow_controllers_bench + flow_controllers_incubator
#
#for inst in flow_controllers:
#    print(inst.get())
#
#for inst in flow_controllers:
#    inst.close()
    

flow_controller_1 = FlowController(port=port_bench,address='A') #3%CO2 in air MC0-5SCCM
flow_controller_2 = FlowController(port=port_bench,address='C') #N2 MC_2SLPM
flow_controller_3 = FlowController(port=port_bench,address='B') #4%CH4 in ch4 MC0-50SCCM

def init(address,port):
    return FlowController(port=port,address=address) #4%CH4 in ch4 MC0-50SCCM

def get_flow(flowInst):
    flow = flowInst.get()['mass_flow']
    print(flow)
    
    return flow
    
def hold(flowInst):
    fllowInst.hold()
    
#flow_controller_1.set_flow_rate(0)
#flow_controller_2.set_flow_rate(0)
#flow_controller_3.set_flow_rate(0)
#sleep(2)


#flow_controller_1.cancel_hold()
#flow_controller_2.cancel_hold()
#flow_controller_3.cancel_hold()
#
#flow_controller_1.hold()
#flow_controller_3.hold()
##flow_controller_1.set_gas(255)
##flow_controller_1.set_flow_rate(5)
#flow_controller_2.set_gas('N2')
#flow_controller_2.set_flow_rate(0.1)
#flow_controller_3.set_gas(255)
#flow_controller_3.set_flow_rate(50)
print(flow_controller_1.get())
print(flow_controller_2.get())
print(flow_controller_3.get())
try:
    input("Press Enter to Stop\n")
except (Exception, KeyboardInterrupt):
    pass

#print(flow_controller_3.get())
#
##sleep(10)
##flow_controller_1.set_flow_rate(0)
##flow_controller_2.set_flow_rate(0)
##flow_controller_3.set_flow_rate(0)
flow_controller_1.cancel_hold()
flow_controller_2.cancel_hold()
flow_controller_3.cancel_hold()
flow_controller_3.set_flow_rate(0)
flow_controller_3.set_gas('Air')
flow_controller_2.set_flow_rate(0)
flow_controller_2.set_gas('Air')
flow_controller_1.set_flow_rate(0)
flow_controller_1.set_gas('Air')
#flow_controller_1.cancel_hold()
#flow_controller_2.cancel_hold()
#flow_controller_1.hold()
#flow_controller_2.hold()
#flow_controller_3.hold()
flow_controller_1.close() #/dev/ttyUSB3 is still open!
flow_controller_2.close()
flow_controller_3.close()

try:
    input(cprint("\n****** Close Valve!!!! ******\n Press ENTER when valve closed\n",'red',attrs=['reverse','blink']))
except (Exception, KeyboardInterrupt):
    pass

#flow_controller_3.close()