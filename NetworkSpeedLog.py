import subprocess
import re
from pathlib import Path
from datetime import datetime
import os
import os.path
import time

def main():

    timecode = '%Y%m%dT%H%M%S.%f'
    npings = 10
    timeout = 5000 # ms
    host = 'login1.int.janelia.org'
    sleeptime = 10 # s

    home = str(Path.home())
    now = datetime.now()
    starttime = now.strftime('%Y%m%dT%H%M%S')
    outfile = os.path.join(home,f'NetworkSpeedLog{starttime}.csv')
    fid = open(outfile,'w')
    cmd = f'ping -n {npings} -w {timeout} {host}'


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
            m = re.search(r'Received = (\d+).*Lost = (\d+).*Average = ((\d|\.)+)ms',res.stdout.decode("utf-8"), re.DOTALL )
            cmdfailure = 0
            if m is None:
                parsefailure = 1
            else:
                received = int(m.groups()[0])
                lost = int(m.groups()[1])
                average = float(m.groups()[2])

        fid.write(f'{cmdtime},{cmdfailure},{parsefailure},{received},{lost},{average}\n')
        fid.flush()
        time.sleep(sleeptime)

    fid.close()

if __name__ == '__main__':
    main()
