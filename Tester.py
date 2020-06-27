import time
import subprocess
import dateutil.parser
import os

def last_line(in_file, block_size=1024, ignore_ending_newline=False):
    suffix = ""
    in_file.seek(0, os.SEEK_END)
    in_file_length = in_file.tell()
    seek_offset = 0

    while(-seek_offset < in_file_length):
        # Read from end.
        seek_offset -= block_size
        if -seek_offset > in_file_length:
            # Limit if we ran out of file (can't seek backward from start).
            block_size -= -seek_offset - in_file_length
            if block_size == 0:
                break
            seek_offset = -in_file_length
        in_file.seek(seek_offset, os.SEEK_END)
        buf = in_file.read(block_size)

        # Search for line end.
        if ignore_ending_newline and seek_offset == -block_size and buf[-1] == '\n':
            buf = buf[:-1]
        pos = buf.rfind('\n')
        if pos != -1:
            # Found line end.
            return buf[pos+1:] + suffix

        suffix = buf + suffix

    # One-line file.
    return suffix


start = time.perf_counter()
# Function
for f in os.listdir('logs'):
    stmthead = 'head -n 1 logs/{}'.format(f)
    stmttail = 'tail -n 1 logs/{}'.format(f)
    head = subprocess.run(stmthead.split(), stdout=subprocess.PIPE).stdout.decode(
        'utf-8').split()[0]
    tail = subprocess.run(stmttail.split(), stdout=subprocess.PIPE).stdout.decode(
        'utf-8').split()[0]
    print("Head : ", head, " Tail : ", tail)

print("Time elapsed for open() : ", time.perf_counter() - start)

start = time.perf_counter()
for f in os.listdir('logs'):
    with open('logs/'+f, 'rb') as file:
        print(last_line(file).split[0])
print("Time elapsed for custom func() : ", time.perf_counter() - start)

