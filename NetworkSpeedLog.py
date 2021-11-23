# Requires Python3
# Makes a file in your home directory called NetworkSpeedLog<timestamp>.csv
# with ping timing information

import subprocess
import re
from pathlib import Path
from datetime import datetime
import os
import os.path
import time
import sys
import platform

def main():

    osname = platform.system
    
    timecode = '%Y%m%dT%H%M%S.%f'
    npings = 10
    timeout = 5 # s
    host = 'login1.int.janelia.org'
    sleeptime = 10 # s

    home = str(Path.home())
    now = datetime.now()
    starttime = now.strftime('%Y%m%dT%H%M%S')
    outfile = os.path.join(home,f'NetworkSpeedLog{starttime}.csv')
    fid = open(outfile,'w')

    fid.write(f'timestamp,cmdfailure,parsefailure,received(%),lost(%),average(ms)\n')
    # windows and linux have different arguments to ping
    if osname == 'Windows':
        cmd = ['ping','-n',str(npings),'-w',str(1000*timeout),host]
    elif osname == 'Darwin':
        cmd = ['ping','-c',str(npings),'-W',str(1000*timeout),host]
    else:
        cmd = ['ping','-c',str(npings),'-W',str(timeout*npings),host]


    while True:
        now = datetime.now()
        cmdtime = now.strftime(timecode)
        res = subprocess.run(cmd,capture_output=True)
        cmdfailure = 1
        parsefailure = 0
        received = 0
        lost = 0
        average = float('nan')
        if res.returncode == 0:
            cmdfailure = 0

            # windows and linux have different ping outputs
            if osname == 'Windows':
                m = re.search(r'Received = (\d+).*Lost = (\d+).*Average = ((\d|\.)+)ms',res.stdout.decode("utf-8"), re.DOTALL )
                if m is None:
                    parsefailure = 1
                else:
                    received = float(m.groups()[0])/float(npings)*100.
                    lost = float(m.groups()[1])/float(npings)*100.
                    average = float(m.groups()[2])
            else:
                m = re.search(r' (\d+) .*received.* ([\d\.]+)% packet loss.*dev = [^/]*/([^/]*)/', res.stdout.decode("utf-8"), re.DOTALL)
                if m is None:
                    parsefailure = 1
                else:
                    received = float(m.groups()[0])/float(npings)*100.
                    lost = float(m.groups()[1])
                    average = float(m.groups()[2])

        fid.write(f'{cmdtime},{cmdfailure},{parsefailure},{received},{lost},{average}\n')
        fid.flush()
        time.sleep(sleeptime)

    fid.close()

if __name__ == '__main__':
    main()
