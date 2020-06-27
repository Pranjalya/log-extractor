import os
import sys
import argparse
import subprocess
import time
import dateutil.parser

def getLine(file:str, stamp, loc) -> int:
    '''

    '''
    linecounter = 'wc -l logs/{}'.format(file)
    left = 1
    right = int(subprocess.run(linecounter.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0])
    last = right

    # To check if our stamp is lesser than the first stamp
    stmt = 'head -n 1 logs/{}'.format(file)
    if(stamp < dateutil.parser.parse(subprocess.run(stmt.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0])):
        return 1

    # Binary Searching for the starting stamp just greater than given stamp
    while left <= right:
        mid = left + (right-left)//2
        if mid==1 or mid==last:
            return mid
        else:
            stmtmid = "sed '{}p;{}p;{}q;d' log/{}".format(mid-1, mid, mid+1, file)
            midstamps = subprocess.run(stmtmid.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
            midstamps = list(map(lambda x: dateutil.parser.parse(x.split()[0]), midstamps[:3]))
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

    startlinecounter = 'wc -l {}/{}'.format(loc, startfile)
    endlinecounter = 'wc -l {}/{}'.format(loc, endfile)

    startlinecount = int(subprocess.run(startlinecounter.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0])
    endlinecount = int(subprocess.run(endlinecounter.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0])
    
    # Display last total lines - initial stamp line lines
    cmd = 'tail -n {} {}/{}'.format(startlinecounter-startlinecount+1, loc, startfile)
    os.system(cmd)

    ## TO DO : Extract no and show all in between

def getLogs(start:str, end:str, loc:str) -> None:
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    startfile = ''
    endfile = ''

    if(start > end):
        raise ArithmeticError

    for f in os.listdir(loc):
        stmthead = 'head -n 1 {}/{}'.format(loc, f)
        stmttail = 'tail -n 1 {}/{}'.format(loc, f)
        head = subprocess.run(stmthead.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0]
        tail = subprocess.run(stmttail.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0]
        header = dateutil.parser.parse(head)
        tailer = dateutil.parser.parse(tail)
        if(header <= start and tailer >= start):
            print("Head : ", head, " Tail : ", tail, "")
            startfile = f
        if(header <= end and tailer >= end):
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