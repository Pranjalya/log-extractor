import os
import sys
import argparse
import subprocess
import time
import dateutil.parser
import linecache
import mmap

def fileLinecount(filename):
    out = subprocess.Popen(['wc', '-l', filename],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT
                         ).communicate()[0]
    return int(out.partition(b' ')[0])

def getTail(filename, n):
    """Returns last n lines from the filename. No exception handling"""
    size = os.path.getsize(filename)
    with open(filename, "r") as f:
        # for Windows the mmap parameters are different, so set them according to system
        fm = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
        try:
            for i in range(size - 1, -1, -1):
                if fm[i] == '\n':
                    n -= 1
                    if n == -1:
                        break
            return fm[i + 1 if i else 0:].splitlines()
        finally:
            fm.close()

def getLine(file:str, stamp, loc) -> int:
    left = 1
    right = fileLinecount(loc+"/"+file)
    last = right

    # To check if our stamp is lesser than the first stamp
    if(stamp < dateutil.parser.parse(linecache.getline(loc+"/"+file, 1).split(",")[0])):
        return 1

    # Binary Search for the starting stamp just greater than given stamp
    while left <= right:
        mid = left + (right-left)//2
        if mid==1 or mid==last:
            return mid
        else:
            stmtmid = "sed '{}p;{}p;{}q;d' log/{}".format(mid-1, mid, mid+1, file)
            midstamps = subprocess.run(stmtmid.split(), stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8').split('\n')
            midstamps = list(map(lambda x: dateutil.parser.parse(x.split(",")[0]), midstamps[:3]))
            if(stamp >= midstamps[1] and stamp<=midstamps[2]):
                return mid
            elif(stamp<=midstamps[1] and stamp>=midstamps[0]):
                return mid
            else:
                if(stamp>midstamps[1]):
                    left = mid+1
                else:
                    right = mid-1


def showLogs(startfile:str, endfile:str, start, end, loc:str) -> None:
    startline = getLine(startfile, start, loc)
    endline = getLine(endfile, end, loc)

    startlinecount = fileLinecount(loc+"/"+startfile)
    
    # Display last total lines - initial stamp line lines
    print(getTail(loc+"/"+startfile, startlinecount-startline))

    # Display all lines of files between start file and end file
    for fileno in range(int(startfile[7:13])+1, int(endfile[7:13])):
        with open(loc+"/LogFile{}.log".format(fileno)) as fi:
            print(fi.readline())
    
    # Display first lines of end file
    print(linecache.getline(loc+endfile, endline))
    

def getLogs(start:str, end:str, loc:str) -> None:
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    startfile = ''
    endfile = ''

    if(start > end):
        raise ArithmeticError

    startfound = False
    for f in os.listdir(loc):
        head = linecache.getline(loc+"/"+f, 1).split(",")[0]
        tail = getTail(loc+"/"+f, 1)[0].split(",")[0]
        header = dateutil.parser.parse(head)
        tailer = dateutil.parser.parse(tail)
        if(not startfound and tailer >= start):
            print("Head : ", head, " Tail : ", tail, "")
            startfile = f
            startfound = True
        if(tailer >= end):
            print("Head : ", head, " Tail : ", tail, "")
            endfile = f
            break
    
    showLogs(startfile, endfile, start, end, loc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        type=str,
        help='Starting timestamp for extraction of file'
    )
    parser.add_argument(
        '-t',
        type=str,
        help='Ending timestamp for extraction of file'
    )
    parser.add_argument(
        '-i',
        type=str,
        help='Location of directory containing logs'
    )

    args = parser.parse_args()
    start = time.perf_counter()
    getLogs(start=args.f, end=args.t, loc=args.i)
    print("Time elapsed for open() : ", time.perf_counter() - start)