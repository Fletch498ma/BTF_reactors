import gasSensorCheck_dataCollection
from time import sleep

if __name__ == '__main__':
    
    while True:
        gasSensorCheck_dataCollection.ir_querie('span A')
        gasSensorCheck_dataCollection.ir_querie('span B')
        sleep(1)
        