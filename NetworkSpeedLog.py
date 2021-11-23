import subprocess
import re
from pathlib import Path
from datetime import datetime
import os
import os.path
import time
import sys

def main():

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

    # windows and linux have different arguments to ping
    if os.name == 'nt':
        fid.write(f'timestamp,cmdfailure,parsefailure,received(%),lost(%),average(ms)\n')
        cmd = ['ping','-n',str(npings),'-w',str(1000*timeout),host]
    else:
        fid.write(f'timestamp,cmdfailure,parsefailure,received(%),lost(%),average(ms),total(ms)\n')
        cmd = ['ping','-c',str(npings),'-w',str(timeout*npings),host]


    while True:
        now = datetime.now()
        cmdtime = now.strftime(timecode)
        res = subprocess.run(cmd,capture_output=True)
        cmdfailure = 1
        parsefailure = 0
        received = 0
        lost = 0
        average = float('nan')
        total = float('nan')
        if res.returncode == 0:
            cmdfailure = 0

            # windows and linux have different ping outputs
            if os.name == 'nt':
                m = re.search(r'Received = (\d+).*Lost = (\d+).*Average = ((\d|\.)+)ms',res.stdout.decode("utf-8"), re.DOTALL )
                if m is None:
                    parsefailure = 1
                else:
                    received = float(m.groups()[0])/float(npings)*100.
                    lost = float(m.groups()[1])/float(npings)*100.
                    average = float(m.groups()[2])
                fid.write(f'{cmdtime},{cmdfailure},{parsefailure},{received},{lost},{average}\n')
            else:
                m = re.search(r' (\d+) received.* (\d+)% packet loss, time ([\d\.]+)ms.*mdev = [^/]*/([^/]*)/', res.stdout.decode("utf-8"), re.DOTALL)
                if m is None:
                    parsefailure = 1
                else:
                    received = float(m.groups()[0])/float(npings)*100.
                    lost = float(m.groups()[1])
                    total = float(m.groups()[2])
                    average = float(m.groups()[3])

                fid.write(f'{cmdtime},{cmdfailure},{parsefailure},{received},{lost},{average},{total}\n')
        fid.flush()
        time.sleep(sleeptime)

    fid.close()

if __name__ == '__main__':
    main()
