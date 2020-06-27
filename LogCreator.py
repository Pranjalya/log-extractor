import os
from datetime import datetime 
import random
import time

for i in range(600):
    for j in range(20000):
        with open('logs/LogFile'+'{:06}'.format(i)+'.log', 'a+') as f:
            f.write((datetime.now().isoformat()+", "+str(random.randint(0, 1566266))+", "+str(random.randint(0, 15665)))+"\n")
