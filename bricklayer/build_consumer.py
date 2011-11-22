import sys
import os
import bricklayer
import signal
sys.path.append(os.path.join(os.path.dirname(bricklayer.__file__), 'utils'))
sys.path.append(os.path.dirname(bricklayer.__file__))

from bricklayer.builder import build_project
from bricklayer.config import BrickConfig
from pyres.worker import Worker
from multiprocessing import Process

def main():
    global worker_num
    if os.path.isdir('/var/run'):
        pidfile = open('/var/run/build_consumer.pid', 'w')
        pidfile.write(str(os.getpid()))
        pidfile.close()
    brickconfig = BrickConfig()
    
    Worker.run(['build'], brickconfig.get('redis', 'redis-server'))

if __name__ == "__main__":
    main()
