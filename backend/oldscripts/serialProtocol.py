try:
    import serial
except ImportError:
    pass

class SerialProtocol(object):
    """Python driver for SGX Sensortech EK2 and EK3 gas sensor evaluation kit circuit boards. 
    
    Driver connects with the EK2 and EK3 on-board microcontrollers using USB or RS-232 connections and communicates via Pyserial.
    Ascii command protocols from product data sheets are used to gather data and communicate with the gas sensor microcontrollers.
    
    [Reference]
    EK2: https://www.sgxsensortech.com/content/uploads/2014/08/DS-0186-IR-EK2-Datasheet-V2.pdf
    EK3: https://www.sgxsensortech.com/content/uploads/2014/07/DS-0238-ECVQ-EK3-Datasheet-V1.pdf
    Pyserisal: https://pypi.org/project/pyserial/
    
    """
    
    def __init__(self,commConfig):
        self.commConfig = commConfig
        self.port_state = False    
        
    def connect(self):
        while not self.port_state:
            try:
                self.serialP = serial.Serial(**self.commConfig)
                if self.serialP.is_open:
                    self.port_state = True
                    chkport = "true"
                else:
                    ckcport = "false"
                print("\nSerial port " +self.commConfig["port"] + " is open: " +chkport+"\n")
            except:
                print("Waiting to open "+self.commConfig["port"] + " ...\n")
                time.sleep(1) #delay for 1 second and wait for port to be open
        
        self.resetSensor()

    def readlineR(self,delim):
        line = ""
        start = time()
        waiting = True
        while(waiting):
            if self.serialP.in_waiting: 
                c = str(self.serialP.read(1),'utf-8')
                line = line + c
                waiting = not line.endswith(delim)
                start = time()
            else:
                sleep(1.0/self.serialP.baudrate)
                waiting = time()-start < self.serialP.timeout
                if not waiting: line = None
        return line
    
    
    
    def flush(self):#changed from clearBuffer
        start = time()
        waiting = True
        while(waiting):
            if self.serialP.in_waiting>0: 
                waiting = time()-start < ser.timeout
                self.serialP.read(ser.in_waiting)
                self.serialP.reset_input_buffer()
                self.serialP.reset_output_buffer()
                sleep(1)
            else:
                waiting = False
             
    def resetSensor(self):
        pass
    
    """TODO: create checksum to ensure what is sent is receieved over sieral connection
    (reference checksum protocol for SGX Sensortech new INIR sensors: https://www.sgxsensortech.com/content/uploads/2016/06/USG_INIR-Evaluation-Software_V3.pdf)"""
    def checkSum(self):
        pass
