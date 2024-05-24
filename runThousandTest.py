import sys
import subprocess

for instance in range(1000) :
    subprocess.check_call(['python','testServer.py'],\
            stdout=sys.stdout, stderr=subprocess.STDOUT)